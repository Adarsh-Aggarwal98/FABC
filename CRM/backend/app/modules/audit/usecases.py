"""
Audit module use cases
"""
from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token
from app.common.usecase import BaseQueryUseCase, BaseCommandUseCase, UseCaseResult
from app.extensions import db
from .repositories import ActivityLogRepository
from app.modules.audit.models.audit_log import ImpersonationSession, ActivityLog


class GetEntityActivityUseCase(BaseQueryUseCase):
    """Get activity timeline for a specific entity"""

    def __init__(self):
        self.activity_repo = ActivityLogRepository()

    def execute(self, entity_type: str, entity_id: str, limit: int = 50) -> UseCaseResult:
        activities = self.activity_repo.get_by_entity(entity_type, entity_id, limit)
        return UseCaseResult.ok({
            'activities': [a.to_dict() for a in activities]
        })


class GetUserActivityUseCase(BaseQueryUseCase):
    """Get activity timeline for a user (actions performed on them)"""

    def __init__(self):
        self.activity_repo = ActivityLogRepository()

    def execute(self, user_id: str, limit: int = 50) -> UseCaseResult:
        activities = self.activity_repo.get_for_entity_user(user_id, limit)
        return UseCaseResult.ok({
            'activities': [a.to_dict() for a in activities]
        })


