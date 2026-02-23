"""
Base Use Case Pattern
Use Cases contain application-specific business logic.
They orchestrate the flow of data between repositories and external services.
Each use case represents a single action/operation that can be performed.
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class UseCaseResult:
    """Standard result wrapper for use cases"""
    success: bool
    data: Any = None
    error: str = None
    error_code: str = None

    @classmethod
    def ok(cls, data: Any = None):
        """Create a successful result"""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str, error_code: str = None):
        """Create a failed result"""
        return cls(success=False, error=error, error_code=error_code)


class BaseUseCase(ABC):
    """
    Base use case class.
    All use cases should inherit from this class and implement the execute method.

    Use cases should:
    - Contain business logic
    - Coordinate between repositories
    - Return UseCaseResult
    - Not depend on HTTP/Flask specifics
    """

    @abstractmethod
    def execute(self, *args, **kwargs) -> UseCaseResult:
        """Execute the use case logic"""
        pass


class BaseQueryUseCase(BaseUseCase):
    """
    Base class for read-only use cases (queries).
    These should not modify any data.
    """
    pass


class BaseCommandUseCase(BaseUseCase):
    """
    Base class for write operations (commands).
    These modify data and should handle transactions.
    """
    pass
