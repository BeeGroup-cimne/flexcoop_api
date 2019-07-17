from endpoint_schema import DOMAIN
from documentation import SWAGGER_INFO
import os
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_USERNAME = os.environ['MONGO_USERNAME']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_DBNAME = os.environ['MONGO_DBNAME']

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
API_VERSION = "1"
TRANSPARENT_SCHEMA_RULES = True
DEBUG = False
OAUTH_PROVIDERS = [
    "https://flexcoop-auth-server.okd.fokus.fraunhofer.de",
    "https://oauth2-flexcoop-keycloak.okd.fokus.fraunhofer.de/auth/realms/flexcoop"
]
# Disabled 'User-Restricted Resource Access'
# See middleware wiki: https://gitlab.fokus.fraunhofer.de/FlexCoop/Documentation/wikis/middleware_info
#
# AUTH_FIELD = "account"
