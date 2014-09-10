'''Email related Exceptions'''

class BaseEmailException(Exception):
    '''Base class for exceptions related to sending email'''

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


class ClientException(BaseEmailException):
    '''Error in data supplied to API, typically 4xx error'''


class ServerException(BaseEmailException):
    '''Error at remote server, typically 5xx error'''
