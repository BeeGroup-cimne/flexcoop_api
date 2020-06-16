from eve.render import JSONRenderer
from flask import request, current_app as app
import simplejson as json
from eve.utils import (
    config,
)

class NaNJSONRenderer(JSONRenderer):
    """ JSON renderer class based on `simplejson` package.

    """

    mime = ("application/json",)

    def render(self, data):
        """ JSON render function

        :param data: the data stream to be rendered as json.

        .. versionchanged:: 0.2
           Json encoder class is now inferred by the active data layer,
           allowing for customized, data-aware JSON encoding.

        .. versionchanged:: 0.1.0
           Support for optional HATEOAS.
        """
        set_indent = None

        # make pretty prints available
        if "GET" in request.method and "pretty" in request.args:
            set_indent = 4
        return json.dumps(
            data,
            indent=set_indent,
            cls=app.data.json_encoder_class,
            sort_keys=config.JSON_SORT_KEYS,
            ignore_nan=True,
        )
