import requests
from eve.auth import TokenAuth

from settings import OAUTH_PROVIDERS

from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)
from datetime import datetime, timedelta

class KeyCache(object):
    class _KeyCache(object):
        def __init__(self, providers, update_key_freq):
            self.providers = providers
            self.keys = []
            self.last_time = None
            self.update_key_time = update_key_freq
            self.get_keys()

        def get_keys(self):
            if self.last_time and self.keys and self.last_time + self.update_key_time >= datetime.utcnow():
                return self.keys
            self.keys = []
            self.last_time = datetime.utcnow()
            for provider in self.providers:
                try:
                    p_info = requests.get("{}/.well-known/openid-configuration/".format(provider)).json()
                    key_url = p_info["jwks_uri"]
                    key_list = requests.get(key_url).json()
                    for key in key_list['keys']:
                        self.keys.append({"key": jwk_from_dict(key), "iss": provider, "kid": key['kid']})
                except:
                    self.keys.append({"key": None, "iss": provider, "kid": None})
            return self.keys

        def __str__(self):
            return repr(self)

    instance = None

    def __init__(self, providers, update_key_freq):
        if not KeyCache.instance:
            KeyCache.instance = KeyCache._KeyCache(providers, update_key_freq)

    def __getattr__(self, name):
        return getattr(self.instance, name)


class JWTokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        jwt = JWT()
        keys_cache = KeyCache(OAUTH_PROVIDERS, timedelta(minutes=10))
        keys = keys_cache.get_keys()
        user_info = None
        key=None
        for key in keys:
            try:
                user_info = jwt.decode(token, key['key'])
                key=key
                break
            except Exception as e:
                pass
        if not user_info:
            return False
        issuer = user_info['iss']
        expiration = datetime.utcfromtimestamp(user_info['exp'])
        role = user_info['role']
        flexId = user_info['sub']
        now_time = datetime.utcnow()
        if expiration < now_time:
            return False
        if issuer != key['iss']:
            return False
        # TODO: define what to do with the roles
        if role == "prosumer":
            self.set_request_auth_value(flexId)
        elif role == "aggragator":
            pass
        elif role == "sevice":
            pass
        return True

