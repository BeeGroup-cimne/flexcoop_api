
from jwt import JWT

jwt = JWT()

def pre_der_get_callback(request, lookup):
    print('A GET request on a DER  endpoint has just been received!')
    print(request)

    sub = None
    role = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']

        try:
            claim = jwt.decode(token, do_verify=False)
            sub = claim['sub']
            role = claim['role']

        except jwt.exceptions.DecodeError as err:
            print('exception decoding token exc=', err)

    if role is None:
        lookup["account_id"] = 'undefined'

    elif role == 'prosumer':
        lookup["account_id"] = sub

    # lookup["device_class"] = {'$eq': 'HVAC'}
    # print(lookup)


