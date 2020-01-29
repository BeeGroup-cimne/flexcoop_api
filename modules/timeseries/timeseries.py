import json
import uuid

import flask
import requests
from flask import current_app, request
from datetime import datetime

from flexcoop_utils import get_middleware_token
from settings import NOTIFICATION_OPENADR_URL, NOTIFICATION_OPENADR_CERT


def pre_timeseries_get_callback(request, lookup=None):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        lookup["account_id"] = account_id

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

    elif role == 'service':
        pass
    else:
        flask.abort(403, "Unknown user role")





def set_hooks(app):
    app.on_pre_GET_indoor_sensing += pre_timeseries_get_callback
    app.on_pre_GET_meter += pre_timeseries_get_callback
    app.on_pre_GET_occupancy += pre_timeseries_get_callback
