import urllib.parse as urlparse
from urllib.parse import parse_qs
import uuid
import flask

from flask import current_app
from datetime import datetime


def pre_datapoints_access_control_callback(request, lookup=None):
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


def translate_device_output(response):
    items = response['_items']
    for index, item in enumerate(items):
        db_item = current_app.data.driver.db['data_points'].find_one({"device_id": item['device_id']})
        item['device_class'] = db_item['rid']
        item['ven_id'] = current_app.data.driver.db['virtual_end_node'].find_one({"account_id": item["account_id"]})['ven_id']
        name_map = current_app.data.driver.db['map_device_name'].find_one({"device_id": item['device_id']})
        if name_map and 'device_name' in name_map:
            item['device_name'] = name_map['device_name']
        else:
            item['device_name'] = db_item['rid'] + str(index)
        item['reporting_metrics'] = []
        for k, v in db_item['reporting_items'].items():
            item['reporting_metrics'].append(k)



def set_hooks(app):
    app.on_pre_GET_data_points += pre_datapoints_access_control_callback
    app.on_fetched_resource_data_points += translate_device_output

