import uuid

import flask
import requests
from flask import current_app

from flexcoop_utils import get_middleware_token

cert = False #"/path/to/cert"

def pre_dr_campaign_access_control_callback(request, lookup):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        flask.abort(403, "Prosumer can't have access to DR Campaign")

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

    elif role == 'service':
        if account_id not in ['GDEM', 'DRSR']:
            flask.abort(403, "The component {} can't have access to DR Campaign".format(account_id))
    else:
        flask.abort(403, "Unknown user role")

def on_deleted_dr_campaign_callback(item):
    timeline_collection = current_app.data.driver.db['dr_campaign_timeline']
	baseline_collection = current_app.data.driver.db['dr_campaign_baseline']
	ldem_dr_event_collection = current_app.data.driver.db['dr_event_ldem_request']
	ldem_baseline_collection = current_app.data.driver.db['dr_event_ldem_baseline']
	#strategy_collection = current_app.data.driver.db['dr_campaign_strategy']
    if item:
        dr_campaign_id = item['dr_campaign_id']
    else:
        return
    timeline_collection.delete_many({"dr_campaign_id" :  dr_campaign_id})
	baseline_collection.delete_many({"dr_campaign_id" :  dr_campaign_id})
	ldem_dr_event_collection.delete_many({"dr_campaign_id" :  dr_campaign_id})
	ldem_baseline_collection.delete_many({"dr_campaign_id" :  dr_campaign_id})
	#strategy_collection.delete_many({"dr_campaign_id" :  dr_campaign_id})
		
def set_hooks(app):
    app.on_pre_GET_dr_campaign += pre_dr_campaign_access_control_callback    
    app.on_pre_DELETE_dr_campaign += pre_dr_campaign_access_control_callback
    app.on_pre_POST_dr_campaign += pre_dr_campaign_access_control_callback
    app.on_delete_item_dr_campaign += on_deleted_dr_campaign_callback