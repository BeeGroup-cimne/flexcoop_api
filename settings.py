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
DEBUG = True
OAUTH_PROVIDERS = [
    "https://flexcoop-auth-server.okd.fokus.fraunhofer.de",
    "https://oauth2-flexcoop-keycloak.okd.fokus.fraunhofer.de/auth/realms/flexcoop"
]
AUTH_FIELD = "account"
