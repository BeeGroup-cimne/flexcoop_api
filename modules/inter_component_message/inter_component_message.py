import flask
import threading
import requests
import json
import datetime
from flexcoop_utils import ServiceToken
from settings import INTERCOMPONENT_SETTINGS

inter_component_message_event = threading.Event()


def inter_component_message_worker_thread(app):

    def cleanup_message(msg_raw):
        msg = msg_raw.copy()
        for key in msg_raw.keys():
            if key[0] == '_' or key == 'message_response' or key == 'delivery_attempt_time':
                del msg[key]
        return msg

    def datetime_serializer(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.replace(tzinfo=None).isoformat(timespec='milliseconds')+'Z'
        else:
            raise TypeError("Type %s not serializable" % type(obj))

    def dump_initial_messages():
        max_age = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        query = {"message_response": {"$eq": 100}, "delivery_attempt_time": {"$gte": max_age}}
        outstanding = flask.current_app.data.driver.db['interComponentMessage'].find(query)
        if outstanding.count() > 0:
            print('There are ', outstanding.count(), ' interComponentMessage(s) still to be delivered')
            for msg_raw in outstanding:
                msg = cleanup_message(msg_raw)
                print('  ', json.dumps(msg, default=datetime_serializer))

        errors = flask.current_app.data.driver.db['interComponentMessage'].find({"message_response": {"$ne": 100}})
        if errors.count() > 0:
            print('There are ', errors.count(), ' undeliverable interComponentMessage(s) ')
            for msg_raw in errors:
                msg = cleanup_message(msg_raw)
                print('  ', json.dumps(msg, default=datetime_serializer))
                # flask.current_app.data.driver.db['interComponentMessage'].delete_one({'_id': msg_raw['_id']})

    def message_delivery_attempt(msg_raw):
        msg = cleanup_message(msg_raw)
        date_now = datetime.datetime.utcnow().replace(microsecond=0)
        receiver = msg['recipient_id']
        status_code = 100
        if receiver in INTERCOMPONENT_SETTINGS:
            token = ServiceToken().get_token()
            headers = {'accept': 'application/xml', 'Authorization': token, "Content-Type": "application/json"}
            try:
                if INTERCOMPONENT_SETTINGS[receiver]['payload_only']:
                    json_string = json.dumps(msg['payload'], default=datetime_serializer)
                else:
                    json_string = json.dumps(msg, default=datetime_serializer)

                response = requests.post(INTERCOMPONENT_SETTINGS[receiver]['message_url'], headers=headers, data=json_string)
                status_code = response.status_code
                if status_code < 200 or status_code > 203:
                    print(date_now.strftime("%d.%b %Y %H:%M:%S"),
                          ' ICM Worker:  Got ', response.status_code,
                          ' from ', receiver, '@', INTERCOMPONENT_SETTINGS[receiver]['message_url'],
                          ' for ', msg['message_type'], '/', event['_id'],' ERROR:',response.content)
            except Exception as e:  # todo catch only corresponding exceptions here
                print(date_now.strftime("%d.%b %Y %H:%M:%S"),
                      ' ICM Worker:  Connection error to ', receiver, '@', INTERCOMPONENT_SETTINGS[receiver]['message_url'],
                      ' for ', msg['message_type'], '/', event['_id'], ' ERROR:', e)
        else:
            print(date_now.strftime("%d.%b %Y %H:%M:%S"),
                  ' ICM Worker: Unknown receiver ', receiver, '@', INTERCOMPONENT_SETTINGS[receiver]['message_url'],
                  'for ', msg['message_type'], '/', msg_raw['_id'])
            status_code = 421

        if 200 <= status_code <= 202:
            flask.current_app.data.driver.db['interComponentMessage'].delete_one({'_id': msg_raw['_id']})
        else:
            update = {'$set': {'delivery_attempt_time': date_now, 'message_response': status_code}}
            flask.current_app.data.driver.db['interComponentMessage'].update_one({'_id': msg_raw['_id']}, update)

    with app.app_context():
        dump_initial_messages()
        while True:
            inter_component_message_event.clear()

            # Find new messages
            where = {"message_response": {"$eq": 100}, "delivery_attempt_time": {"$exists": False}}
            events = app.data.driver.db['interComponentMessage'].find(where)
            for event in events:
                message_delivery_attempt(event)

            five_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
            one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)

            # Find undelivered messages
            where = {"message_response": {"$eq": 100},
                      "delivery_attempt_time": {"$lte": five_minutes_ago, "$gte": one_day_ago}}
            events = app.data.driver.db['interComponentMessage'].find(where)
            for event in events:
                message_delivery_attempt(event)

            inter_component_message_event.wait(120)


def pre_inter_component_message_GET_callback(request, lookup):
    if request.role == 'service':
        pass
    elif request.role == 'aggregator':
        pass
    else:
        print('error: GET interComponentMessage not allowed for ', request.role)
        flask.abort(403)


def pre_inter_component_message_POST_callback(request):
    if request.role == 'service':
        pass
    else:
        print('error: POST interComponentMessage not allowed for ', request.role)
        flask.abort(403)


def post_inter_component_message_INSERTED_callback(items):
    inter_component_message_event.set()


def set_hooks(app):
    app.on_pre_GET_interComponentMessage += pre_inter_component_message_GET_callback
    app.on_pre_POST_interComponentMessage += pre_inter_component_message_POST_callback
    app.on_inserted_interComponentMessage += post_inter_component_message_INSERTED_callback

    print("Starting worker thread: interComponentMessage")
    tp_thread = threading.Thread(target= inter_component_message_worker_thread, args=(app,), daemon=True)
    tp_thread.start()
