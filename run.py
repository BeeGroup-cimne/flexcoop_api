from eve import Eve
from eve_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from documentation import *
from auth.authentication import JWTokenAuth


app = Eve(auth=JWTokenAuth)
# we have to call init_documentation to set the "SWAGGER_INFO" config variable before the registration of the blueprint
init_documentation(app)

app.register_blueprint(swagger)

# This is done to add extra information to the methods presented, as the "TOKEN" authentication
set_methods_documentation(app)

SWAGGER_URL = '/docs'
API_URL = '/api-docs'

swaggerui_blueprint = get_swaggerui_blueprint(
SWAGGER_URL, # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
API_URL,
config={ # Swagger UI config overrides
    'app_name': 'FLEXCoop REST API'
})

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


app.run()