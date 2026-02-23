"""
Create Client Entity Use Case
==============================
Business logic for creating a new ClientEntity.
"""

from datetime import date
from app.extensions import db
from ..models import ClientEntity, ClientEntityContact
from ..repositories import ClientEntityRepository, ClientEntityContactRepository
from .result import UseCaseResult


class CreateClientEntityUseCase:
    """Use case for creating a new ClientEntity."""

    def __init__(self):
        self.entity_repo = ClientEntityRepository()
        self.contact_repo = ClientEntityContactRepository()

    def execute(
        self,
        company_id: str,
        created_by_id: str,
        name: str,
        entity_type: str,
        trading_name: str = None,
        abn: str = None,
        acn: str = None,
        tfn: str = None,
        trust_type: str = None,
        trustee_name: str = None,
        trust_deed_date: date = None,
        email: str = None,
        phone: str = None,
        address_line1: str = None,
        address_line2: str = None,
        city: str = None,
        state: str = None,
        postcode: str = None,
        country: str = 'Australia',
        financial_year_end_month: int = 6,
        financial_year_end_day: int = 30,
        xero_contact_id: str = None,
        notes: str = None,
        primary_contact: dict = None
    ) -> UseCaseResult:
        """Create a new client entity."""
        try:
            # Check for duplicate name in same company
            existing = self.entity_repo.get_by_name_and_company(name, company_id)
            if existing:
                return UseCaseResult.fail(
                    f"An entity with name '{name}' already exists",
                    'DUPLICATE_NAME'
                )

            # Create entity
            entity = ClientEntity(
                company_id=company_id,
                created_by_id=created_by_id,
                name=name,
                entity_type=entity_type,
                trading_name=trading_name,
                abn=abn,
                acn=acn,
                tfn=tfn,
                trust_type=trust_type,
                trustee_name=trustee_name,
                trust_deed_date=trust_deed_date,
                email=email,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postcode=postcode,
                country=country,
                financial_year_end_month=financial_year_end_month,
                financial_year_end_day=financial_year_end_day,
                xero_contact_id=xero_contact_id,
                notes=notes
            )

            self.entity_repo.create(entity)

            # Create primary contact if provided
            if primary_contact:
                contact = ClientEntityContact(
                    client_entity_id=entity.id,
                    first_name=primary_contact.get('first_name'),
                    last_name=primary_contact.get('last_name'),
                    email=primary_contact.get('email'),
                    phone=primary_contact.get('phone'),
                    position=primary_contact.get('position'),
                    contact_type=primary_contact.get('contact_type', ClientEntityContact.TYPE_PRIMARY),
                    is_primary=True,
                    user_id=primary_contact.get('user_id'),
                    effective_from=primary_contact.get('effective_from') or date.today()
                )
                self.contact_repo.create(contact)

            db.session.commit()

            return UseCaseResult.ok({
                'entity': entity.to_dict(include_primary_contact=True)
            })

        except Exception as e:
            db.session.rollback()
            return UseCaseResult.fail(str(e), 'CREATE_ERROR')
