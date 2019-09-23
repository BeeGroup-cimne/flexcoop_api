from datetime import datetime, timedelta

from jwt import (
    JWT,
    jwk_from_dict
)
import requests
from eve.auth import TokenAuth
from flask import current_app as app

from settings import OAUTH_PROVIDERS


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
        # TODO: konami code!! Remove when release
        # TODO:____________KONAMI CODE START______________________
        flex_id = None
        issuer = None
        role = None
        if token == "UUDDLRLRBA1":
            role = "prosumer"
            flex_id = "1111111-1111-1111-1111-111111111111"
            issuer = "http://217.182.160.171:9042"
        if token == "UUDDLRLRBA11":
            role = "prosumer"
            flex_id = "1111111-1111-1111-1111-111111111112"
            issuer = "http://217.182.160.171:9043"
        if token == "UUDDLRLRBA2":
            role = "aggregator"
            flex_id = "2222222-2222-2222-2222-222222222222"
            issuer = "http://217.182.160.171:9043"
        if token == "UUDDLRLRBA3":
            role = "service"
            flex_id = "3333333-3333-3333-3333-333333333333"
            issuer = ""
        # TODO:____________KONAMI CODE END______________________
        if flex_id is None:
            jwt = JWT()
            keys_cache = KeyCache(OAUTH_PROVIDERS, timedelta(minutes=10))
            keys = keys_cache.get_keys()
            user_info = None
            key = None
            for key in keys:
                try:
                    user_info = jwt.decode(token, key['key'])
                    key = key
                    break
                except Exception as e:  # todo catch only corresponding exceptions here
                    pass
            if not user_info:
                return False
            else:
                issuer = user_info['iss']
                expiration = datetime.utcfromtimestamp(user_info['exp'])
                role = user_info['role']
                flex_id = user_info['sub']
                now_time = datetime.utcnow()
                if expiration < now_time:
                    return False
                if issuer != key['iss']:
                    return False
        if issuer is None:  # make sure the code above has catched all conditions
            raise AuthenticationException("No issuer was detected, this should not happen")
        else:
            org_id = issuer  # todo why do we do this inited of using issuer?

        if role is None:
            raise AuthenticationException("No role was detected, this should not happen")

        # TODO: define what to do with the roles
        if role == "prosumer":
            self.set_request_auth_value([flex_id, org_id])
            return True
        elif role == "aggregator":
            try:
                # user = app.data.driver.db['aggregators'].find_one({'account': flex_id})
                db_resource = app.config['DOMAIN'][resource]
                if db_resource['datasource']['filter'] is None:
                    db_resource['datasource']['filter'] = {"{}.1".format(app.config['AUTH_FIELD']): org_id}
                else:
                    db_resource['datasource']['filter'].update({"{}.1".format(app.config['AUTH_FIELD']): org_id})
                return True
            except Exception as e:
                # return False
                raise AuthenticationException(e)

        elif role == "service":
            return True
        return False


class AuthenticationException(Exception):
    pass
