from urlparse import urljoin

import requests

from flask import current_app as app

from .exceptions import ClientException, ServerException


class BaseEmailBackend(object):
    '''
    Base class for email backend implementations.

    Subclasses must overwrite send_message().
    '''

    def __init__(self, **kwargs):
        pass

    def send_messages(self, email_messages):
        '''
        Sends one or more EmailMessage objects and returns the number of email
        messages sent
        '''
        raise NotImplementedError(
            'Subclasses of BaseEmailBackend must override send_message() method'
        )


class SendgridBackend(BaseEmailBackend):

    def __init__(self, host=None, api_user=None, api_key=None,
                 requests_session=None):
        self.host = host or app.config['SENDGRID_HOST']
        self.api_user = api_user or app.config['SENDGRID_USER']
        self.api_key = api_key or app.config['SENDGRID_API_KEY']
        self.requests_session = requests_session or requests.Session()
        self.api_urls = {
            'send_email': '/api/mail.send.json'
        }

    def _create_payload(self, message):
        payload = {
            'api_user': self.api_user,
            'api_key': self.api_key,
            'from': message.from_email,
            'fromname': message.from_name,
            'to': message.to,
            'cc': message.cc,
            'bcc': message.bcc,
            'subject': message.subject,
            'text': message.text,
            'html': message.html,
            'headers': message.headers,
        }

        return payload

    def _send(self, message):
        payload = self._create_payload(message)
        url = urljoin(self.host, self.api_urls.get('send_email'))
        raise ServerException(500, {})
        response = self.requests_session.post(
            url, data=payload,
        )

        if response.status_code == 400:
            raise ClientException(response.status_code, response.json())
        elif response.status_code >= 500:
            raise ServerException(response.status_code, response.json())

        return response

    def send_messages(self, email_messages):

        if not email_messages:
            return

        num_sent = 0

        for message in email_messages:
            sent = self._send(message)

            if sent:
                num_sent += 1

        return num_sent


class MailgunBackend(BaseEmailBackend):

    def __init__(self, host=None, api_user=None, api_key=None,
                 requests_session=None):
        self.host = host or app.config['MAILGUN_HOST']
        self.api_user = api_user or app.config['MAILGUN_USER']
        self.api_key = api_key or app.config['MAILGUN_API_KEY']
        self.requests_session = requests_session or requests.Session()
        self.api_urls = {
            'send_email': '/v2/{domain}/messages'.format(
                domain='tapandita.com',
            ),
        }

    def _create_payload(self, message):
        payload = {
            'from': '{from_name} <{from_email}>'.format(
                from_name=message.from_name, from_email=message.from_email,
            ),
            'to': ','.join(message.to),
            'subject': message.subject,
            'text': message.text,
            'html': message.html,
        }

        if message.cc:
            payload['cc'] = ','.join(message.cc)

        if message.bcc:
            payload['bcc'] = ','.join(message.bcc)

        for header, value in message.headers.items():
            payload['h:{header}'.format(header=header)] = value

        return payload

    def _send(self, message):
        payload = self._create_payload(message)
        url = urljoin(self.host, self.api_urls.get('send_email'))
        auth = (self.api_user, self.api_key)
        response = self.requests_session.post(
            url, data=payload, auth=auth,
        )

        if response.status_code == 400:
            raise ClientException(response.status_code, response.json())
        elif response.status_code >= 500:
            raise ServerException(response.status_code, response.json())

        return response

    def send_messages(self, email_messages):

        if not email_messages:
            return

        num_sent = 0

        for message in email_messages:
            sent = self._send(message)

            if sent:
                num_sent += 1

        return num_sent
