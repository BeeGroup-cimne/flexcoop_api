from eve.io.mongo import MongoJSONEncoder
from eve.io.mongo import Validator
from uuid import UUID

class UUIDEncoder(MongoJSONEncoder):
    """ JSONEconder subclass used by the json render function.
    This is different from BaseJSONEoncoder since it also addresses
    encoding of UUID
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        else:
            # delegate rendering to base class method (the base class
            # will properly render ObjectIds, datetimes, etc.)
            return super(UUIDEncoder, self).default(obj)
            #return BaseJSONEncoder.default(self, obj)


class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """

    def _validate_type_uuid(self, value):
        try:
            UUID(value)
            return True
        except ValueError:
            #return False
            pass

