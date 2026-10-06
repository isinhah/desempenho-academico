"""Exceções de domínio expostas pela aplicação."""

from app.exceptions.application_exception import (
    ApplicationException,
    BusinessRuleException,
    ConflictException,
    DatabaseUnavailableException,
    ResourceNotFoundException,
)

__all__ = [
    "ApplicationException",
    "BusinessRuleException",
    "ConflictException",
    "DatabaseUnavailableException",
    "ResourceNotFoundException",
]
