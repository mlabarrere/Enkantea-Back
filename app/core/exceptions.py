from typing import Any, Dict


class BaseAPIException(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.error_code, "message": self.message}


class AuthenticationError(BaseAPIException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class TokenError(BaseAPIException):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, "TOKEN_ERROR")


class UserNotFoundError(BaseAPIException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")


class InternalError(BaseAPIException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, "INTERNAL_ERROR")


class DatabaseOperationError(BaseAPIException):
    """Exception raised for errors in database operations."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_OPERATION_ERROR")


class LotNotFoundError(BaseAPIException):
    """Exception raised when a lot is not found."""

    def __init__(self, message: str = "Lot not found"):
        super().__init__(message, "LOT_NOT_FOUND")


class OrganisationNotFoundError(BaseAPIException):
    """Exception raised when an organisation is not found."""

    def __init__(self, message: str = "Organisation not found"):
        super().__init__(message, "ORGANISATION_NOT_FOUND")


class ClientNotFoundError(BaseAPIException):
    """Exception raised when a client is not found."""

    def __init__(self, message: str = "Client not found"):
        super().__init__(message, "CLIENT_NOT_FOUND")


class SaleNotFoundError(BaseAPIException):
    """Exception raised when a sale is not found."""

    def __init__(self, message: str = "Sale not found"):
        super().__init__(message, "SALE_NOT_FOUND")


class SellerNotFoundError(BaseAPIException):
    """Exception raised when a seller is not found."""

    def __init__(self, message: str = "Seller not found"):
        super().__init__(message, "SELLER_NOT_FOUND")


class PermissionDenied(BaseAPIException):
    """Exception raised when permission is denied."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED")


class NotFoundError(BaseAPIException):
    """Generic exception for resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class DuplicateValueException(BaseAPIException):
    """Exception raised when a duplicate value is encountered."""

    def __init__(self, message: str = "Duplicate value"):
        super().__init__(message, "DUPLICATE_VALUE")
