import flask
import threading
import requests
import json
import datetime
from flexcoop_utils import ServiceToken
from settings import INTERCOMPONENT_SETTINGS, CLIENT_OAUTH
from requests.exceptions import ConnectionError

inter_component_message_event = threading.Event()


def inter_component_message_worker_thread(app):
    """
        A worker thread that processes the list of interComponentMessage database entries.

        At startup the not-yet delivered or delivered-with-failure entries will be listed
        and then the daemonic thread enters an loop:
            - Newly added messages will be tried to deliver first
            - Then undelivered messages, not older than a day and not tried for more than 5 minutes
              are tried to deliver
            - After this, the thread sleeps for two minutes or until woken up by adding a new message

        In each delivery attempt, either the full interComponentMessage or only the payload is posted
        to the recipient and then acted upon the result:
         - with http status 201-203, the message was transmitted succesfully and therefore deleted from the db
         - with http status 502,503,504 there was a network problem. The error is logged and the message will be retried
         - with another http status, there was a problem with the message itself - an error is logged, and the message
             status updated to the received error. The message wil not be re-transmitted.
         - with connection error, the error is logged and the message will be retried
    """

    def cleanup_message(msg_raw, clean_internal):
        msg = msg_raw.copy()
        for key in msg_raw.keys():
            if key[0] == '_':
                del msg[key]
            if clean_internal and 'delivery_' in key:
                del msg[key]
        return msg

    def datetime_serializer(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            raise TypeError("Type %s not serializable" % type(obj))

    def dump_initial_messages():
        max_age = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        query1 = {"delivery_failure_response": {"$exists": True, "$eq": 100}, "delivery_attempt_time": {"$gte": max_age}}
        outstanding = flask.current_app.data.driver.db['interComponentMessage'].find(query1)
        if outstanding.count() > 0:
            print('| There are ', outstanding.count(), ' interComponentMessage(s) still to be delivered')
            for msg_raw in outstanding:
                msg = cleanup_message(msg_raw, False)
                print('|  ', json.dumps(msg, default=datetime_serializer))

        query2 = {"delivery_failure_response": {"$exists": True, "$ne": 100, "$ne": 200}}
        errors = flask.current_app.data.driver.db['interComponentMessage'].find(query2)
        if errors.count() > 0:
            print('| There are ', errors.count(), ' rejected interComponentMessage(s) ')
            for msg_raw in errors:
                msg = cleanup_message(msg_raw, False)
                print('|  ', json.dumps(msg, default=datetime_serializer))
                # flask.current_app.data.driver.db['interComponentMessage'].delete_one({'_id': msg_raw['_id']})

    def message_delivery_attempt(msg_raw):
        msg = cleanup_message(msg_raw, True)
        date_now = datetime.datetime.utcnow().replace(microsecond=0)
        recipient = msg['recipient_id']

        failure = True
        failure_response = 500
        failure_message = 'undefined internal error'

        if recipient not in INTERCOMPONENT_SETTINGS:
            failure = True
            failure_response = 421
            failure_message = 'Unknown receiver ' + recipient
        else:
            url = INTERCOMPONENT_SETTINGS[recipient]['message_url']

            token = ServiceToken().get_token()
            headers = {'accept': 'application/json', 'Authorization': token, "Content-Type": "application/json"}
            try:
                json_string = json.dumps(msg, default=datetime_serializer)
                response = requests.post(url, headers=headers, data=json_string)
                status_code = response.status_code
                if status_code < 200 or status_code > 203:
                    failure = True
                    failure_response = status_code
                    failure_message = 'POST ICM to ' + recipient + ' for ' \
                                      + msg['notification_id'] + ' / ' + msg['message_type'] + ' failed. ' \
                                      + '  http_status=' + str(response.status_code) \
                                      + '  http_response='+ str(response.text)[:1024]
                else:
                    failure = False

            except ConnectionError as e:
                failure_response = 100
                failure_message = 'Connection error contacting ' + recipient + ' for ' \
                                  + msg['notification_id'] + ' / ' + msg['message_type']
                # Keep the message active

        if failure:
            log_inter_component_message_error('ICM Worker: ' + failure_message)
            update = {'$set': {'delivery_attempt_time': date_now,
                               'delivery_failure_response': failure_response,
                               'delivery_failure_message': failure_message}}
            flask.current_app.data.driver.db['interComponentMessage'].update_one({'_id': event['_id']}, update)
        # Todo: Remove temporary Sprint4 variant that keeps the ICM message in the DB
        else:
            update = {'$set': {'delivery_attempt_time': date_now,
                               'delivery_failure_response': 200,
                               'delivery_failure_message': 'OKAY'}}
            flask.current_app.data.driver.db['interComponentMessage'].update_one({'_id': event['_id']}, update)
        # else:
        #    flask.current_app.data.driver.db['interComponentMessage'].delete_one({'_id': event['_id']})

    with app.app_context():
        dump_initial_messages()
        while True:
            inter_component_message_event.clear()

            # Find new messages
            where = {"delivery_attempt_time": {"$exists": False}}
            events = app.data.driver.db['interComponentMessage'].find(where)
            for event in events:
                message_delivery_attempt(event)

            five_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
            one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)

            # Find undelivered messages
            where = {"delivery_failure_response": {"$exists": True, "$eq": 100},
                     "delivery_attempt_time": {"$exists": True, "$lte": five_minutes_ago, "$gte": one_day_ago}}
            events = app.data.driver.db['interComponentMessage'].find(where)
            for event in events:
                message_delivery_attempt(event)

            inter_component_message_event.wait(60)


