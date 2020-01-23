import uuid

import flask
import requests
from flask import current_app

from flexcoop_utils import get_middleware_token

cert = False #"/path/to/cert"

def pre_dr_event_ldem_request_access_control_callback(request, lookup):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        flask.abort(403, "Prosumer can't have access to DR event LDEM request")

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

    elif role == 'service':
        if account_id not in ['GDEM', 'DRSR', 'LDEM']:
            flask.abort(403, "The component {} can't have access to DR event LDEM request".format(account_id))
    else:
        flask.abort(403, "Unknown user role")

def set_hooks(app):
    app.on_pre_GET_dr_event_ldem_request += pre_dr_event_ldem_request_access_control_callback    
    app.on_pre_DELETE_dr_event_ldem_request += pre_dr_event_ldem_request_access_control_callback