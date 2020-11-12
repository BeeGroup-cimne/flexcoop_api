import urllib.parse as urlparse
from urllib.parse import parse_qs
import uuid
import flask

from flask import current_app
from datetime import datetime


def pre_access_control_callback(request, lookup=None):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        lookup["account_id"] = account_id
    elif role == 'aggregator':
        pass
    elif role == 'service':
        pass
    elif role == 'admin':
        pass
    else:
        flask.abort(403, "Unknown user role")

def set_hooks(app):
    app.on_pre_GET_comfortProfiles += pre_access_control_callback
    app.on_pre_PATCH_comfortProfiles += pre_access_control_callback
    app.on_pre_GET_thermalComfortLevels += pre_access_control_callback
    app.on_pre_PATCH_thermalComfortLevels += pre_access_control_callback
