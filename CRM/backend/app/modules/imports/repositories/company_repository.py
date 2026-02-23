"""
Company Repository for Import Operations

Provides data access methods for company-related import operations.
"""
import logging
from typing import Optional

from app.extensions import db
from app.modules.company.models import Company

logger = logging.getLogger(__name__)


class CompanyImportRepository:
    """Repository for company import operations."""

    @staticmethod
    def company_exists(name: str) -> bool:
        """Check if a company with the given name exists."""
        return Company.query.filter_by(name=name).first() is not None

    @staticmethod
    def get_company_by_name(name: str) -> Optional[Company]:
        """Get a company by name."""
        return Company.query.filter_by(name=name).first()

    @staticmethod
    def create_company(
        name: str,
        trading_name: Optional[str] = None,
        abn: Optional[str] = None,
        acn: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        website: Optional[str] = None,
        tax_agent_number: Optional[str] = None
    ) -> Company:
        """
        Create a new company.

        Args:
            name: Company name
            **kwargs: Optional company attributes

        Returns:
            The created Company object
        """
        company = Company(
            name=name,
            trading_name=trading_name,
            abn=abn,
            acn=acn,
            email=email,
            phone=phone,
            address=address,
            website=website,
            tax_agent_number=tax_agent_number,
            is_active=True
        )
        db.session.add(company)
        db.session.flush()
        return company

    @staticmethod
    def commit():
        """Commit the current transaction."""
        db.session.commit()
