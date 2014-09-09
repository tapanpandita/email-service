Email Service
=============

The email service is a simple Python/Flask service which is a thin wrapper around sendgrid and mailgun APIs. It seamlessly transitions over from one provider to the other in case one stops responding.


Using the service
-----------------

1. Create accounts on sendgrid and mailgun and get your username and API keys.
2. Fill in the relevant information in config/base.py. Export your sendgrid and mailgun credentials as environment variables.
```
export SENDGRID_USER="YOUR_SENDGRID_USER" && export SENDGRID_API_KEY="YOUR_SENDGRID_API_KEY"
export MAILGUN_USER="YOUR_MAILGUN_USER" && export MAILGUN_API_KEY="YOUR_MAILGUN_API_KEY"
```
3. Install all dependencies using:
```
pip install -r requirements.txt
```
4. Run `python app.py`. The service should now be available on port 7000.


Testing
-------

1. Install test dependencies with `pip install -r requirements/ci.txt`
2. Run tests with `nosetests test`


API spec
--------

* GET /api/v1/health

Response:

Status Code: 200 OK

Content-Type: application/json

Body:
```javascript
{
  "status": "ok"
}
```
* POST /api/v1/emails

Request:

Content-Type: application/json

Body:
```javascript
{
  "to":[
    "tapan.pandita@gmail.com",
    "tapan.pandita+1@gmail.com"
  ],
  "subject":"Full payload test",
  "text":"This is the text",
  "html":"This is <b>HTML</b>",
  "cc":[
    "tapan.pandita+2@gmail.com"
  ], //optional
  "bcc":[
    "tapan.pandita+3@gmail.com"
  ], //optional
  "from_name":"Test client", //optional
  "from_email":"test@tapandita.com" //optional
}
// One of text or html is required
```
Responses:

Email sent successfully

Status Code: 200 OK

Content-Type: application/json

Body:
```javascript
{
  "backend": "sendgrid",  // or "mailgun"
  "message": "success"
}
```
Reuest payload is invalid

Status Code: 400 Bad Request

Body:
```javascript
{
  "error": {
    "field": "subject",
    "message": "'' is too short"
  },
  "message": "error"
}
```
Could not send email

Status Code: 502 Bad Gateway

Body:
```javascript
{
  "message": "error"
}
```

TODOs
-----
1. Adding authentication on APIs
2. Better error messages if request payload is invalid (especially for the case when all required fields are not present)
3. Adding support for attachments and custom headers
4. Adding unit tests for the mail package
5. Using a better tool than jsonschema for api validation. Jsonschema doesn't seem extendable.
