


class DatabaseOperationError(Exception):
    """Exception raised for errors in database operations."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LotNotFoundError(Exception):
    """Exception raised when a lot is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OrganisationNotFoundError(Exception):
    """Exception raised when an organisation is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ClientNotFoundError(Exception):
    """Exception raised when a client is not found."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class SaleNotFoundError(Exception):
    """Exception raised when a client is not found."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class SellerNotFoundError(Exception):
    """Exception raised when a client is not found."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

