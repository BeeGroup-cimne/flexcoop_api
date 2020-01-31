import uuid

import flask
import requests
from flask import current_app

from flexcoop_utils import get_middleware_token

cert = False #"/path/to/cert"

def pre_control_signal_access_control_callback(request, lookup=None):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        flask.abort(403, "Prosumer can't have access to Control Signals")

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

    elif role == 'service':
        if account_id not in ['LDEM', 'DFP']:
            flask.abort(403, "The component {} can't have access to Control Signals".format(account_id))
    else:
        flask.abort(403, "Unknown user role")

def set_hooks(app):
    app.on_pre_GET_control_signal += pre_control_signal_access_control_callback    
    app.on_pre_DELETE_control_signal += pre_control_signal_access_control_callback