# LIVE FLEXcoop RESTFULL DEMO
1. Set the `temperature.json` file
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
2. check it is correct with `json.load`
```python
import json
print(json.load(open("endpoint_schema/temperature.json")))
```
3. access the resource and check it works
    - go to the server and "get/post" some documents

4. populate db using utils
    - show data files
    - show populate_db.ini
    - run populate_db.py
    
    
5. Show aggregate values functionality:
    - resource = "temperature"
    - resolution = "2H"
    - operation = "AVG"
    - page = 1
    
    *advise of long time if requested for many data*
    
6. Program the access control using Hooks:
    - Create a module in `modules` directory (remember to add an empty `__init.py` file)
    - Create the file with the same name inside (`temperature.py`)
    - Add the required hooks
    - show get with different user roles
    - show post with different user roles
    - show patch with different user roles and modifing more that `configuration` as prosumer

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

