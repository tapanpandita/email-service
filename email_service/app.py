'''The email service flask app'''
import requests

from flask import Flask, request, jsonify

from decorators import consumes, produces, json_validate
from schemas import email_api_schema
from errors import ValidationError
from mail.message import EmailMessage
from mail.exceptions import ClientException


app = Flask(__name__)
app.config.from_object('config.base')
app.config.from_envvar('EMAIL_SERVICE_SETTINGS')
app.requests_session = requests.Session()


@app.route('/api/v1/health', methods=['GET'])
@produces('application/json')
def health():
    '''Check the status of the service.'''
    return jsonify({'status': 'ok'})


@app.route('/api/v1/emails', methods=['POST'])
@consumes('application/json')
@produces('application/json')
@json_validate(email_api_schema)
def send_email():
    '''
    Thin wrapper around sendgrid and mailgun apis. Sends emails to provided
    email addresses.
    '''
    request_payload = request.get_json()

    message = EmailMessage(**request_payload)

    try:
        is_sent, backend = message.send()
    except ClientException, excp:
        status_code, error = excp
        return jsonify(error), status_code

    if not is_sent:
        return jsonify({'message': 'error'}), 502

    return jsonify({'message': 'success', 'backend': backend.name})


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    '''
    Returns a 400 response with error message when validation error is raised.
    '''
    status_code = 400
    message = error.message
    field = error.field

    payload = {
        'message': 'error',
        'error': {
            'field': field,
            'message': message,
        }
    }

    return jsonify(payload), status_code


if __name__ == '__main__':
    app.run(debug=True, port=7000)
