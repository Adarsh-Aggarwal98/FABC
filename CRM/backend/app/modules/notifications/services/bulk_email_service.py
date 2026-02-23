"""
BulkEmailRecipientService - Service for filtering recipients for bulk email campaigns
"""
from sqlalchemy import or_
from app.extensions import db
from app.modules.user.models import User, Role


class BulkEmailRecipientService:
    """Service for filtering recipients for bulk email campaigns"""

    @classmethod
    def get_filtered_recipients(cls, company_id: str, filter_criteria: dict) -> list:
        """
        Get users matching the filter criteria.

        Filter criteria can include:
        - roles: list of role names (e.g., ['client', 'accountant'])
        - tags: list of tag IDs to match
        - status: 'active' or 'inactive'
        - has_service_requests: bool - users who have submitted requests
        - service_ids: list of service IDs - users who requested specific services
        - created_after: datetime - users created after this date
        - created_before: datetime - users created before this date
        - has_outstanding_invoices: bool - users with unpaid invoices
        - search: text search on name/email
        - exclude_user_ids: list of user IDs to exclude
        """
        query = User.query.filter_by(company_id=company_id)

        # Filter by active status
        status = filter_criteria.get('status', 'active')
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        # 'all' includes both

        # Filter by roles
        roles = filter_criteria.get('roles', [])
        if roles:
            role_ids = Role.query.filter(Role.name.in_(roles)).with_entities(Role.id).all()
            role_ids = [r.id for r in role_ids]
            if role_ids:
                query = query.filter(User.role_id.in_(role_ids))

        # Filter by tags
        tags = filter_criteria.get('tags', [])
        if tags:
            from app.modules.tags.models import user_tags
            query = query.join(user_tags).filter(user_tags.c.tag_id.in_(tags))

        # Filter by service requests
        if filter_criteria.get('has_service_requests'):
            from app.modules.services.models import ServiceRequest
            user_ids_with_requests = ServiceRequest.query.filter_by(
                company_id=company_id
            ).with_entities(ServiceRequest.user_id).distinct().all()
            user_ids_with_requests = [u.user_id for u in user_ids_with_requests]
            query = query.filter(User.id.in_(user_ids_with_requests))

        # Filter by specific services requested
        service_ids = filter_criteria.get('service_ids', [])
        if service_ids:
            from app.modules.services.models import ServiceRequest
            user_ids_with_services = ServiceRequest.query.filter(
                ServiceRequest.company_id == company_id,
                ServiceRequest.service_id.in_(service_ids)
            ).with_entities(ServiceRequest.user_id).distinct().all()
            user_ids_with_services = [u.user_id for u in user_ids_with_services]
            query = query.filter(User.id.in_(user_ids_with_services))

        # Filter by created date range
        if filter_criteria.get('created_after'):
            query = query.filter(User.created_at >= filter_criteria['created_after'])
        if filter_criteria.get('created_before'):
            query = query.filter(User.created_at <= filter_criteria['created_before'])

        # Filter users with outstanding invoices
        if filter_criteria.get('has_outstanding_invoices'):
            from app.modules.services.models import Invoice
            user_ids_with_invoices = Invoice.query.filter(
                Invoice.company_id == company_id,
                Invoice.balance_due > 0,
                Invoice.status.in_(['sent', 'overdue'])
            ).with_entities(Invoice.client_id).distinct().all()
            user_ids_with_invoices = [u.client_id for u in user_ids_with_invoices]
            query = query.filter(User.id.in_(user_ids_with_invoices))

        # Text search
        search = filter_criteria.get('search', '').strip()
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern)
                )
            )

        # Exclude specific users
        exclude_ids = filter_criteria.get('exclude_user_ids', [])
        if exclude_ids:
            query = query.filter(~User.id.in_(exclude_ids))

        return query.all()

    @classmethod
    def count_filtered_recipients(cls, company_id: str, filter_criteria: dict) -> int:
        """Count recipients matching filter without fetching all data"""
        query = User.query.filter_by(company_id=company_id)

        status = filter_criteria.get('status', 'active')
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)

        roles = filter_criteria.get('roles', [])
        if roles:
            role_ids = Role.query.filter(Role.name.in_(roles)).with_entities(Role.id).all()
            role_ids = [r.id for r in role_ids]
            if role_ids:
                query = query.filter(User.role_id.in_(role_ids))

        tags = filter_criteria.get('tags', [])
        if tags:
            from app.modules.tags.models import user_tags
            query = query.join(user_tags).filter(user_tags.c.tag_id.in_(tags))

        return query.count()

    @classmethod
    def get_filter_summary(cls, company_id: str) -> dict:
        """
        Get summary of available filter options for a company.
        Returns counts for each filter category to help UI display.
        """
        # Get role counts
        role_counts = db.session.query(
            Role.name, db.func.count(User.id)
        ).join(User).filter(
            User.company_id == company_id,
            User.is_active == True
        ).group_by(Role.name).all()

        # Get tag counts
        from app.modules.tags.models import user_tags, ClientTag
        tag_counts = db.session.query(
            ClientTag.id, ClientTag.name, ClientTag.color, db.func.count(user_tags.c.user_id)
        ).join(user_tags).join(User).filter(
            ClientTag.company_id == company_id,
            User.is_active == True
        ).group_by(ClientTag.id, ClientTag.name, ClientTag.color).all()

        return {
            'total_active_users': User.query.filter_by(company_id=company_id, is_active=True).count(),
            'roles': [{'name': name, 'count': count} for name, count in role_counts],
            'tags': [{'id': id, 'name': name, 'color': color, 'count': count}
                     for id, name, color, count in tag_counts]
        }
