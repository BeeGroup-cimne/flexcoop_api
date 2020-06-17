import uuid

import flask
import requests
from flask import current_app

from flexcoop_utils import ServiceToken

cert = False #"/path/to/cert"

def pre_btp_request_access_control_callback(request, lookup=None):
    account_id = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id
    if role == 'prosumer':
        flask.abort(403, "Prosumer can't have access to BTP Request")

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

    elif role == 'service':
        if account_id not in ['GDEM']:
            flask.abort(403, "The component {} can't have access to BTP Request".format(account_id))
    else:
        flask.abort(403, "Unknown user role")


def on_deleted_btp_request_callback(item):
    bid_message_collection = current_app.data.driver.db['btp_message']
    bid_collection = current_app.data.driver.db['btp_bid']
    bid_line_collection = current_app.data.driver.db['btp_bid_line']
    if item:
        btp_messageId = item['btp_requestId']
    else:
        return
    bid_message_collection.delete_many({"btp_messageId" :  btp_requestId})
    bid_collection.delete_many({"btp_messageId" :  btp_requestId})
    bid_line_collection.delete_many({"btp_messageId" :  btp_requestId})


def set_hooks(app):
    app.on_pre_GET_btp_request += pre_btp_request_access_control_callback    
    app.on_pre_DELETE_btp_request += pre_btp_request_access_control_callback    
    app.on_pre_POST_btp_request += pre_btp_request_access_control_callback    
    app.on_delete_item_btp_request += on_deleted_btp_request_callback
