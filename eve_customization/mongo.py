# -*- coding: utf-8 -*-

"""
    eve.io.mongo.mongo (eve.io.mongo)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import simplejson as json

from eve.io.mongo.mongo import Mongo
from werkzeug.exceptions import HTTPException

class Mongo1(Mongo):
    def find(self, resource, req, sub_resource_lookup, perform_count=True):
        spec = self._convert_where_request_to_dict(req)
        if 'device_class' in spec:
            value = spec.pop("device_class")
            spec['rid'] = value
        req.where = json.dumps(spec)
        return super(Mongo1, self).find(resource, req, sub_resource_lookup, perform_count=True)
