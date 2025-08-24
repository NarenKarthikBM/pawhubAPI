import ujson
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser, BaseParser

class UJSONParser(JSONParser):
    """
    Parses JSON-serialized data using ujson library.
    """

    media_type = "application/json"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", "utf-8")

        try:
            decoded = stream.read().decode(encoding)
            return ujson.loads(decoded)
        except ValueError as exc:
            raise ParseError("JSON parse error - %s" % exc)


class OctetStreamParser(BaseParser):
    """
    Parses raw octet-stream (binary) files.
    """
    media_type = 'application/octet-stream'

    def parse(self, stream, media_type=None, parser_context=None):
        # Get filename from headers (optional)
        request = parser_context.get('request') if parser_context else None
        filename = request.headers.get('X-Filename', 'uploaded_file') if request else 'uploaded_file'
        from django.core.files.base import ContentFile
        return {'image_file': ContentFile(stream.read(), name=filename)}