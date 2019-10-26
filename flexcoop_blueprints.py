import math

import flask
import pandas as pd
from bson import ObjectId
from eve_swagger import add_documentation
from flask import Blueprint, current_app as app, jsonify, request

from settings import NOTIFICATION_OPENADR

flexcoop_blueprints = Blueprint('1', __name__)

@flexcoop_blueprints.route('/aggregate/<collection>/<resolution>/<operation>', methods=['GET'])
def aggregate_collection(collection, resolution, operation):
    max_results = app.config['PAGINATION_DEFAULT']
    if app.config['QUERY_MAX_RESULTS'] in request.args:
        max_results = min(request.args[app.config['QUERY_MAX_RESULTS']], app.config['PAGINATION_LIMIT'])

    page = 1
    if app.config['QUERY_PAGE'] in request.args:
        page = int(request.args[app.config['QUERY_PAGE']])

    page_ini = (page - 1) * max_results
    page_end = page * max_results


    current_url = request.url
    base_url = current_url.split("?")[0]

    schema = app.config['DOMAIN'][collection]
    data = app.data.driver.db[collection].find({})
    df = pd.DataFrame.from_records(data)
    df = df.set_index(schema['aggregation']['index_field'])
    df.index = pd.to_datetime(df.index)
    if operation == "AVG":
        df = df.resample(resolution).mean()
    if operation == "SUM":
        df = df.resample(resolution).sum()
    df['ts'] = df.index.strftime(app.config['DATE_FORMAT'])

    total_len = len(df)
    if total_len > max_results:
        items = df.iloc[page_ini:page_end]
        next_url = "{}?page={}".format(base_url, page + 1)
        max_page = math.ceil(total_len/max_results)
        last_url = "{}?page={}".format(base_url, max_page)
    else:
        items = df
        next_url = None
        max_page = 1
        last_url = None

    items = items.sort_index()
    hateoas = {
        "_meta": {
            app.config['QUERY_MAX_RESULTS']: max_results,
            "total": total_len,
            "page": page,
            "max_page": max_page
        },
        "_links": {
            "self": {"href": request.url, "title": "aggregate"},
            "parent": {"href": "/", "title": "home"},
        },
        "_items": items.to_dict(orient="records")
    }
    if next_url:
        hateoas['_links']['next'] = {"href": next_url, "title": "next page"}
    if last_url:
        hateoas['_links']['last'] = {"href": last_url, "title": "last page"}

    return jsonify(hateoas)




def set_documentation():
    add_documentation(
        {
            'paths': {
                "/aggregate/{collection}/{resolution}/{operation}": {
                    "get": {
                        "parameters": [
                            {"name": "collection", "in": "path", "type": "string", "required": "true", "description": "a timeseries collection"},
                            {"name": "resolution", "in": "path", "type": "string", "required": "true",
                             "description": "the frequency to aggregate values"},
                            {"name": "operation", "in": "path", "type": "string", "required": "true",
                             "description": "operation when aggregating"},
                            {"name": "page", "in": "query", "type": "integer",
                             "description": "page of data"},
                        ],
                        "responses":{
                            "200": {"description": "OK"}
                        }
                        # ],
                        # "security": [
                        #     {"JWTAuth": []}
                        # ]
                    }
                }
            }
        }
    )

@flexcoop_blueprints.route('/notify/der_installed/<report>', methods=['GET'])
def oadr_notification_new_devices(report):
    if request.remote_addr != NOTIFICATION_OPENADR:
        flask.abort(403)
    items = list(app.data.driver.db['devices'].find({"report":ObjectId(report)}))
    getattr(app, 'on_insert_devices')(items)
    return jsonify({"notification": str(request.environ)})

    # def post_get_callback(resource_name, response):
    #     if 'aggregate' in request.args:
    #         try:
    #             params = json.loads(request.args['aggregate'])
    #         except:
    #             return
    #         try:
    #             definition = app.config['DOMAIN'][resource_name]['aggregation']
    #         except:
    #             return
    #         df = pd.DataFrame.from_records(response["_items"])
    #         df = df.set_index(definition['index_field'])
    #         df.index = pd.to_datetime(df.index)
    #         if params[1] == "AVG":
    #             df = df.resample(params[0]).mean()
    #         if params[1] == "SUM":
    #             df = df.resample(params[0]).sum()
    #         df['ts'] = df.index
    #         response["_items"] = df.to_dict(orient="records")
    #
    #
    # app.on_fetched_resource += post_get_callback