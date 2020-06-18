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
    aggregator_id = request.aggregator_id

    if role == 'prosumer':
        lookup["account_id"] = sub

    elif role == 'aggregator':
        lookup["aggregator_id"] = aggregator_id

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


def pre_patch__contracts(request, lookup):
    sub = request.account_id
    role = request.role
    aggregator_id = request.aggregator_id

    print('PATCH contract  request: ', request.json, 'by', role)

    has_error = False
    error_str = ""
    for entry in ['contract_id', 'start_date', 'end_date', 'aggregator_id', 'account_id',
                  'assets', 'contract_type']:
        if entry in request.json:
            error_str = error_str + entry+','
            has_error = True

    if role == 'service' and sub == 'OMP':
        # Open Marketplace can patch only 'validated', 'status' and 'details.date_of_signage'
        for key in request.json.keys():
            if key == 'validated':
                pass
            elif key == 'status' and request.json['status'] == 'canceled':
                pass
            elif key == 'details':
                for sub_key in request.json['details'].keys():
                    if sub_key != 'date_of_signage':
                        error_str = error_str + 'details.' + sub_key + ','
                        has_error = True
            else:
                error_str = error_str + key + ','
                has_error = True

    else:
        # Others can't patch 'validated'
        if 'validated' in request.json:
            error_str = error_str + 'validated'
            has_error = True

        if 'details' in request.json:
            # Details patches of 'description','notification' and 'date_of_signage' are restricted
            if 'description' in request.json['details'] and role != 'aggregator':
                error_str = error_str + 'details.description,'
                has_error = True
            if 'notification' in request.json['details'] and role != 'prosumer':
                error_str = error_str + 'details.notification,'
                has_error = True
            if 'date_of_signage' in request.json['details']:
                error_str = error_str + 'details.date_of_signage,'
                has_error = True

        # All patches from aggregator or prosumer require a 'timestamp' field
        if 'timestamp' not in request.json:
            error_str = error_str + ' missing timestamp'
            has_error = True

    if has_error:
        flask.abort(403, description='PATCH contract of ' + error_str + ' field(s) not allowed')

    else:
        if role == 'prosumer' or role == 'aggregator':
            query = {"contract_id": request.view_args['contract_id']}
            contract = flask.current_app.data.driver.db['contracts'].find_one(query)
            if contract and 'validated' in contract and not contract['validated']:
                flask.abort(409, description='PATCH of contract in state validated=False not allowed')

        if role == 'prosumer':
            lookup["account_id"] = sub

        elif role == 'aggregator':
            lookup["aggregator_id"] = aggregator_id

        elif role == 'service' and sub == 'OMP':
            pass

        # Todo: Remove temporary Sprint4 'admin' allowance to PATCH contracts
        elif role == 'admin':
            if 'status' in request.json and request.json['status'] == 'published':
                # Remove 'date_of_signage' when Admin reset contract back to 'published'
                query = {'contract_id': request.view_args['contract_id']}
                update = {'$unset': {'details.date_of_signage': ""}}
                flask.current_app.data.driver.db['contracts'].update_one(query, update)
        else:
            flask.abort(403, description='PATCH contract not allowed for ' + role + ' ' + sub)


def post_patch__contracts(request,payload):
    if payload.status_code == 200 and (request.role != 'service' or request.account_id != 'OMP'):
        send_inter_component_message(recipient='OMP', msg_type='PATCH_CONTRACT',
                                     json_payload={'contract_id': request.view_args['contract_id'],
                                                   'initiator_sub': request.account_id,
                                                   'initiator_role': request.role,
                                                   'initiator_issuer': request.aggregator_id,
                                                   'prev_state': flask.g.prev_patch_state,
                                                   'patch': request.json})


def pre_post__contracts(request):
    if request.role != 'aggregator':
        flask.abort(403, description='POST contract not allowed for ' + request.role)

    aggregator_id = request.aggregator_id

    if 'aggregator_id' in request.json:
        if request.json['aggregator_id'] != aggregator_id:
            flask.abort(403, description='POST contract aggregator_id mismatch')
        else:
            pass
    else:
        request.json['aggregator_id'] = aggregator_id

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


def update__contracts(updates, original):
    #print('update__contracts  upd=', updates)
    #print('update__contracts  org=', original)

    # 1) For all modified fields, copy the previous state from DB
    prev_state = {}
    for key in updates:
        if key == 'details':
            prev_state[key] = {}
            for d_key in updates['details']:
                if d_key in original['details']:
                    prev_state['details'][d_key] = original['details'][d_key]
        elif key[0] != '_' and key in original:
            prev_state[key] = original[key]
    if 'validated' not in updates and 'validated' in original:
        prev_state['validated'] = original['validated']
        updates['validated'] = False

    # 2) Store the previous state in current context to be retrieved in post_patch__contracts()
    flask.g.prev_patch_state = prev_state


def set_hooks(app):
    app.on_pre_GET_contracts += pre_get__contracts_callback
    app.on_pre_PATCH_contracts += pre_patch__contracts
    app.on_post_PATCH_contracts += post_patch__contracts
    app.on_pre_POST_contracts += pre_post__contracts
    app.on_post_POST_contracts += post_post__contracts
    app.on_pre_DELETE_contracts += pre_delete__contracts
    app.on_update_contracts += update__contracts
