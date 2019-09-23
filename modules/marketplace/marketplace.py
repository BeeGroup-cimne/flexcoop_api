from jwt import JWT
from jwt.exceptions import JWTDecodeError

jwt = JWT()

def get_sub_and_role_from_request(request):
    sub = None
    role = None
    token = None
    if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
        token = request.headers['Authorization'].split(None, 1)[1].strip()
    elif 'Authorization' in request.headers:
        token = request.headers['Authorization']

    if 'access_token' in request.form:
        token = request.form['access_token']
    elif 'access_token' in request.args:
        token = request.args['access_token']

    if token is not None:
        try:
            claim = jwt.decode(token, do_verify=False)
            sub = claim['sub']
            role = claim['role']

        except JWTDecodeError as err:
            print('exception decoding token exc=', err)

    return sub, role


def pre_contract_GET_callback(request, lookup):
    print('A GET request on a Marketplace Contract endpoint has just been received!')
    print(request)

    sub, role = get_sub_and_role_from_request(request)

    if role is None:
        print('unknown role, query will produce empty result')
        lookup["prosumer_id"] = 'undefined'

    elif role == 'prosumer':
        print('limiting results to prosumer_id')
        lookup["prosumer_id"] = sub

    elif role == 'aggregator':
        print('limiting results to agr_id')
        lookup["agr_id"] = sub
