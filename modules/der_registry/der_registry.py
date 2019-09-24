import flask



def pre_der_GET_callback(request, lookup):
    print('A GET request on a DER  endpoint has just been received!')
    print(request)

    sub = request.sub
    role = request.role

    if role is None:
        print('unknown role')
        flask.abort(403)

    elif role == 'prosumer':
        print('limiting results to account_id')
        lookup["account_id"] = sub


def pre_der_POST_callback(request):
    print('A POST request on a DER  endpoint has just been received!')
    print(request)

    sub = request.sub
    role = request.role

    if role != 'prosumer':
        print('role != prosumer')
        flask.abort(403)


def pre_flexibility_GET_callback(request, lookup):
    print('A GET request on a Flexibility  endpoint has just been received!')
    print(request)

    sub = request.sub
    role = request.role

    if role is None:
        print('unknown role')
        flask.abort(403)

    elif role == 'prosumer':
        print('limiting results to account_id')
        lookup["account_id"] = sub


def pre_flexibility_POST_callback(request):
    print('A POST request on a Flexibility  endpoint has just been received!')
    print(request)


def set_hooks(app):
    app.on_pre_GET_der += pre_der_GET_callback
    app.on_pre_POST_der += pre_der_POST_callback
    app.on_pre_GET_flexibility += pre_flexibility_GET_callback
    app.on_pre_POST_flexibility += pre_flexibility_POST_callback