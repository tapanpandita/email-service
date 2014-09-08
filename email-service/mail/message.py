from flask import current_app as app

from .exceptions import ServerException
from .backends import SendgridBackend, MailgunBackend


class EmailMessage(object):
    '''
    Container for email information. Uses first of multiple email backends to
    send email.
    '''
    backends = [
        SendgridBackend,
        MailgunBackend,
    ]

    def __init__(self, to, from_email=None, from_name=None, cc=None, bcc=None,
                 subject='', text='', html='', headers=None):
        '''Initializes an email message object with provided details'''
        self.to = to
        self.from_email = from_email or app.config['DEFAULT_FROM_EMAIL']
        self.from_name = from_name or app.config['DEFAULT_FROM_NAME']
        self.cc = cc or []
        self.bcc = bcc or []
        self.subject = subject
        self.text = text
        self.html = html
        self.headers = headers or {}

    def send(self):
        '''Sends the email message using the first backend that works'''
        is_sent = False

        for backend in self.backends:

            try:
                backend().send_messages([self])
                is_sent = True
                return is_sent, backend
            except ServerException:
                continue

        return is_sent, None
