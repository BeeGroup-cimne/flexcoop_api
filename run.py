from os import environ

from eve import Eve
from eve_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from documentation import *
from flexcoop_blueprints import flexcoop_blueprints, set_documentation
from datatypes import UUIDEncoder, UUIDValidator
from flexcoop_hooks import filter_internal_schema, filter_item_schema
from auth.authentication import JWTokenAuth
import modules
from settings import NUM_PROXIES

SWAGGER_URL = '/docs'
API_URL = '/api-docs'
app = Eve(auth=JWTokenAuth, json_encoder=UUIDEncoder, validator=UUIDValidator)

# we have to call init_documentation to set the "SWAGGER_INFO" config variable before the registration of the blueprint
init_documentation(app)

app.register_blueprint(swagger)

# This is done to add extra information to the methods presented, as the "TOKEN" authentication
set_methods_documentation(app)

app.json_encoder = UUIDEncoder
# required. See http://swagger.io/specification/#infoObject for details.
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': 'FLEXCoop REST API'
    })

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.register_blueprint(flexcoop_blueprints, url_prefix="/" + app.config['API_VERSION'])
set_documentation()

modules.add_resource_hooks(app)

#add flexcoop filtering hooks
app.on_fetched_resource += filter_internal_schema
app.on_fetched_item += filter_item_schema


if __name__ == '__main__':
    try:
        HOST_PORT = environ['HOST_PORT']
    except KeyError:
        HOST_PORT = 8080
    app.run(port=int(HOST_PORT), host="0.0.0.0")
