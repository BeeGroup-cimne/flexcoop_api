from ast import literal_eval
import math
from datetime import datetime

import flask
import pandas as pd
from bson import ObjectId
from eve.auth import requires_auth
from eve_swagger import add_documentation
from flask import Blueprint, current_app as app, request
import simplejson as json
from modules.timeseries.timeseries import pre_timeseries_get_callback

flexcoop_blueprints = Blueprint('1', __name__)
@flexcoop_blueprints.route('/aggregate/<collection>/<resolution>', methods=['GET'])
@requires_auth('aggregate')
def aggregate_collection(collection, resolution):
    try:
        page_param = app.config['QUERY_PAGE']
        try:
            page = int(request.args[page_param])
        except:
            page = 1

        max_results = app.config['PAGINATION_DEFAULT']
        if app.config['QUERY_MAX_RESULTS'] in request.args:
            max_results = min(int(request.args[app.config['QUERY_MAX_RESULTS']]), app.config['PAGINATION_LIMIT'])

        page_ini = (page - 1) * max_results
        page_end = page * max_results

        try:
            where_param = literal_eval(request.args['where'])
        except SyntaxError as e:
            flask.abort(422, 'error!incorrect where query: {}'.format(e))
        except Exception as e:
            print(e)
            where_param = {}

        try:
            sort_param = literal_eval(request.args['sort'])
        except SyntaxError as e:
            flask.abort(422, 'error!incorrect sort param: {}'.format(e))
        except Exception as e:
            sort_param = None

        try:
            aggregate_field = request.args['aggregate']
        except SyntaxError as e:
            flask.abort(422, 'error!incorrect sort param: {}'.format(e))
        except Exception as e:
            aggregate_field = None


        pre_timeseries_get_callback(request, where_param)
        schema = app.config['DOMAIN'][collection]
        timestamp_field = schema['aggregation']['index_field']
        for k, v in where_param.items():
            if k == timestamp_field:
                if isinstance(v, dict):
                    for k1, v1 in v.items():
                        where_param[k][k1] = datetime.strptime(v1, app.config['DATE_FORMAT'])
                else:
                    where_param[k] = datetime.strptime(v, app.config['DATE_FORMAT'])

        data = app.data.driver.db[collection].find(where_param)
        if sort_param:
            data = data.sort(sort_param)

        df = pd.DataFrame.from_records(data)

        if df.empty:
            hateoas = {
                "_meta": {
                    app.config['QUERY_MAX_RESULTS']: max_results,
                    "total": 0,
                    "page": page,
                    "max_page": 1
                },
                "_links": {
                    "self": {"href": request.url, "title": "aggregate"},
                    "parent": {"href": "/", "title": "home"},
                },
                "_items": []
            }
            return json.dumps(
                hateoas,
                cls=app.data.json_encoder_class,
                ignore_nan=True
            )

        if aggregate_field or schema['aggregation']['groupby']:
            if aggregate_field:
                grouped = df.groupby(schema['aggregation']['groupby'])
            elif schema['aggregation']['groupby']:
                grouped = df.groupby(schema['aggregation']['groupby'])
            groups_df = []
            for g, d in grouped:
                groups_df.append(aggregate_timeseries(d, resolution, schema))
            df = pd.concat(groups_df)
        else:
            df = aggregate_timeseries(df, resolution, schema)

        total_len = len(df)
        if total_len > max_results:
            parameter_character = '?'
            query_url = request.base_url
            for key, value in request.args.items():
                if key != page_param:
                    query_url += "{}{}={}".format(parameter_character,key,value)
                    parameter_character = '&'

            items = df.iloc[page_ini:page_end]
            max_page = math.ceil(total_len / max_results)
            if page + 1 < max_page:
                next_url = "{}{}{}={}".format(query_url,parameter_character, page_param, page + 1)
            else:
                next_url = None
            last_url = "{}{}{}={}".format(query_url,parameter_character,page_param, max_page)
        else:
            items = df
            next_url = None
            max_page = 1
            last_url = None

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

        return json.dumps(
            hateoas,
            cls=app.data.json_encoder_class,
            ignore_nan=True
        ), 200, {'Content-Type': 'text/json; charset=utf-8'}
    except ValueError as e:
        flask.abort(422, 'Unexpected error: {}'.format(e))
    except Exception as e:
        flask.abort(500, e)



def aggregate_timeseries(df, resolution, schema):
    timestamp_field = schema['aggregation']['index_field']
    df = df.set_index(timestamp_field)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    aggregated_index = df.resample(resolution).mean().index
    df_aggregated = None

    for field, operation in schema['aggregation']['aggregate_fields'].items():
        if field not in df.columns:
            continue
        if operation == "AVG":
            series = df[field].resample(resolution).mean()
        if operation == "SUM":
            series = df[field].resample(resolution).sum()
        if df_aggregated is None:
            df_aggregated = pd.DataFrame(data={field: series}, index=aggregated_index)
        else:
            df_aggregated[field] = series

    for field in schema['aggregation']['add_fields']:
        df_aggregated[field] = [df[field][0]] * len(df_aggregated)

    df_aggregated[timestamp_field] = df_aggregated.index.strftime(app.config['DATE_FORMAT'])
    df_aggregated = df_aggregated.reset_index(drop=True)
    return df_aggregated

def set_documentation():
    add_documentation(
        {
            'paths': {
                "/aggregate/{collection}/{resolution}": {
                    "get": {
                        "parameters": [
                            {"name": "collection", "in": "path", "type": "string", "required": "true", "description": "a timeseries collection"},
                            {"name": "resolution", "in": "path", "type": "string", "required": "true",
                             "description": "the frequency to aggregate values"},
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
@requires_auth('notify')
def oadr_notification_new_devices(report):
    if hasattr(request, 'account_id') and request.account_id == 'cimne_client':
        items = list(app.data.driver.db['devices'].find({"report": ObjectId(report)}))
        getattr(app, 'on_inserted_devices')(items)
    return jsonify({"notification": "OK"})

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