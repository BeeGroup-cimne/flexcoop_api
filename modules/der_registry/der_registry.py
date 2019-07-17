

def pre_der_get_callback(request, lookup):
    print('A GET request on the contacts endpoint has just been received!')
    print(request)

    lookup["device_class"] = {'$eq': 'HVAC'}
    print(lookup)