def log_inter_component_message_error(info):
    date_now = datetime.datetime.utcnow().replace(microsecond=0)
    print(date_now.strftime("%d.%b %Y %H:%M:%S") + '  ' + info);


def find_service_for_recipient(account_id):
    for key in INTERCOMPONENT_SETTINGS:
        if 'account_id' in INTERCOMPONENT_SETTINGS[key] and account_id == INTERCOMPONENT_SETTINGS[key]['account_id']:
            return key
    return 'unknown'


def pre_inter_component_message_GET_callback(request, lookup):
    if request.role == 'admin':
        pass
    else:
        log_inter_component_message_error(' ICM pre GET : not allowed for '+request.role)
        flask.abort(403, 'wrong role')


def pre_inter_component_message_POST_callback(request):
    # Todo: Remove temporary Sprint4 check to allow admin POST
    if request.role == 'admin':
        pass

    elif request.role != 'service':
        log_inter_component_message_error(' ICM pre POST : not allowed for '+request.role)
        flask.abort(403, 'wrong role')

    if 'recipient_id' in request.json and request.json['recipient_id'] not in INTERCOMPONENT_SETTINGS:
        log_inter_component_message_error(' ICM pre POST : unknown recipient '+request.json['recipient_id'])
        flask.abort(406, 'unknown recipient')

    if 'notification_id' in request.json:
        id_check = {"notification_id": {"$eq": request.json['notification_id']}}
        cursor = flask.current_app.data.driver.db['interComponentMessage'].find(id_check)
        if cursor.count() > 0:
            log_inter_component_message_error(' ICM pre POST : notification_id already exists')
            flask.abort(409, 'notification_id already exists')


def pre_inter_component_message_DELETE_callback(request, lookup):
    if request.role == 'admin':
        pass
    else:
        log_inter_component_message_error(' ICM pre DELETE : not allowed for '+request.role)
        flask.abort(403)


def post_inter_component_message_INSERTED_callback(items):
    inter_component_message_event.set()


def set_hooks(app):
    app.on_pre_GET_interComponentMessage += pre_inter_component_message_GET_callback
    app.on_pre_POST_interComponentMessage += pre_inter_component_message_POST_callback
    app.on_pre_DELETE_interComponentMessage += pre_inter_component_message_DELETE_callback
    app.on_inserted_interComponentMessage += post_inter_component_message_INSERTED_callback

    log_inter_component_message_error('Starting worker thread: interComponentMessage')
    tp_thread = threading.Thread(target= inter_component_message_worker_thread, args=(app,), daemon=True)
    tp_thread.start()
