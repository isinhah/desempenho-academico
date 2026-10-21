"""Exceções de domínio expostas pela aplicação."""

from app.exceptions.application_exception import (
    ApplicationException,
    DatabaseUnavailableException,
    ResourceNotFoundException,
)

__all__ = [
    "ApplicationException",
    "DatabaseUnavailableException",
    "ResourceNotFoundException",
]
