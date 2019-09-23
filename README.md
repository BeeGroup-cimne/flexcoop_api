# Middleware RESTful API

This project is intended to provide an RESTful API for the communciation of FLEXCoop components. The API will be installed in a server managed by CIMNE.

## 1. Generate endpoints

### Resource Schema
The API will provide all the required endpoints, that should be generated as a [Cerberus JSON Schema](http://docs.python-cerberus.org/en/stable/). 

**EXAMPLE**
```json
{
  "firstname": {
    "type": "string",
    "minlength": 1,
    "maxlength": 10
  },
  "lastname": {
    "type": "string",
    "minlength": 1,
    "maxlength": 15,
    "required": true,
    "unique": true
  },
  "role": {
    "type": "list",
    "allowed": ["author", "contributor", "copy"]
  },
  "location": {
    "type": "dict",
      "schema": {
        "address": {"type": "string"},
        "city": {"type": "string"}
      }
  },
  "born": {
    "type": "datetime"
  }
}
```

*Special remarks*

1. `datetime` type has already been defined to match the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) an should be pased using UTC timezone. `YYYY-MM-DDThh:mm:ss.fffZ`
2. `account` field is automatically added by the API depending on the user performing the request (extracted from the JWT Token).

### Endpoint Configuration

Additionally, in order to generate the endpoints, some configuration must be included in the json.

**EXAMPLE**
```json
{
  "item_title": "person",
  "additional_lookup": {
    "url": "regex(\"[\\w]+\")",
    "field": "lastname"
  },
  "cache_control": "max-age=10,must-revalidate",
  "cache_expires": 10,
  "resource_methods": ["GET", "POST"],
  "schema": previous_schema_definition
}
``` 
The result of combining both, resource schema and the endpoint configuration must be saved as <endpoint-name>.json . Following the example above person.json should be created.
This will result in an endpoint like http://<server ip>/<api version number>/person . In a dev environment this will most likely be http://127.0.0.1:5000/1/person .
More information about the endpoint configuration can be found in the documentation of [Python Eve](https://docs.python-eve.org/en/stable/config.html#domain-configuration)

### Activate an endpoint

By the time of witting this documentation, the addition of a new endpoint to the API is still done in a manual way.

1. Generate the `endpoint.json` file following the schema directives. Make sure the json file can be read by python with the `json.load` function.
2. Upload the `endpoint.json` file into the endpoint_schema folder. *The base name of the file will be the endpoint name in the API*
3. Push the changes to the git repository.
4. Notify `egabaldon@cimne.upc.edu` to the changes made
5. The changes will be uploaded to the production API as soon as possible.

## 2. API Documentation
The API disposes of a dynamic documentation generated automatically using Swagger. If you have a swagger interpreter, you can access to the [provider url](/api-docs/), else you can access the [HTML swagger interpreter](/docs)

You can customize the documentation of your provided endpoints following the [Python eve swagger](https://github.com/pyeve/eve-swagger) documentation

## 3. Install and Build

To install or build the repository in your own server, follow this steps:

1. Download or clone the repository
2. Install the requirements of the project `requirements.txt`
3. Create the following environment variables:
   ```bash
   export MONGO_HOST='<mongo_host>'
   export MONGO_PORT=<mongo_port>
   export MONGO_USERNAME='<mongo_username>'
   export MONGO_PASSWORD='<mongo_password>'
   export MONGO_DBNAME='<mongo_database>'
   ```
   (you may want to store this e.g. in a set_env.sh which you can source every time you need it)
   
   To be able to run several components on a single computer, the host port can be specified by an optional environment variable: 
   ```bash
   export HOST_PORT=8081
   ```
4. run the server with `python run.py`

