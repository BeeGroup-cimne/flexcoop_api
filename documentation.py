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
http://api.com/some_resource?where=[("field", asc)]
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
    'schemes': ['http', 'https'],
}