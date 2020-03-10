import json
import uuid

import flask
import requests
from flask import current_app, request
from datetime import datetime

from flexcoop_utils import ServiceToken
from settings import NOTIFICATION_OPENADR_URL, NOTIFICATION_OPENADR_CERT

def on_insert_dr_events_callback(items):
    print("inserting event")
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        for item in items:
            if not item["account_id"] == account_id:
                flask.abort(403, "prosumer can't create events in other prosumers")

    elif role == 'aggregator':
        for item in items:
            if not item["aggregator_id"] == aggregator_id:
                flask.abort(403, "aggregator can't create events external prosumers")

    elif role == 'service':
        pass
    else:
        flask.abort(403, "Unknown user role")

    service_token_provider = ServiceToken()
    devices_id = list(set([x1["device_id"] for x1 in items]))
    vens = {}

    for d_id in devices_id:
        device = current_app.data.driver.db['devices'].find_one({'device_id': d_id})
        ven = current_app.data.driver.db['virtual_end_node'].find_one({"account_id": device['account_id']})
        if not ven:
            flask.abort(flask.Response(json.dumps({"error": "The ven does not exist"})))
        try:
            vens[ven['ven_id']][d_id]['events'].extend(list(filter(lambda i: i['device_id'] == d_id, items)))
        except:
            vens[ven['ven_id']]={d_id : {"device": device, "events": list(filter(lambda i: i['device_id'] == d_id, items))}}

    for ven_id, ven_events in vens.items():
        for device_id, device_events_dict in ven_events.items():
            mid = current_app.data.driver.db['map_id'].find_one({"device_id": device_id})['rid']
            status_device = device_events_dict['device']['status']
            for event in device_events_dict['events']:
                status_changes = event['status']
                for change, value in status_changes.items():
                    oadr_name = status_device[change]['oadr_name']
                    rid = "{}_{}".format(mid, oadr_name)
                    event_dict = {
                        "event_id": str(uuid.uuid1()),
                        "modification_number": "0",
                        "priority": "0",
                        "market_context": "",
                        "created_date_time": datetime.now(),
                        "event_status": "active",
                        "test_event": False,
                        "vtn_comment": "",
                        "dtstart": datetime.now(),
                        "duration": "P10Y",
                        "tolerance": "",
                        "ei_notification": "",
                        "ei_ramp_up": "",
                        "ei_recovery": "",
                        "target": rid,
                        "response_required": "never",
                        "modification_date_time": None,
                        "ven_id": ven_id,
                        "_updated_at": datetime.now(),
                        "_created_at": datetime.now()
                    }
                    current_app.data.driver.db['events'].insert_one(event_dict)
                    id = current_app.data.driver.db['events'].find_one(event_dict)['_id']
                    signal_dict = {
                        "event" : id,
                        "target" : "",
                        "signal_name" : "LOAD_CONTROL",
                        "signal_type" : "x-loadControlSetpoint",
                        "signal_id" : str(uuid.uuid1()),
                        "current_value" : "",
                        "_updated_at" : datetime.now(),
                        "_created_at" : datetime.now()
                    }
                    current_app.data.driver.db['event_signals'].insert_one(signal_dict)
                    id = current_app.data.driver.db['event_signals'].find_one(signal_dict)['_id']
                    interval_dict = {
                        "signal" : id,
                        "dtstart" : None,
                        "duration" : "",
                        "uid" : "",
                        "value" : value,
                        "_updated_at" : datetime.now(),
                        "_created_at" : datetime.now()
                    }
                    current_app.data.driver.db['event_signal_intervals'].insert_one(interval_dict)
        try:
            headers = {"Authorization": service_token_provider.get_token()}
            resp = requests.get("{}/{}/{}".format(NOTIFICATION_OPENADR_URL,"notify/events",ven_id), headers=headers, verify=NOTIFICATION_OPENADR_CERT)
            if not resp.ok:
                print("error sending the event")
                flask.abort(flask.Response(json.dumps({"error": "error sending the event"})))
        except:
            print("Notification to openADR failed")
            flask.abort(flask.Response(json.dumps({"error": "error sending the event"})))
    response = {'events_sent': len(items)}
    flask.abort(flask.Response(json.dumps(response)))



def set_hooks(app):
    app.on_insert_dr_events += on_insert_dr_events_callback


