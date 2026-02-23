"""
Base Service Pattern
Services handle domain-specific operations and external integrations.
They are reusable components that can be used across multiple use cases.
"""
from abc import ABC
from typing import Any


class BaseService(ABC):
    """
    Base service class.
    Services should:
    - Handle domain-specific operations
    - Integrate with external systems
    - Be stateless and reusable
    - Not contain application flow logic (that's for use cases)
    """
    pass


class BaseDomainService(BaseService):
    """
    Domain services handle complex business logic that spans multiple entities
    or doesn't naturally fit within a single entity.
    """
    pass


class BaseIntegrationService(BaseService):
    """
    Integration services handle communication with external systems
    like email providers, storage services, payment gateways, etc.
    """
    pass
