class APIException(Exception):
    """Base exception for API errors"""
    status_code = 500
    message = 'An unexpected error occurred'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIException):
    """Raised when input validation fails"""
    status_code = 400
    message = 'Validation error'


class AuthenticationError(APIException):
    """Raised when authentication fails"""
    status_code = 401
    message = 'Authentication failed'


class AuthorizationError(APIException):
    """Raised when user lacks permission"""
    status_code = 403
    message = 'Access denied'


class NotFoundError(APIException):
    """Raised when a resource is not found"""
    status_code = 404
    message = 'Resource not found'


class ConflictError(APIException):
    """Raised when there's a conflict (e.g., duplicate entry)"""
    status_code = 409
    message = 'Resource already exists'
