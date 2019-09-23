
def pre_der_get_callback(request, lookup):
    print('A GET request on the contacts endpoint has just been received!')
    print(request)

    # lookup operators come from mongoDB see https://docs.mongodb.com/manual/reference/operator/query/

    lookup["device_class"] = {'$eq': 'HVAC'}
    print(lookup)


