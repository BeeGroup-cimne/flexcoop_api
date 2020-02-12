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

    elif role == 'service':
        if sub is "DSAR":
            pass
        elif sub == 'OMP':
            pass
        else:
            print('error: GET contract not allowed for ', role, '  ', sub)
            flask.abort(403)
    else:
        print('error: GET contract unknown role ', role)
        flask.abort(403)


def pre_patch__contracts(request, lookup):
    sub = request.account_id
    role = request.role

    print('PATCH contract  request: ', request.json)

    has_error = False
    error_str = ""
    for entry in ['contract_id', 'start_date', 'end_date', 'agr_id', 'account_id',
                  'template_id', 'assets', 'contract_type']:
        if entry in  request.json:
            error_str = error_str + ' ' + entry
            print('error: PATCH contract modification of ',entry,' not allowed')
            has_error = True

    if 'validated' in request.json and (role != 'service' or sub != 'OMP'):
        print('error: PATCH contract modification of "validated"  not allowed for ', role, '  ', sub)
        has_error = True

    if has_error:
        flask.abort(403, {'error': 'Modification of ' + error_str + ' not allowed'})

    if role == 'prosumer':
        lookup["account_id"] = sub

    elif role == 'aggregator':
        lookup["agr_id"] = sub

    elif role == 'service':
        if sub == 'OMP':
            pass
        else:
            print('error: PATCH contract not allowed for ', role, '  ', sub)
            flask.abort(403)
    else:
        print('error: PATCH contract not allowed for ', role, '  ', sub)
        flask.abort(403)


def post_patch__contracts(request,payload):
    if payload.status_code == 200:
        if request.role == 'service' and request.account_id != 'OMP':
            #Todo The message send depends on the acknowledgement state of the contract

            if request.json['validated']:
                print('PATCH contract validated, inform prosumer')
            else:
                print('PATCH contract rejected, inform aggregator')

        # if aggregator changed stuff, the contract is then active and valid
        pass


def pre_post__contracts(request):
    if request.role == 'aggregator':
        pass
    else:
        print('error: POST contract not allowed for ', request.role)
        flask.abort(403)


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
        print('error: DELETE contract not allowed for ', request.role)
        flask.abort(403)

def set_hooks(app):
    app.on_pre_GET_contracts += pre_get__contracts_callback
    app.on_pre_PATCH_contracts += pre_patch__contracts
    app.on_post_PATCH_contracts += post_patch__contracts
    app.on_pre_POST_contracts += pre_post__contracts
    app.on_post_POST_contracts += post_post__contracts
    app.on_pre_DELETE_contracts += pre_delete__contracts
