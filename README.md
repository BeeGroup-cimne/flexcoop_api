# Middleware RESTful API

This project is intended to provide an RESTful API for the communciation of FLEXCoop components. The API will be installed in a server managed by CIMNE.


## 1. Communication Process

The communication process will be performed as the component that generates the output data will upload it to the API (by means of POST, PATCH or PUT). The component that needs to read the data, will retrieve it (By means of GET).

Additionally, if some components needs to be notified when some new data is posted, or requires some events, a (pre/post)event hook can be implemented. However, the component will require a secure API to get the required data (using the Oauth2.0)



## 1. Generate endpoints

To generate the endpoints required for your component, you should follow these points:

1. Generate the resource schema. [see doc](#1-generate-the-resource-schema)
2. Generate the resource hooks. [see doc](#2-generate-the-resource-hooks)
3. Deploy your resource to CIMNE's middleware. [see doc](3-deploy-your-resource-to-cimne-middleware)

### 1. Generate the resource schema

The API will provide all the required endpoints, that should be generated as a [Cerberus JSON Schema](http://docs.python-cerberus.org/en/stable/). 

The possible available option, more information about the endpoint configuration can be found in the documentation of [Python Eve](https://docs.python-eve.org/en/stable/config.html#domain-configuration)

While the available configurations are the same as can be seen in the previous link, some modifications have been applied in the current project.

1. The documents should be saved as a `<resource_name>.json` file. In the example, `temperature.json`. 
2. The format of the file has to be in `json` instead of `python dictionary`. The translation almost trivial ([see section for translation](#translation-between-python-and-json)). 

**EXAMPLE**
```json
{
  "item_title": "temperature",
  "cache_control": "max-age=10,must-revalidate",
  "cache_expires": 10,
  "resource_methods": ["GET", "POST"],
  "item_methods": ["PATCH"],
  "aggregation":{
    "index_field":"timestamp"
  },
  "schema":{
    "prosumer_id" : {
      "type" : "uuid"
    },
    "timestamp": {
      "type": "datetime",
      "required": true
    },
    "value": {
      "type": "float",
      "min": "-40",
      "max": "40",
      "required": true
    },
    "space": {
      "type": "list",
      "allowed": ["kitchen", "living", "bedroom"]
    },
    "configuration": {
      "type": "dict",
      "schema": {
        "param1": {"type": "string"},
        "param2": {"type": "float"}
      },
      "required": false
    }
  }
}
```

*Special remarks*

1. `datetime` type has already been defined to match the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) an should be pased using UTC timezone. `YYYY-MM-DDThh:mm:ss.fffZ`
2. Is important to add all fields required for the access control. In this example `prosumer_id`.
3. All the ID's in the document should be of the flexcoop agreed type `uuid`.
4. An extra configuration `aggregation` file has been added in order to allow the resample of the data to other frequency. Set the aggregation_index_field for the timeseries, and call the API endpoint aggregate (Beta functionality).

This configuration result in an endpoint like http://<server ip>/<api version number>/tempreature . In a dev environment this will most likely be http://127.0.0.1:5000/1/temperature .

### 2. Generate the resource hooks
Hooks are programmable actions that will be called when communicating with the API. [See documentation](https://docs.python-eve.org/en/stable/features.html#event-hooks)

To add them into the project, create a module into `modules` directory, and add the required functions within a file with the same name as the module. This module should implement a function `def set_hooks(app)`
that will recieve an app object as a parameter and should install the hooks of this module. Take care to not install your hooks to the general `GET`, `PATHC`, `POST` or `DELETE` methods as you will change the behavour also for other parners.

You will need to use this hooks for programing the access control to your resources. The user information can be obtained through the `request.sub`, `request.role` and `request.iss` variables.

**EXAMPLE**
```python
import flask
from flask import request


def pre_temperature_GET_callback(request, lookup):
    print('A GET request on a temperature  endpoint has just been received!')
    # access the user information in the request

    sub = request.sub
    role = request.role
    iss = request.iss

    # program the access control
    if role == 'prosumer':
        print('limiting results to prosumer_id')
        lookup["prosumer_id"] = sub
    elif role == 'aggregator':
        print("aggregator does not have permission to get temperature")
        flask.abort(403)
    elif role == "service":
        print("service can access all temperature fields")
    else:
        print("the role does not exists")
        flask.abort(403)


def pre_temperature_POST_callback(request):
    print('A POST request on a temperature  endpoint has just been received!')
    sub = request.sub
    role = request.role
    iss = request.iss

    if role == 'prosumer':
        print('prosumer is allowed to post temperature')
    elif role == 'aggregator':
        print("aggregator does not have permission to post temperature")
        flask.abort(403)
    elif role == "service":
        print("service does not have permission to post temperature")
        flask.abort(403)
    else:
        print("the role does not exists")
        flask.abort(403)


# When the user inserts data, we can double check if the prosumer_id is equal to the user making the request
def on_insert_temperature_callback(items):
    print('An item is going to be inserted')
    for item in items:
        if item['prosumer_id'] != request.sub:
            flask.abort(403)


# We can also define fieds that can't be changed during an update. For example, the user is only allowed to update the params, while the service is allowed to update all document
def on_update_temperature_callback(updates, original):
    print('An item is going to be updated')
    sub=request.sub
    role = request.role
    if role == "prosumer":
        allowed_keys = ["configuration"]
        invalid_dic = {k: v for k, v in updates.items() if not k.startswith("_") and k not in allowed_keys}
        print(invalid_dic)
        if invalid_dic:
            flask.abort(403, "The prosumer can only update: {}".format(", ".join(allowed_keys)))
    elif role == "aggregator":
        flask.abort(403)
    elif role == "service":
        print("Services can update everything")
    else:
        flask.abort(403)


# Finally define your installing function:
def set_hooks(app):
    app.on_pre_GET_temperature += pre_temperature_GET_callback
    app.on_pre_POST_temperature += pre_temperature_POST_callback
    app.on_insert_temperature += on_insert_temperature_callback
    app.on_update_temperature += on_update_temperature_callback
```

### 3. Deploy your resource to CIMNE middleware

Once your endpoints are working in the developement environment, you can deploy them to production by:

1. Generate the `endpoint.json` file following the schema directives. Make sure the json file can be read by python with the `json.load` function.
2. Upload the `endpoint.json` file into the endpoint_schema folder. *The base name of the file will be the endpoint name in the API*
3. Generate the hooks into a module inside `modules` following the hooks directives.
4. Test and debug in your local environent ([see docs](#3-install-and-build)).
5. Push the changes to the git repository.
6. Notify `egabaldon@cimne.upc.edu` to the changes made
7. The changes will be uploaded to the production API as soon as possible.


## 2. API Documentation
The API disposes of a dynamic documentation generated automatically using Swagger. If you have a swagger interpreter, you can access to the [provider url](/api-docs/), else you can access the [HTML swagger interpreter](/docs)

You can customize the documentation of your provided endpoints following the [Python eve swagger](https://github.com/pyeve/eve-swagger) documentation

## 3. Install and Build

To install or build the repository in your own server, follow this steps:

1. Download or clone the repository
```bash
git clone https://gitlab.fokus.fraunhofer.de/FlexCoop/middleware_rest
```
2. Install the requirements of the project `requirements.txt`
```bash
# create a python virtualenv
virtualenv venv
# activate the virtualenv
source venv/bin/activate
# now your shell hostname sould have the virtualenv between parentheses
# install all requirements in the virtualenv

pip install -r requirements.txt

# remember to activate the virtualenv everytime you are going to use the server
```
3. Create the following environment variables (Notice you need a [local mongo](install-a-local-mongo) for debuging):
   ```bash
   export MONGO_HOST='<mongo_host>'
   export MONGO_PORT=<mongo_port>
   export MONGO_USERNAME='<mongo_username>'
   export MONGO_PASSWORD='<mongo_password>'
   export MONGO_DBNAME='<mongo_database>'
   export OAUTH_PROVIDERS="<valid_oauth_providers>" 
   export CLIENT_OAUTH='service_provider_oauth_name'
   export CLIENT='client_id_of_this_project_in_client_oauth'
   export SECRET='secret_id_of_this_project_in_client_oauth'
   export NOTIFICATION_OPENADR_URL="url_to_notify_openADR_of_actions"
   export NOTIFICATION_OPENADR_CERT="cert_of_openadr_url"
   export INTERCOMPONENT_SETTINGS="<inter_component_settings>" 

   ```
   *NOTES*: 
   
   The notification variables "NOTIFICATION_OPENADR_URL" and "NOTIFICATION_OPENADR_URL" are used to notify the openADR component that an event has to be sent using OpenADR. (If not using this feature you can leave them blank)
   
   "OAUTH_PROVIDERS" is a dict containing all oauth providers that the middleware will accept their tokens:
   ``` bash
   "{
        'provider_self_assigned_name': {
            'url': 'url of provider', 
            'cert': True = known cert | False = disable ssl validation | 'path_to_cert' = path to a self signed certificate
            'client_id': 'client_id of the rest application in each provider'
        },{...}
   }"
   
   #example:
   "{
    'cimne':{'url': 'https://oauth.middleware.platform.flexcoop.eu', 'cert':False, 'client_id': '688669'}
   }"
   ```

   "INTERCOMPONENT_SETTINGS" is a dict containing the settings for sending intercomponent messages from the middleware: 
   ``` bash
   "{
        'component shortname': {
            'message_url': 'endpoint where component receives ICM messages',
            'account_id': 'the account id supplied in the servicetoken in an ICM from that component' 
        },{...}
   }"
   
   #example:
   "{
    'OMP':{'message_url': 'https://marketplace.flexcoop.eu/1/interComponentMessage','account_id': 'marketplace'},
    'LDEM':{'message_url': 'http://cloudtec.etra-id.com:6100/api/drevent/notify','account_id': 'LDEM'}, 
   }"
   ```
   Look carefully the single and double quotes used in the variable value for "OAUTH_PROVIDERS" and "INTERCOMPONENT_SETTINGS"

   
   The optional boolean environment variable ICM_WORKER_THREAD controls, if the interComponentMessage worker thread 
   is started. If not specified, ICM_WORKER_THREAD defaults to 'True'. Set it to 'False' on local instances will 
   prevent delivery attempts from that instance when the DB changed (for the 'real' instance). 
   
    
   To be able to run several components on a single computer, the host port can be specified by an optional environment variable: 
   ```bash
   export HOST_PORT=8081
   ```
   (you may want to store this e.g. in a set_env.sh which you can source every time you need it)

   
4. run the server with `python run.py`

## ANNEX:

### Translation between python and json

The translation between cerberus schema (`python`) to `json` is very trivial.

1. Make sure you are using double quotes `"` instead of single quotes `'` for all string delimiters.
2. All variables should be in the `javascript` format. EX: the true value in python `True` should be `true` in the json.
3. If you want to use the `regex` function, you have to escape all in-function `"` with `\"`. EX: `"regex(\"[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\")"`

### Install a local mongo

To install a local mongo, follow the instructions in the [mongo documentation](https://docs.mongodb.com/manual/installation/) depending on your operation system.

Once installed, create the database and user to link the REST API.

```bash

#open mongodb shell

mongo

# this will only work for local connections, additional parameters can be used to connect to a remote mongo

# create and connect to the database

use 'databasename'

# create the user with readWrite permissions in the database

db.createUser({"user": "yourusername", "pwd": "yourpassword", "roles":["readWrite"]})


```