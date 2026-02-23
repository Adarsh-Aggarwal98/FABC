"""Create custom status use case."""

from app.extensions import db
from app.common.usecase import UseCaseResult
from app.modules.services.models.status_models import CompanyRequestStatus
from app.modules.services.repositories.status_repository import CompanyRequestStatusRepository


class CreateCustomStatusUseCase:
    """Create a new custom status for a company."""

    def __init__(self):
        self.company_repo = CompanyRequestStatusRepository()

    def execute(
        self,
        company_id: str,
        status_key: str,
        display_name: str,
        description: str = None,
        color: str = '#6B7280',
        position: int = None,
        wip_limit: int = None,
        is_final: bool = False,
        category: str = 'request',
        is_default: bool = False
    ) -> UseCaseResult:
        """Create a new custom status."""
        try:
            # Check for duplicate key
            existing = self.company_repo.get_by_key_and_company(status_key, company_id)
            if existing:
                return UseCaseResult.fail(
                    f"Status with key '{status_key}' already exists",
                    'DUPLICATE_KEY'
                )

            # Get next position if not provided
            if position is None:
                position = self.company_repo.get_next_position(company_id)

            # If setting as default, unset other defaults in same category
            if is_default:
                existing_defaults = CompanyRequestStatus.query.filter_by(
                    company_id=company_id,
                    is_default=True
                ).filter(
                    (CompanyRequestStatus.category == category) |
                    (CompanyRequestStatus.category == 'both')
                ).all()
                for d in existing_defaults:
                    d.is_default = False

            # Create status
            status = CompanyRequestStatus(
                company_id=company_id,
                status_key=status_key,
                display_name=display_name,
                description=description,
                color=color,
                position=position,
                wip_limit=wip_limit,
                is_final=is_final,
                category=category,
                is_default=is_default
            )

            self.company_repo.create(status)
            db.session.commit()

            return UseCaseResult.ok({
                'status': status.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'CREATE_STATUS_ERROR')
