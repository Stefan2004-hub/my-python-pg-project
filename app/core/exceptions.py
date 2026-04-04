"""Application-specific exceptions."""


class AppError(Exception):
    """Base application exception with HTTP response metadata."""

    def __init__(
        self,
        detail: str,
        status_code: int = 400,
        error_code: str = "application_error",
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(
            detail=detail,
            status_code=404,
            error_code="not_found",
        )


class DomainValidationError(AppError):
    """Raised when domain validation fails."""

    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(
            detail=detail,
            status_code=422,
            error_code="validation_error",
        )


class ServiceUnavailableError(AppError):
    """Raised when a required dependency is unavailable."""

    def __init__(self, detail: str = "Service unavailable") -> None:
        super().__init__(
            detail=detail,
            status_code=503,
            error_code="service_unavailable",
        )
