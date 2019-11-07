import uuid

import flask
import requests
from flask import current_app
from datetime import datetime

from flexcoop_utils import get_middleware_token

def pre_local_access_control_callback(request, lookup):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        flask.abort(403, "Prosumer can't have access to Local Demand Manager")

    elif role == 'aggregator':
        flask.abort(403, "Prosumer can't have access to Local Demand Manager")

    elif role == 'service':
        if account_id not in ['LDEM', 'GDEM']:
            flask.abort(403, "The component {} can't have access to Local Demand Manager".format(account_id))
    else:
        flask.abort(403, "Unknown user role")



def set_hooks(app):
    app.on_pre_GET_local_demand_manager += pre_local_access_control_callback
    app.on_pre_PATCH_local_demand_manager += pre_local_access_control_callback
    app.on_pre_PUT_local_demand_manager += pre_local_access_control_callback
    app.on_pre_DELETE_local_demand_manager += pre_local_access_control_callback
    app.on_pre_POST_local_demand_manager += pre_local_access_control_callback

