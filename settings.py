import ast

from endpoint_schema import DOMAIN
import os
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_USERNAME = os.environ['MONGO_USERNAME']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_DBNAME = os.environ['MONGO_DBNAME']

RENDERERS = [
    'eve.render.JSONRenderer',
    'eve.render.XMLRenderer'
]

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
API_VERSION = "1"
TRANSPARENT_SCHEMA_RULES = True
DEBUG = False
OAUTH_PROVIDERS = ast.literal_eval(os.environ['OAUTH_PROVIDERS'])
NOTIFICATION_OPENADR = os.environ.get("NOTIFICATION_OPENADR")
# Disabled 'User-Restricted Resource Access'
# See middleware wiki: https://gitlab.fokus.fraunhofer.de/FlexCoop/Documentation/wikis/middleware_info
#
AUTH_FIELD = "account"
NUM_PROXIES = os.environ["NUM_PROXIES"]