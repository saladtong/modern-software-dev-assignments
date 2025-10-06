from __future__ import annotations

from typing import Optional

from fastapi import HTTPException


class APIException(HTTPException):
    """Base API exception with standardized error handling."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class ValidationError(APIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class NotFoundError(APIException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            status_code=404,
            detail=f"{resource} not found",
            error_code="NOT_FOUND"
        )


class DatabaseError(APIException):
    """Raised when a database operation fails."""
    
    def __init__(self, operation: str, detail: str) -> None:
        super().__init__(
            status_code=500,
            detail=f"Database {operation} failed: {detail}",
            error_code="DATABASE_ERROR"
        )


class ExternalServiceError(APIException):
    """Raised when an external service (like LLM) fails."""
    
    def __init__(self, service: str, detail: str) -> None:
        super().__init__(
            status_code=502,
            detail=f"{service} service failed: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )


def handle_database_error(operation: str, error: Exception) -> None:
    """Standardized database error handling."""
    raise DatabaseError(operation, str(error))


def handle_validation_error(field: str, message: str) -> None:
    """Standardized validation error handling."""
    raise ValidationError(f"{field}: {message}")


def handle_not_found_error(resource: str, resource_id: str) -> None:
    """Standardized not found error handling."""
    raise NotFoundError(resource, resource_id)


def handle_external_service_error(service: str, error: Exception) -> None:
    """Standardized external service error handling."""
    raise ExternalServiceError(service, str(error))
