import flask
from flask import current_app


def pre_devices_GET_callback(request, lookup):
    #print('A GET request on a DER  endpoint has just been received!')
    #print(request)

    sub = request.sub
    role = request.role

    if role == 'prosumer':
        #print('limiting results to account_id')
        lookup["account_id"] = sub

    elif role == 'aggregator' or role == 'service':
        pass

    else:
        print('error: GET DER unknown role ',role)
        flask.abort(403)


def pre_devices_POST_callback(request):
    #print('A POST request on a DER  endpoint has just been received!')
    #print(request)

    role = request.role

    if role == 'prosumer':
        pass

    else:
        print('error: POST DER role != prosumer')
        flask.abort(403)


def on_inserted_devices_callback(devices):
    pass

def set_hooks(app):
    app.on_pre_GET_devices += pre_devices_GET_callback
    app.on_pre_POST_devices += pre_devices_POST_callback
    app.on_inserted_devices += on_inserted_devices_callback