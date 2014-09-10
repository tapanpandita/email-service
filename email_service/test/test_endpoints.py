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
        self.incorrect_email_payload = {
            'to': ['tapan.pandita@'],
            'subject': 'Incorrect payload test',
            'text': 'This is an incorrect payload that passes jsonschema '
            'validation',
        }
        self.incomplete_email_payload = {
        }
        self.sendgrid_url = 'https://api.sendgrid.com/api/mail.send.json'
        self.mailgun_url = 'https://api.mailgun.net/v2/tapandita.com/messages'

    def mock_json_response_for_post(self, url, response_code, response_body):
        '''
        Mocks responses for post requests
        '''
        responses.add(
            responses.POST, url,
            body=json.dumps(response_body), status=response_code,
            content_type='application/json',
        )

    def mock_sendgrid_response(self, response_code, response_body):
        '''
        Mocks responses from the sendgrid api
        '''
        self.mock_json_response_for_post(
            self.sendgrid_url, response_code, response_body,
        )

    def mock_mailgun_response(self, response_code, response_body):
        '''
        Mocks responses from the mailgun api
        '''
        self.mock_json_response_for_post(
            self.mailgun_url, response_code, response_body,
        )

    def make_health_request(self, headers=None):
        '''
        Makes api requests to the health endpoint
        '''

        if not headers:
            headers = self.headers

        response = self.client.get(
            '/api/v1/health', headers=headers,
        )
        return response

    def make_send_email_request(self, payload, headers=None):
        '''
        Makes api requests to the send email endpoint
        '''

        if not headers:
            headers = self.headers

        response = self.client.post(
            '/api/v1/emails', data=json.dumps(payload), headers=headers,
        )
        return response

    def test_health_endpoint(self):
        '''
        Assert that the health endpoint works
        '''
        response = self.make_health_request()
        self.assertEquals(response.status_code, 200)

    def test_health_endpoint_when_client_doesnt_accept_json(self):
        '''
        Assert that the health endpoint returns NotAcceptable, 406,
        When client doesn't accept json
        '''
        response = self.make_health_request(headers={'accept': 'text/html'})
        self.assertEquals(response.status_code, 406)

    def test_send_email_endpoint_when_client_doesnt_accept_json(self):
        '''
        Assert that the send email endpoint returns NotAcceptable, 406,
        When client doesn't accept json
        '''
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
            headers={
                'content-type': 'application/json',
                'accept': 'text/html',
            },
        )
        self.assertEquals(response.status_code, 406)

    def test_send_email_endpoint_when_content_type_is_not_json(self):
        '''
        Assert that the send email endpoint returns UnsupportedMediaTyep, 415,
        When content-type is not json
        '''
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
            headers={
                'content-type': 'application/x-www-form-urlencoded',
            }
        )
        self.assertEquals(response.status_code, 415)

    @responses.activate
    def test_send_email_endpoint_with_valid_payload(self):
        '''
        Assert that the send email endpoint returns 200 OK
        When sendgrid sends email successfully
        '''
        self.mock_sendgrid_response(200, {'message': 'success'})
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
        )
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_endpoint_uses_correct_backend_with_valid_payload(self):
        '''
        Assert that the send email endpoint returns correct backend,
        When sendgrid sends email successfully
        '''
        self.mock_sendgrid_response(200, {'message': 'success'})
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
        )
        self.assertEquals(json.loads(response.data).get('backend'), 'sendgrid')

    @responses.activate
    def test_send_email_endpoint_with_full_payload(self):
        '''
        Assert that the send email endpoint works,
        When the full payload is posted
        '''
        self.mock_sendgrid_response(200, {'message': 'success'})
        response = self.make_send_email_request(self.full_email_payload)
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_endpoint_uses_correct_backend_with_full_payload(self):
        '''
        Assert that the send email endpoint returns correct backend,
        When the full payload is posted
        '''
        self.mock_sendgrid_response(200, {'message': 'success'})
        response = self.make_send_email_request(self.full_email_payload)
        self.assertEquals(json.loads(response.data).get('backend'), 'sendgrid')

    @responses.activate
    def test_send_email_endpoint_with_incomplete_payload(self):
        '''
        Assert that the send email endpoint returns BadResponse, 400,
        When an incomplete payload is posted
        '''
        response = self.make_send_email_request(self.incomplete_email_payload)
        self.assertEquals(response.status_code, 400)

    @responses.activate
    def test_send_email_endpoint_with_incorrect_payload(self):
        '''
        Assert that the send email endpoint returns BadResponse, 400,
        When an incorrect payload is posted
        '''
        self.mock_sendgrid_response(400, {'message': 'error'})
        response = self.make_send_email_request(self.incorrect_email_payload)
        self.assertEquals(response.status_code, 400)

    @responses.activate
    def test_send_email_works_when_sendgrid_fails_and_mailgun_works(self):
        '''
        Assert that the send email endpoint works,
        When sendgrid is down
        '''
        self.mock_sendgrid_response(500, {'message': 'error'})
        self.mock_mailgun_response(200, {'message': 'success'})
        response = self.make_send_email_request(self.full_email_payload)
        self.assertEquals(response.status_code, 200)

    @responses.activate
    def test_send_email_uses_correct_backend_when_sendgrid_is_down(self):
        '''
        Assert that the send email endpoint works with the correct backend,
        When sendgrid is down and mailgun works
        '''
        self.mock_sendgrid_response(500, {'message': 'error'})
        self.mock_mailgun_response(200, {'message': 'success'})
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
        )
        self.assertEquals(json.loads(response.data).get('backend'), 'mailgun')

    @responses.activate
    def test_send_email_when_sendgrid_fails_and_payload_is_incorrect(self):
        '''
        Assert that send email endpoint returns BadResponse, 400,
        When sendgrid is down and an incorrect payload is posted
        '''
        self.mock_sendgrid_response(500, {'message': 'error'})
        self.mock_mailgun_response(400, {'message': 'error'})
        response = self.make_send_email_request(self.incorrect_email_payload)
        self.assertEquals(response.status_code, 400)

    @responses.activate
    def test_send_email_when_sendgrid_fails_authentication_fails(self):
        '''
        Assert that send email endpoint fails with BadGateway, 502,
        When sendgrid is down and mailgun authentication fails
        '''
        self.mock_sendgrid_response(500, {'message': 'error'})
        self.mock_mailgun_response(401, {'message': 'error'})
        response = self.make_send_email_request(self.incorrect_email_payload)
        self.assertEquals(response.status_code, 400)

    @responses.activate
    def test_send_email_when_sendgrid_fails_and_mailgun_fails(self):
        '''
        Assert that sending email fails with BadGateway, 502,
        When sendgrid and mailgun are down
        '''
        self.mock_sendgrid_response(500, {'message': 'error'})
        self.mock_mailgun_response(500, {'message': 'error'})
        response = self.make_send_email_request(
            self.minimum_required_email_payload,
        )
        self.assertEquals(response.status_code, 502)


if __name__ == '__main__':
    unittest.main()
