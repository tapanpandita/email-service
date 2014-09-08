email_api_schema = {
    'type': 'object',
    'properties': {
        'to': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'email',
            },
            'minItems': 1,
        },
        'from_email': {'type': 'string', 'format': 'email'},
        'from_name': {'type': 'string'},
        'cc': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'email',
            },
            'minItems': 1,
        },
        'bcc': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'email',
            },
            'minItems': 1,
        },
        'subject': {'type': 'string', 'minLength': 1},
        'text': {'type': 'string', 'minLength': 1},
        'html': {'type': 'string', 'minLength': 1},
    },
    'anyOf': [
        {'required': ['to', 'subject', 'text']},
        {'required': ['to', 'subject', 'html']}
    ]
}
