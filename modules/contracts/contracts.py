import flask
from flexcoop_utils import send_inter_component_message


def pre_get__contracts_callback(request, lookup):
    """
    GET callback for the contract endpoint
    request: eve request object
    lookup: reference to external lookup object
    """
    sub = request.account_id
    role = request.role

    if role == 'prosumer':
        lookup["account_id"] = sub

    elif role == 'aggregator':
        lookup["agr_id"] = sub

    elif role == 'admin':
        pass

    elif role == 'service' and sub == "DSAR":
        pass

    elif role == 'service' and sub == "OMP":
        pass

    else:
        flask.abort(403, description='GET contract not allowed for '+role+' '+sub)


def pre_patch__contracts(request, lookup):
    sub = request.account_id
    role = request.role

    print('PATCH contract  request: ', request.json)

    has_error = False
    error_str = ""
    for entry in ['contract_id', 'start_date', 'end_date', 'agr_id', 'account_id',
                  'template_id', 'assets', 'contract_type']:
        if entry in  request.json:
            error_str = error_str + entry+','
            has_error = True

    if 'validated' in request.json and (role != 'service' or sub != 'OMP'):
        error_str = error_str + 'validated'
        has_error = True

    if has_error:
        flask.abort(403, description='PATCH contract of ' + error_str + ' field(s) not allowed')

    else:
        if role == 'prosumer':
            request.json['validated'] = False
            lookup["account_id"] = sub

        elif role == 'aggregator':
            request.json['validated'] = False
            lookup["agr_id"] = sub

        elif role == 'service' and sub == 'OMP':
            pass

        else:
            flask.abort(403, description='PATCH contract not allowed for ' + role + ' ' + sub)


def post_patch__contracts(request,payload):
    if payload.status_code == 200:
        if request.role == 'service' and request.account_id != 'OMP':
            pass

        elif request.role == 'aggregator':
            send_inter_component_message(recipient='OMP', msg_type='AGGREGATOR_PATCH',
                                        json_payload={'contract_id': request.view_args['contract_id'],
                                                      'patch' : request.json})
        elif request.role == 'prosumer':
            send_inter_component_message(recipient='OMP', msg_type='PROSUMER_PATCH',
                                        json_payload={'contract_id': request.view_args['contract_id'],
                                                      'patch' : request.json})


def pre_post__contracts(request):
    if request.role == 'aggregator':
        pass
    else:
        flask.abort(403, description='POST contract not allowed for ' + request.role)


def post_post__contracts(request,payload):
    if payload.status_code == 201:
        send_inter_component_message(recipient='OMP', msg_type='NEW_CONTRACT',
                                     json_payload={'contract_id': request.json['contract_id']})
    else:
        pass


def pre_delete__contracts(request, lookup):
    if request.role == 'admin':
        pass
    else:
        flask.abort(403, description='DELETE contract not allowed for ' + request.role)


def set_hooks(app):
    app.on_pre_GET_contracts += pre_get__contracts_callback
    app.on_pre_PATCH_contracts += pre_patch__contracts
    app.on_post_PATCH_contracts += post_patch__contracts
    app.on_pre_POST_contracts += pre_post__contracts
    app.on_post_POST_contracts += post_post__contracts
    app.on_pre_DELETE_contracts += pre_delete__contracts
