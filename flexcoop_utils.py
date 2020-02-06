import requests
from eve.utils import config
from settings import OAUTH_PROVIDERS, CLIENT, SECRET, CLIENT_OAUTH
from jwt import JWT
from auth.authentication import KeyCache
from datetime import datetime, timedelta

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


class ServiceToken(object):
    class _ServiceToken(object):
        def __init__(self):
            self.token = None
            self.exp = None
            self.token_url = None
            self.client = CLIENT
            self.secret = SECRET
            self.oauth = OAUTH_PROVIDERS[CLIENT_OAUTH]['url']
            self.cert = OAUTH_PROVIDERS[CLIENT_OAUTH]['cert']

        def __str__(self):
            return repr(self)

        def get_token(self):
            def get_exp(token):
                jwt = JWT()
                keys_cache = KeyCache(OAUTH_PROVIDERS, timedelta(minutes=10))
                keys = keys_cache.get_keys()
                for key in keys:
                    try:
                        user_info = jwt.decode(token, key['key'])
                        return datetime.utcfromtimestamp(user_info['exp'])

                    except Exception as e:  # todo catch only corresponding exceptions here
                        pass
                return None

            if self.token and self.exp:
                in_five_minutes = datetime.utcnow() + timedelta(minutes=5)
                if self.exp > in_five_minutes:
                    return self.token
            self.token = None
            self.exp = None

            if self.token_url is None:
                response = requests.get("{}/.well-known/openid-configuration/".format(self.oauth), verify=self.cert)
                if response.ok:
                    self.token_url = response.json()['token_endpoint']
                else:
                    raise Exception("Oauth client .well-known/openid-configuration not found")

            login = {'grant_type': 'client_credentials', 'client_id': self.client, 'client_secret': self.secret}
            response = requests.post(self.token_url, data=login, verify=self.cert)
            if response.ok:
                self.token = response.json()['access_token']
                self.exp = get_exp(self.token)
                return self.token
            else:
                raise Exception("Oauth client not found")

    instance = None

    def __init__(self):
        if not ServiceToken.instance:
            ServiceToken.instance = ServiceToken._ServiceToken()

    def __getattr__(self, name):
        return getattr(self.instance, name)