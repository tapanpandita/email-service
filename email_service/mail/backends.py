from urlparse import urljoin

import requests
from requests.exceptions import ConnectionError

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
    '''Implements an email backend that uses sendgrid to send emails'''

    name = 'sendgrid'

    def __init__(self, host=None, api_user=None, api_key=None,
                 requests_session=None):
        '''Initialises with sendgrid config'''
        self.host = host or app.config['SENDGRID_HOST']
        self.api_user = api_user or app.config['SENDGRID_USER']
        self.api_key = api_key or app.config['SENDGRID_API_KEY']
        self.requests_session = requests_session or requests.Session()
        self.api_urls = {
            'send_email': '/api/mail.send.json'
        }

    def _create_payload(self, message):
        '''Creates payload conforming to the sendgrid api'''
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

    def _make_request(self, url, payload=None, headers=None, auth=None):
        '''Makes post requests with provided params'''
        payload = payload or {}
        headers = headers or {}
        auth = auth or ()

        try:
            response = self.requests_session.post(
                url, data=payload, headers=headers, auth=auth,
            )
        except ConnectionError:
            raise ServerException(500, {})

        return response

    def _send(self, message):
        '''Helper method that does the actual sending'''
        payload = self._create_payload(message)
        url = urljoin(self.host, self.api_urls.get('send_email'))
        response = self._make_request(
            url, payload=payload,
        )

        if response.status_code >= 500:
            raise ServerException(response.status_code, {})
        elif response.status_code >= 400:
            raise ClientException(response.status_code, response.json())

        return response

    def send_messages(self, email_messages):
        '''
        Sends one or more EmailMessage objects and returns the number of email
        messages sent
        '''

        if not email_messages:
            return

        num_sent = 0

        for message in email_messages:
            sent = self._send(message)

            if sent:
                num_sent += 1

        return num_sent


class MailgunBackend(BaseEmailBackend):
    '''Implements an email backend that uses mailgun to send emails'''

    name = 'mailgun'

    def __init__(self, host=None, api_user=None, api_key=None,
                 requests_session=None, domain=None):
        '''Initialises with mailgun config'''
        self.host = host or app.config['MAILGUN_HOST']
        self.api_user = api_user or app.config['MAILGUN_USER']
        self.api_key = api_key or app.config['MAILGUN_API_KEY']
        self.requests_session = requests_session or requests.Session()
        self.domain = domain or app.config['EMAIL_DOMAIN']
        self.api_urls = {
            'send_email': '/v2/{domain}/messages'.format(
                domain=self.domain,
            ),
        }

    def _create_payload(self, message):
        '''Creates payload conforming to the mailgun api'''
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

    def _make_request(self, url, payload=None, headers=None, auth=None):
        '''Makes post requests with provided params'''
        payload = payload or {}
        headers = headers or {}
        auth = auth or ()

        try:
            response = self.requests_session.post(
                url, data=payload, headers=headers, auth=auth,
            )
        except ConnectionError:
            raise ServerException(500, {})

        return response

    def _send(self, message):
        '''Helper method that does the actual sending'''
        payload = self._create_payload(message)
        url = urljoin(self.host, self.api_urls.get('send_email'))
        auth = (self.api_user, self.api_key)
        response = self._make_request(
            url, payload=payload, auth=auth,
        )

        if response.status_code == 400:
            raise ClientException(response.status_code, response.json())
        elif response.status_code in [401, 402, 404]:
            raise ServerException(response.status_code, {})
        elif response.status_code >= 500:
            raise ServerException(response.status_code, {})

        return response

    def send_messages(self, email_messages):
        '''
        Sends one or more EmailMessage objects and returns the number of email
        messages sent
        '''

        if not email_messages:
            return

        num_sent = 0

        for message in email_messages:
            sent = self._send(message)

            if sent:
                num_sent += 1

        return num_sent
