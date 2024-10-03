class NoCardError(Exception):
    """Exception raised when given Card does not exist in the Deck."""
    pass


class NoProfileError(Exception):
    """Exception raised when given Profile does not exist for User."""
    pass


class DuplicateProfileError(Exception):
    """Exception raised when given Profile already exists for User"""
    pass


class NoCredentialsError(Exception):
    """Exception raised when given Credentials does not exist for Profile."""
    pass


class DuplicateServiceError(Exception):
    """Exception raised when given Service credentials already exists in Profile credentials list"""
    pass


class UsernameAlreadyExists(Exception):
    pass


class InvalidUsername(Exception):
    pass


class InvalidPassword(Exception):
    pass


class ValidationError(Exception):
    pass
