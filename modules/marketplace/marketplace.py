def pre_contract_get_callback(request, lookup):
    print('A GET request on the contacts endpoint has just been received!')
    print(request)

    lookup["status"] = {'$eq': 'active'}
    print(lookup)
