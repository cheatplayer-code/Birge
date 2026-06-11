"""Custom exception classes for the ML API layer."""


class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseError(APIError):
    """Exception for database-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ValidationError(APIError):
    """Exception for request validation errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(APIError):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=404)
