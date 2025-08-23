REST_FRAMEWORK = {
    # * Custom UJSON parser and renderer classes
    "DEFAULT_RENDERER_CLASSES": [
        "pawhubAPI.settings.custom_DRF_settings.renderers.UJSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "pawhubAPI.settings.custom_DRF_settings.parsers.UJSONParser",
    ],
    # * Custom authentication class
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "pawhubAPI.settings.custom_DRF_settings.authentication.UserTokenAuthentication",
    ],
}
