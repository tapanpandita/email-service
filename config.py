import os


#### FLASK CONFIG
SECRET_KEY = os.environ.get('SECRET_KEY')

#### EMAIL CONFIG
DEFAULT_FROM_EMAIL = 'support@tapandita.com'
DEFAULT_FROM_NAME = 'Tapan Pandita'

#### SENDGRID CONFIG
SENDGRID_HOST = 'https://api.sendgrid.com'
SENDGRID_USER = os.environ.get('SENDGRID_USER')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

#### MAILGUN CONFIG
MAILGUN_HOST = 'https://api.mailgun.net'
MAILGUN_USER = os.environ.get('MAILGUN_USER')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
