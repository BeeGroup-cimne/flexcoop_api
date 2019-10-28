from eve_swagger import add_documentation

description ="""
### How to use the REST API
There are 4 methods available that can be used with the provided endpoints. To specify an item, the specified "id" of this item has to be provided to the endpoint

- **GET**
To obtain an item or list of items of resource

- **POST**
Insert a new item or a list of items in a resource collection.
*It is important to add request header <abbr title="Indicates the format of the content of the request body">Content-Type</abbr>*

- **PATCH**
Updates an item
*It is important to add request header <abbr title="Indicates the format of the content of the request body">Content-Type</abbr> and <abbr title="Indicates a field added automatically on item insertion to support concurrency control called '_etag'">If-Match</abbr>.*

- **DELETE**
Deletes an item of the resource
*It is important to add request header <abbr title="Indicates a field added automatically on item insertion to support concurrency control called '_etag'">If-Match</abbr>.*

### Filtering
The resources can be filtered and sorted using the `where` get parameter
~~~
http://api.com/some_resource?where={"key": value}
~~~

### Sorting
The resources can be sorted using the `sort` get paramether. The ordering will be defined with the <abbr title="1 ascendent -1 descendent">asc</abbr> parameter
~~~
http://api.com/some_resource?sort=[("field", asc)]
~~~

### Authentication
To use the API, an JWT Token is required, this token must be obtained using one of the Oauth2.0 server providers.
*All methods should include the <abbr title="Indicates the authentication token">Authentication</abbr> request header.*

"""



SWAGGER_INFO = {
    'title': 'FLEXCoop API Documentation',
    'version': '1.0',
    'description': description,
    'contact': {
        'name': 'Eloi Gabaldon',
        'url': 'mailto:egabaldon@cimne.upc.edu'
    },
    'schemes': [],
}

SWAGGER_EXT = {
    'securityDefinitions': {
        'JWTAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'security': [
        {'JWTAuth':[]}
    ],
}
add_documentation(SWAGGER_EXT)

def init_documentation(app):
    app.config['SWAGGER_INFO']=SWAGGER_INFO

def set_methods_documentation(app):
    for resource, rd in app.config['DOMAIN'].items():
        if (rd.get('disable_documentation')
                or resource.endswith('_versions')):
            continue
        methods = rd['resource_methods']
        url = '/%s' % rd['url']
        for method in methods:
            parameters = []
            if method == "GET":
                parameters = [
                    {"name":"where", "in": "query", "type":"string", "description": "filter by value"},
                    {"name":"sort", "in": "query", "type":"string", "description": "sort by value"}
                ]
            add_documentation(
                {
                    'paths': {
                        url: {
                            method.lower(): {
                                "parameters": parameters,
                                "security": [
                                    {"JWTAuth": []}
                                ]
                            }
                        }
                    }
                }
            )


        methods = rd['item_methods']
        item_id = '%sId' % rd['item_title'].lower()
        url = '/%s/{%s}' % (rd['url'], item_id)
        for method in methods:
            add_documentation({'paths': {url: {method.lower(): {"security": [{"JWTAuth": []}]}}}})

