import ast

from endpoint_schema import DOMAIN
import os
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_USERNAME = os.environ['MONGO_USERNAME']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_DBNAME = os.environ['MONGO_DBNAME']

RENDERERS = [
    'eve_customization.render.NaNJSONRenderer',
    'eve.render.XMLRenderer'
]

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
API_VERSION = "1"
TRANSPARENT_SCHEMA_RULES = True
PAGINATION_LIMIT = 300
DEBUG = False
OAUTH_PROVIDERS = ast.literal_eval(os.environ['OAUTH_PROVIDERS'])
# Disabled 'User-Restricted Resource Access'
# See middleware wiki: https://gitlab.fokus.fraunhofer.de/FlexCoop/Documentation/wikis/middleware_info
#
AUTH_FIELD = "account"

NOTIFICATION_OPENADR_URL = os.environ['NOTIFICATION_OPENADR_URL']
NOTIFICATION_OPENADR_CERT = os.environ['NOTIFICATION_OPENADR_CERT']
CLIENT = os.environ['CLIENT']
SECRET = os.environ['SECRET']
CLIENT_OAUTH = os.environ['CLIENT_OAUTH']

STANDARD_ERRORS = [400, 401, 403, 404, 405, 406, 409, 410, 412, 422, 428, 429]

INTERCOMPONENT_SETTINGS = ast.literal_eval(os.environ['INTERCOMPONENT_SETTINGS'])

ICM_WORKER_THREAD = True
if 'ICM_WORKER_THREAD' in os.environ:
    ICM_WORKER_THREAD = ast.literal_eval(os.environ['ICM_WORKER_THREAD'])
