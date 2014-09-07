'''The email service flask app'''
import requests

from flask import Flask, request, jsonify

from decorators import consumes, produces
from mail.message import EmailMessage
from mail.exceptions import ClientException


app = Flask(__name__)
app.config.from_object('config.base')
app.config.from_envvar('EMAIL_SERVICE_SETTINGS')
app.requests_session = requests.Session()


@app.route('/health', methods=['GET'])
def health():
    '''Check the status of the service.'''
    return jsonify({'status': 'ok'})


@app.route('/api/v1/emails/', methods=['POST'])
@consumes('application/json')
@produces('application/json')
def send_email():
    '''
    Thin wrapper around sendgrid and mailgun apis. Sends emails provided
    email addresses.

    param str from_email: Email address from which the email is being sent
    param list to: Email addresses of recipients
    param list cc: Email addresses of recipients but cc
    param list bcc: Email addresses of recipients but bcc
    param str subject: Email subject
    param str text: Body of the email (text version).
    param str html: Body of the email (html version).
    param dict headers: Key/value pairs where each key represents the header
    name and the value represents the header value
    '''
    request_payload = request.get_json()
    message = EmailMessage(**request_payload)

    try:
        message.send()
    except ClientException, excp:
        status_code, error = excp
        return jsonify(error), status_code

    return jsonify({'message': 'success'})


if __name__ == '__main__':
    app.run(debug=True, port=7000)
