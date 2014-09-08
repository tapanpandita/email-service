'''Misc utility functions that can be used throughout the app'''
from functools import wraps

import jsonschema

from flask import request
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable


def consumes(*content_types):
    '''
    Validates if incoming request has an accepted content-type. Raises
    UnsupportedMediaType if requirements are not satisfied.
    '''

    def decorated(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            if request.mimetype not in content_types:
                raise UnsupportedMediaType()

            return fn(*args, **kwargs)

        return wrapper

    return decorated


def produces(*content_types):
    '''
    Checks if client accepts generated response content type. Raises
    NotAcceptable if requirements aren't satisfied.
    '''

    def decorated(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            requested = set(request.accept_mimetypes.values())
            defined = set(content_types)

            if len(requested & defined) == 0:
                raise NotAcceptable()

            return fn(*args, **kwargs)

        return wrapper

    return decorated


def json_validate(schema):
    '''
    Validates if incoming request is valid json and satisfies the given schema.
    Raises ValidationError if requirements are not satisfied.
    '''

    def decorated(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            request_payload = request.get_json(silent=True)

            if request_payload is None:
                raise ValidationError('request', 'Not a valid json')

            try:
                jsonschema.validate(
                    request_payload, schema,
                    format_checker=jsonschema.FormatChecker(),
                )
            except jsonschema.ValidationError, excp:
                invalid_field = excp.path[0]
                error_message = excp.message
                raise ValidationError(invalid_field, error_message)

            return fn(*args, **kwargs)

        return wrapper

    return decorated
