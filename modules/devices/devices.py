import uuid

import flask
import requests
from flask import current_app
from datetime import datetime

from flexcoop_utils import get_middleware_token

url = "https://<url>/gdem/newLDEM/{idLDEM}"
cert = False #"/path/to/cert"

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
    print(items)
    return
    #TODO: Correct this hook
    ldm_collection = current_app.data.driver.db['local_demand_manager']
    devices_collection = current_app.data.driver.db['devices']
    item = items[0] if len(items) > 0 else None
    if item:
        account_id = item['account_id']
        aggregator_id = item['aggregator_id']
    else:
        return

    devices = [x['device_id'] for x in devices_collection.find({"account_id": account_id})]

    ldem = ldm_collection.find_one({"account_id": account_id})
    if not ldem:
        # If a new OSB is being registered, a new LDEM has to be instantiated containing all the DERs controlled by it
        idLDEM = str(uuid.uuid1())
        headers = {"Authentication": get_middleware_token()}
        resp = requests.get(url.format(idLDEM), headers=headers, verify=cert)
        if not resp.ok:
            # considere not aborting the request.
            flask.abort(403, "It has been not possible to register a new LDEM on the GDEM")
        else:
            ldm_collection.insert_one({
                'ldem_id': idLDEM,
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