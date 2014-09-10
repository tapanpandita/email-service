'''Erros used throughout the app'''
class ValidationError(Exception):
    '''
    Error in request validation
    '''

    def __init__(self, field, message):
        self.field = field
        self.message = message
