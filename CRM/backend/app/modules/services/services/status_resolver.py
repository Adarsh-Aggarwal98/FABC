"""
Status Resolver Service
========================
Provides dynamic status resolution for requests and tasks.
Company-specific statuses take precedence over system defaults.
"""

from typing import List, Optional, Tuple
from app.modules.services.models.status_models import SystemRequestStatus, CompanyRequestStatus


class StatusResolver:
    """Resolves valid statuses for a company, with system fallback."""

    @staticmethod
    def get_statuses(company_id: str, category: str = None) -> list:
        """
        Get statuses for a company. Company custom statuses take priority;
        falls back to system defaults if no custom statuses exist.

        Args:
            company_id: The company ID
            category: Optional filter - 'request', 'task', or 'both'

        Returns:
            List of status dicts
        """
        # Check for company custom statuses first
        query = CompanyRequestStatus.query.filter_by(
            company_id=company_id,
            is_active=True
        )
        has_custom = query.first() is not None

        if has_custom:
            query = CompanyRequestStatus.query.filter_by(
                company_id=company_id,
                is_active=True
            )
            if category:
                query = query.filter(
                    (CompanyRequestStatus.category == category) |
                    (CompanyRequestStatus.category == 'both')
                )
            statuses = query.order_by(CompanyRequestStatus.position).all()
        else:
            query = SystemRequestStatus.query.filter_by(is_active=True)
            if category:
                query = query.filter(
                    (SystemRequestStatus.category == category) |
                    (SystemRequestStatus.category == 'both')
                )
            statuses = query.order_by(SystemRequestStatus.position).all()

        return statuses

    @staticmethod
    def get_valid_keys(company_id: str, category: str = None) -> List[str]:
        """
        Get just the status keys valid for a company.

        Args:
            company_id: The company ID
            category: Optional filter - 'request', 'task', or 'both'

        Returns:
            List of valid status key strings
        """
        statuses = StatusResolver.get_statuses(company_id, category)
        return [s.status_key for s in statuses]

    @staticmethod
    def get_default_status(company_id: str, category: str = 'both') -> Optional[str]:
        """
        Get the default status key for new items.

        Args:
            company_id: The company ID
            category: 'request', 'task', or 'both'

        Returns:
            Default status key string, or 'pending' as ultimate fallback
        """
        # Check company statuses first
        query = CompanyRequestStatus.query.filter_by(
            company_id=company_id,
            is_active=True,
            is_default=True
        )
        if category:
            query = query.filter(
                (CompanyRequestStatus.category == category) |
                (CompanyRequestStatus.category == 'both')
            )
        status = query.first()

        if status:
            return status.status_key

        # Fallback to system default
        query = SystemRequestStatus.query.filter_by(
            is_active=True,
            is_default=True
        )
        if category:
            query = query.filter(
                (SystemRequestStatus.category == category) |
                (SystemRequestStatus.category == 'both')
            )
        status = query.first()

        return status.status_key if status else 'pending'

    @staticmethod
    def is_final_status(company_id: str, status_key: str) -> bool:
        """
        Check if a status is a final status (completed/cancelled).

        Args:
            company_id: The company ID
            status_key: The status key to check

        Returns:
            True if the status is final
        """
        # Check company statuses first
        status = CompanyRequestStatus.query.filter_by(
            company_id=company_id,
            status_key=status_key,
            is_active=True
        ).first()

        if status:
            return status.is_final

        # Fallback to system
        status = SystemRequestStatus.query.filter_by(
            status_key=status_key,
            is_active=True
        ).first()

        return status.is_final if status else False


class TransitionResolver:
    """Resolves allowed status transitions for a company."""

    @staticmethod
    def get_allowed_transitions(company_id: str, from_status: str, user_role: str) -> List[str]:
        """
        Get allowed target statuses for a transition.

        Args:
            company_id: The company ID
            from_status: Current status key
            user_role: Role of the user attempting the transition

        Returns:
            List of allowed target status keys
        """
        from app.modules.services.models.status_transition import StatusTransition

        # Check company-specific transitions first
        transitions = StatusTransition.query.filter_by(
            from_status_key=from_status,
            company_id=company_id
        ).all()

        # Fallback to system defaults
        if not transitions:
            transitions = StatusTransition.query.filter_by(
                from_status_key=from_status,
                company_id=None
            ).all()

        # If no transitions defined at all, allow all (permissive fallback)
        if not transitions:
            return StatusResolver.get_valid_keys(company_id)

        # Filter by role
        allowed = []
        for t in transitions:
            if t.allowed_roles is None:
                allowed.append(t.to_status_key)
            elif user_role in t.allowed_roles:
                allowed.append(t.to_status_key)

        return allowed

    @staticmethod
    def validate_transition(
        company_id: str,
        from_status: str,
        to_status: str,
        user_role: str
    ) -> Tuple[bool, bool]:
        """
        Validate whether a status transition is allowed.

        Args:
            company_id: The company ID
            from_status: Current status key
            to_status: Target status key
            user_role: Role of the user

        Returns:
            Tuple of (allowed: bool, requires_note: bool)
        """
        from app.modules.services.models.status_transition import StatusTransition

        # Check company-specific transition first
        transition = StatusTransition.query.filter_by(
            from_status_key=from_status,
            to_status_key=to_status,
            company_id=company_id
        ).first()

        # Fallback to system default
        if not transition:
            transition = StatusTransition.query.filter_by(
                from_status_key=from_status,
                to_status_key=to_status,
                company_id=None
            ).first()

        # No transition rule defined = allow (permissive)
        if not transition:
            # Check if ANY transitions are defined for this from_status
            has_rules = StatusTransition.query.filter_by(
                from_status_key=from_status,
                company_id=company_id
            ).first() or StatusTransition.query.filter_by(
                from_status_key=from_status,
                company_id=None
            ).first()

            if not has_rules:
                return (True, False)  # No rules = allow all
            else:
                return (False, False)  # Rules exist but this transition isn't in them

        # Check role
        if transition.allowed_roles and user_role not in transition.allowed_roles:
            return (False, False)

        return (True, transition.requires_note or False)
