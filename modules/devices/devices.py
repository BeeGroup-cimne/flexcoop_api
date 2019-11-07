import uuid

import flask
import requests
from flask import current_app
from datetime import datetime

from flexcoop_utils import get_middleware_token

def pre_devices_access_control_callback(request, lookup):
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


def on_update_devices_callback(updates, original):
    # Only allow the modification of non OSB fields
    allowed_fields = ['availability', 'location', 'device_type', 'max_capacity', 'available_capacity', 'cluster_id', 'cluster_type', 'vpp_id']
    for field in updates:
        if field not in allowed_fields:
            if updates[field] != original[field]:
                flask.abort(403, "The modification of the field {} is not allowed".format(field))


def on_insterted_devices_callback(items):
    ldm_collection = current_app.data.driver.db['local_demand_manager']
    devices_collection = current_app.data.driver.db['devices']
    item = items[0] if len(items) > 0 else None
    if item:
        account_id = item['account_id']
        aggregator_id = item['aggregator_id']
    else:
        return
    # To get all the identifiers of existing devices for that user
    devices = [x['device_id'] for x in devices_collection.find({"account_id": account_id})]

    ldem = ldm_collection.find_one({"account_id": account_id})
    if not ldem:
        ldm_collection.insert_one({
            'ldem_id': str(uuid.uuid1()),
            'account_id': account_id,
            'aggregator_id': aggregator_id,
            'creation_date': datetime.now(),
            'timestamp': None,
            'ders': devices
        })
    else:
        ldem['ders'] = devices
        ldm_collection.update({'ldem_id': ldem['ldem_id']}, {"$set": ldem})


def set_hooks(app):
    app.on_pre_GET_devices += pre_devices_access_control_callback
    app.on_pre_PATCH_devices += pre_devices_access_control_callback
    app.on_inserted_devices += on_insterted_devices_callback
    app.on_update_devices += on_update_devices_callback

