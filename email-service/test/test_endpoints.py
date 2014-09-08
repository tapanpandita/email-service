import re
import json
import unittest

import responses

from app import app


class TestCases(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
        }
        self.minimum_required_email_payload = {
            'to': ['tapan.pandita@gmail.com'],
            'subject': 'Minimum paylod test',
            'text': 'This is the minimum required payload',
        }
        self.full_email_payload = {
            'from_email': 'test@tapandita.com',
            'from_name': 'Test client',
            'to': ['tapan.pandita@gmail.com', 'tapan.pandita+1@gmail.com'],
            'cc': ['tapan.pandita+2@gmail.com'],
            'bcc': ['tapan.pandita+3@gmail.com'],
            'subject': 'Full payload test',
            'text': 'This is the text',
            'html': 'This is <b>HTML</b>',
            'headers': {
                'test-header': 'test',
            }
        }
        self.incomplete_email_payload = {
        }
        self.sendgrid_url = 'https://api.sendgrid.com/api/mail.send.json'
        self.mailgun_url = 'https://api.mailgun.net/v2/tapandita.com/messages'

    def test_health_endpoint(self):
        response = self.client.get(
            '/health', headers={'accept': 'application/json'}
        )
        self.assertEquals(response.status_code, 200)

    def test_health_endpoint_when_client_doesnt_accept_json(self):
        response = self.client.get('/health', headers={'accept': 'text/html'})
        self.assertEquals(response.status_code, 406)

    def test_send_email_endpoint_when_client_doesnt_accept_json(self):
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.minimum_required_email_payload),
            headers={
                'content-type': 'application/json',
                'accept': 'text/html',
            },
        )
        self.assertEquals(response.status_code, 406)

    def test_send_email_endpoint_when_content_type_is_not_json(self):
        response = self.client.post(
            '/api/v1/emails/',
            data=self.minimum_required_email_payload,
        )
        self.assertEquals(response.status_code, 415)

    @responses.activate
    def test_send_email_endpoint_with_minimum_required_payload(self):
        responses.add(
            responses.POST, self.sendgrid_url,
            body='{"message":"success"}', status=200,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.minimum_required_email_payload),
            headers=self.headers,
        )
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_endpoint_with_full_payload(self):
        responses.add(
            responses.POST, self.sendgrid_url,
            body='{"message":"success"}', status=200,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.full_email_payload),
            headers=self.headers,
        )
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_endpoint_with_incomplete_payload(self):
        responses.add(
            responses.POST, self.sendgrid_url,
            body='{"message":"error"}', status=400,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.incomplete_email_payload),
            headers=self.headers,
        )
        self.assertEquals(response.status_code, 400)

    @responses.activate
    def test_send_email_when_sendgrid_fails_and_mailgun_works(self):
        responses.add(
            responses.POST, self.sendgrid_url,
            body='{"message":"error"}', status=500,
            content_type='application/json',
        )
        responses.add(
            responses.POST, self.mailgun_url,
            body='{"message":"success"}', status=200,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.minimum_required_email_payload),
            headers=self.headers,
        )
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_when_sendgrid_fails_and_mailgun_fails(self):
        responses.add(
            responses.POST, self.sendgrid_url,
            body='{"message":"error"}', status=500,
            content_type='application/json',
        )
        responses.add(
            responses.POST, self.mailgun_url,
            body='{"message":"success"}', status=500,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/emails/',
            data=json.dumps(self.minimum_required_email_payload),
            headers=self.headers,
        )
        self.assertEquals(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
