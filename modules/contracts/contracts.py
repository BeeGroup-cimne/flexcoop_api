import flask
from flexcoop_utils import send_inter_component_message
from eve.utils import parse_request
from settings import CLIENT_OAUTH


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
    elif role == 'service' and sub == "LDEM":
        pass

    else:
        flask.abort(403, description='GET contract not allowed for '+role+' '+sub)


def store_pre_patch_contract_state(request):
    # 1) Fetch contract in current state
    doc = flask.current_app.data.find_one('contracts', parse_request('contracts'))
    if doc is not None:
        # 2) For all modified fields, fetch the previous state in the DB
        prev_state = {}
        for key in request.json:
            prev_state[key] = request.json[key]
            # 3) Store the previous state in current context to be retrieved in post_patch__contracts()
        flask.g.prev_patch_state = prev_state
    else:
        flask.g.prev_patch_state = {}


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
            store_pre_patch_contract_state(request)

        elif role == 'aggregator':
            request.json['validated'] = False
            lookup["agr_id"] = sub
            store_pre_patch_contract_state(request)

        elif role == 'service' and sub == 'OMP':
            pass

        # Todo: Remove temporary Sprint4 'admin' allowance to PATCH contracts
        elif role == 'admin' and CLIENT_OAUTH == 'fokus':
            store_pre_patch_contract_state(request)

        else:
            flask.abort(403, description='PATCH contract not allowed for ' + role + ' ' + sub)


def post_patch__contracts(request,payload):
    if payload.status_code == 200:
        prev_state = flask.g.prev_patch_state
        msg_type = None
        if request.role == 'aggregator':
            msg_type = 'AGGREGATOR_PATCH'
        elif request.role == 'prosumer':
            msg_type = 'PROSUMER_PATCH'
        # Todo: Remove temporary Sprint4 'admin' ICM to Marketplace
        elif request.role == 'admin':
            msg_type = 'ADMIN_PATCH'

        if msg_type is not None:
            send_inter_component_message(recipient='OMP', msg_type=msg_type,
                                         json_payload={'contract_id': request.view_args['contract_id'],
                                                       'patch': request.json,
                                                       'prev_state': prev_state})


def pre_post__contracts(request):
    if request.role != 'aggregator':
        flask.abort(403, description='POST contract not allowed for ' + request.role)

    if 'agr_id' in request.json and request.json['agr_id'] != request.account_id:
        flask.abort(403, description='POST contract agr_id mismatch')

    if 'contract_id' in request.json:
        id_check = {"contract_id": {"$eq": request.json['contract_id']}}
        cursor = flask.current_app.data.driver.db['contracts'].find(id_check)
        if cursor.count() > 0:
            flask.abort(409, 'contract_id already exists')

    if 'validated' in request.json:
        flask.abort(406, 'POST contains unauthorised validated field')


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
