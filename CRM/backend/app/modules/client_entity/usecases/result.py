"""
Use Case Result
================
Common result object for use case operations.
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class UseCaseResult:
    """Result object for use case operations."""
    success: bool
    data: Any = None
    error: str = None
    error_code: str = None

    @classmethod
    def ok(cls, data: Any = None) -> 'UseCaseResult':
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str, error_code: str = 'ERROR') -> 'UseCaseResult':
        return cls(success=False, error=error, error_code=error_code)
