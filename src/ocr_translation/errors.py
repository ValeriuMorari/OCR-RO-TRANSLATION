class AppError(Exception):
    """Base class for user-facing application errors."""


class DependencyMissingError(AppError):
    """Raised when an optional runtime dependency is not installed."""


class UnsupportedFileError(AppError):
    """Raised when the input file type is not supported."""
