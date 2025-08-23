import ujson
from rest_framework.renderers import JSONRenderer


class UJSONRenderer(JSONRenderer):
    """
    Renderer which serializes to JSON using ujson library.
    """

    media_type = "application/json"
    format = "json"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return bytes()

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = (",", ":")
        else:
            separators = (",", ": ")

        ret = ujson.dumps(
            data,
            ensure_ascii=self.ensure_ascii,
            indent=indent,
        )

        # On python 2.x ujson returns a string, not a bytestring.
        # In this case we need to encode the bytestring
        if isinstance(ret, str):
            return ret.encode(self.charset)
        return ret