class GetCompanyActivityUseCase(BaseQueryUseCase):
    """Get activity logs for a company with filters"""

    def __init__(self):
        self.activity_repo = ActivityLogRepository()

    def execute(
        self,
        company_id: str,
        entity_type: str = None,
        action: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        page: int = 1,
        per_page: int = 50
    ) -> UseCaseResult:
        pagination = self.activity_repo.get_by_company(
            company_id=company_id,
            entity_type=entity_type,
            action=action,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page
        )

        return UseCaseResult.ok({
            'activities': [a.to_dict() for a in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class SearchActivityUseCase(BaseQueryUseCase):
    """Advanced search for activity logs"""

    def __init__(self):
        self.activity_repo = ActivityLogRepository()

    def execute(
        self,
        company_id: str = None,
        entity_type: str = None,
        entity_id: str = None,
        action: str = None,
        performed_by_id: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        page: int = 1,
        per_page: int = 50
    ) -> UseCaseResult:
        pagination = self.activity_repo.search(
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            performed_by_id=performed_by_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page
        )

        return UseCaseResult.ok({
            'activities': [a.to_dict() for a in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


# ============== Impersonation Use Cases ==============

class StartImpersonationUseCase(BaseCommandUseCase):
    """
    Start an impersonation session.

    Business Rules:
    - Only super_admin can impersonate other users
    - Cannot impersonate another super_admin
    - Must provide a reason for audit purposes
    - Creates a new JWT token with impersonation claims
    """

    def execute(self, admin_id: str, target_user_id: str, reason: str = None) -> UseCaseResult:
        from app.modules.user.models import User, Role

        # Verify admin is super_admin
        admin = User.query.get(admin_id)
        if not admin:
            return UseCaseResult.fail('Admin user not found', 'NOT_FOUND')

        if admin.role.name != Role.SUPER_ADMIN:
            return UseCaseResult.fail('Only super admins can impersonate users', 'FORBIDDEN')

        # Verify target user exists
        target_user = User.query.get(target_user_id)
        if not target_user:
            return UseCaseResult.fail('Target user not found', 'NOT_FOUND')

        # Cannot impersonate another super_admin
        if target_user.role.name == Role.SUPER_ADMIN:
            return UseCaseResult.fail('Cannot impersonate another super admin', 'FORBIDDEN')

        # Check for existing active impersonation sessions
        active_session = ImpersonationSession.query.filter_by(
            admin_id=admin_id,
            ended_at=None
        ).first()

        if active_session:
            return UseCaseResult.fail(
                'You already have an active impersonation session. Please end it first.',
                'SESSION_ACTIVE'
            )

        # Create impersonation session
        session = ImpersonationSession(
            admin_id=admin_id,
            impersonated_user_id=target_user_id,
            reason=reason,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent')[:500] if request else None
        )
        db.session.add(session)

        # Log the impersonation start
        activity = ActivityLog(
            entity_type=ActivityLog.ENTITY_USER,
            entity_id=target_user_id,
            action=ActivityLog.ACTION_IMPERSONATION_STARTED,
            details={
                'admin_id': admin_id,
                'admin_email': admin.email,
                'target_user_email': target_user.email,
                'reason': reason,
                'session_id': session.id
            },
            performed_by_id=admin_id,
            company_id=target_user.company_id,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent')[:500] if request else None
        )
        db.session.add(activity)
        db.session.commit()

        # Create impersonation token with special claims
        additional_claims = {
            'is_impersonating': True,
            'original_user_id': admin_id,
            'impersonated_user_id': target_user_id,
            'impersonation_session_id': session.id
        }

        # The identity becomes the impersonated user for data access
        impersonation_token = create_access_token(
            identity=target_user_id,
            additional_claims=additional_claims
        )

        return UseCaseResult.ok({
            'session': session.to_dict(),
            'impersonation_token': impersonation_token,
            'target_user': target_user.to_dict(),
            'message': f"Now impersonating {target_user.full_name} ({target_user.email})"
        })


class StopImpersonationUseCase(BaseCommandUseCase):
    """
    Stop an active impersonation session.

    Business Rules:
    - Must have an active impersonation session
    - Logs the session end for audit
    """

    def execute(self, session_id: str, admin_id: str) -> UseCaseResult:
        from app.modules.user.models import User

        session = ImpersonationSession.query.get(session_id)
        if not session:
            return UseCaseResult.fail('Impersonation session not found', 'NOT_FOUND')

        if session.admin_id != admin_id:
            return UseCaseResult.fail('You can only end your own impersonation sessions', 'FORBIDDEN')

        if not session.is_active:
            return UseCaseResult.fail('This impersonation session has already ended', 'SESSION_ENDED')

        # End the session
        session.end_session()

        # Log the impersonation end
        admin = User.query.get(admin_id)
        target_user = User.query.get(session.impersonated_user_id)

        activity = ActivityLog(
            entity_type=ActivityLog.ENTITY_USER,
            entity_id=session.impersonated_user_id,
            action=ActivityLog.ACTION_IMPERSONATION_ENDED,
            details={
                'admin_id': admin_id,
                'admin_email': admin.email if admin else None,
                'target_user_email': target_user.email if target_user else None,
                'session_id': session.id,
                'duration_seconds': session.duration_seconds,
                'action_count': session.action_count
            },
            performed_by_id=admin_id,
            company_id=target_user.company_id if target_user else None,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent')[:500] if request else None
        )
        db.session.add(activity)
        db.session.commit()

        # Generate a fresh token for the admin (their original identity)
        admin_token = create_access_token(identity=admin_id)

        return UseCaseResult.ok({
            'session': session.to_dict(),
            'access_token': admin_token,
            'message': 'Impersonation session ended successfully'
        })


class GetImpersonationHistoryUseCase(BaseQueryUseCase):
    """
    Get impersonation history for audit purposes.

    Can filter by:
    - admin_id: Sessions initiated by a specific admin
    - target_user_id: Sessions targeting a specific user
    - company_id: Sessions involving users from a specific company
    """

    def execute(
        self,
        admin_id: str = None,
        target_user_id: str = None,
        company_id: str = None,
        include_active_only: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> UseCaseResult:
        from app.modules.user.models import User

        query = ImpersonationSession.query

        if admin_id:
            query = query.filter_by(admin_id=admin_id)

        if target_user_id:
            query = query.filter_by(impersonated_user_id=target_user_id)

        if company_id:
            # Filter by target user's company
            query = query.join(
                User,
                ImpersonationSession.impersonated_user_id == User.id
            ).filter(User.company_id == company_id)

        if include_active_only:
            query = query.filter_by(ended_at=None)

        # Order by most recent first
        query = query.order_by(ImpersonationSession.started_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return UseCaseResult.ok({
            'sessions': [s.to_dict() for s in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class GetMyActiveImpersonationUseCase(BaseQueryUseCase):
    """Get the current user's active impersonation session if any"""

    def execute(self, admin_id: str) -> UseCaseResult:
        session = ImpersonationSession.query.filter_by(
            admin_id=admin_id,
            ended_at=None
        ).first()

        if session:
            return UseCaseResult.ok({
                'session': session.to_dict(),
                'is_impersonating': True
            })

        return UseCaseResult.ok({
            'session': None,
            'is_impersonating': False
        })
