import flask

def pre_contract_GET_callback(request, lookup=None):
    #print('A GET request on a Marketplace Contract endpoint has just been received!')
    #print(request)

    sub = request.sub
    role = request.role

    #print(sub)
    #print(role)
    #print(request.iss)

    if role == 'prosumer':
        # print('limiting results to prosumer_id')
        lookup["prosumer_id"] = sub

    elif role == 'aggregator':
        # print('limiting results to agr_id')
        lookup["agr_id"] = sub

    elif role == 'service':
        pass

    else:
        print('error: GET contract unknown role ',role)
        flask.abort(403)

def set_hooks(app):
    app.on_pre_GET_contract += pre_contract_GET_callback
