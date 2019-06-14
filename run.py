from eve import Eve
from eve_swagger import swagger, add_documentation
from flask_swagger_ui import get_swaggerui_blueprint
from auth.authentication import JWTokenAuth

SWAGGER_URL = '/docs'
API_URL = '/api-docs'
app = Eve(auth=JWTokenAuth)
app.register_blueprint(swagger)
SWAGGER_EXT = {
    'securityDefinitions': {
        'JWTAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'security': [
        {'JWTAuth': []}
    ],
}
add_documentation(SWAGGER_EXT)

for resource, rd in app.config['DOMAIN'].items():
    if (rd.get('disable_documentation')
            or resource.endswith('_versions')):
        continue
    methods = rd['resource_methods']
    url = '/%s' % rd['url']
    for method in methods:
        add_documentation({'paths': {url: {method.lower(): {"security": [{"JWTAuth": []}]}}}})
    methods = rd['item_methods']
    item_id = '%sId' % rd['item_title'].lower()
    url = '/%s/{%s}' % (rd['url'], item_id)
    for method in methods:
        add_documentation({'paths': {url: {method.lower(): {"security": [{"JWTAuth": []}]}}}})

# required. See http://swagger.io/specification/#infoObject for details.
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': 'FLEXCoop REST API'
    })

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.run()
