import requests
from eve.utils import config
from settings import OAUTH_PROVIDERS, CLIENT, SECRET, CLIENT_OAUTH
from flask import current_app

def filter_field(data, schema):
    fitem = {}
    if schema['type'] == "dict" and "schema" in schema:
        for k, v in schema['schema'].items():
            if k in data:
                fitem[k] = filter_field(data[k], v)
    else:
        fitem = data
    return fitem


def filter_item_schema(resource_name, response):
    schema = config.DOMAIN[resource_name]['schema']
    for k, v in schema.items():
        if k in response:
            response[k] = filter_field(response[k], schema[k])
    for k, v in response.items():
        if k not in schema:
            response[k] = response[k]

    print(response)

def filter_internal_schema(resource_name, response):
    filtered_items = []
    schema = config.DOMAIN[resource_name]['schema']
    for x in response["_items"]:
        f_item = {}
        for k, v in schema.items():
            if k in x:
                f_item[k] = filter_field(x[k], schema[k])
        for k, v in x.items():
            if k not in schema:
                f_item[k] = x[k]

        filtered_items.append(f_item)
    response["_items"] = filtered_items


def get_middleware_token():
    client = CLIENT
    secret = SECRET
    login = {'grant_type': 'client_credentials', 'client_id': client, 'client_secret': secret}
    response = requests.post("{}/token".format(OAUTH_PROVIDERS[CLIENT_OAUTH]['url']), data=login, verify=OAUTH_PROVIDERS[CLIENT_OAUTH]['cert'])
    if response.ok:
        return response.json()['access_token']
    else:
        raise Exception("Oauth client not found")