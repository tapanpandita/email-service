class BaseEmailException(Exception):
    '''Base class for exceptions related to sending email'''


class ClientException(BaseEmailException):
    '''Error in data supplied to API, 4xx error'''


class ServerException(BaseEmailException):
    '''Error at remote server, 5xx error'''
