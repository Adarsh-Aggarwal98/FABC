"""
Company Use Cases - Business Logic Layer
==========================================

This module contains use cases for company-related operations. Each use case
represents a single business operation following the Command Query Responsibility
Segregation (CQRS) pattern:

- Command Use Cases: Operations that modify state (create, update, delete)
- Query Use Cases: Operations that read data without modification

Use Case Pattern:
----------------
Each use case:
1. Receives input data
2. Validates business rules
3. Orchestrates repositories and services
4. Returns a UseCaseResult (success/fail with data or error)

Available Use Cases:
------------------
Company Operations:
    - CreateCompanyUseCase: Create new company with admin owner
    - UpdateCompanyUseCase: Update company details
    - GetCompanyUseCase: Get single company
    - ListCompaniesUseCase: List all companies (paginated)
    - DeleteCompanyUseCase: Soft delete (deactivate) company

User Operations:
    - AddUserToCompanyUseCase: Add accountant or client
    - GetCompanyUsersUseCase: List company users
    - TransferOwnershipUseCase: Transfer company ownership
    - GetMyCompanyUseCase: Get current user's company

Contact Operations:
    - ListCompanyContactsUseCase: List company contacts
    - AddCompanyContactUseCase: Add new contact
    - UpdateCompanyContactUseCase: Update contact
    - DeleteCompanyContactUseCase: Soft delete contact
    - SetPrimaryContactUseCase: Set primary contact

Author: CRM Development Team
"""

import logging
from flask import current_app
from app.common.usecase import BaseCommandUseCase, BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.company.models import Company, CompanyContact, ContactType
from app.modules.company.repositories import CompanyRepository, UserRepository, RoleRepository
from app.modules.user.models import User, Role
from app.modules.user.utils import generate_password
from app.modules.notifications.services import NotificationService

# Configure module-level logger
logger = logging.getLogger(__name__)


class CreateCompanyUseCase(BaseCommandUseCase):
    """
    Creates a new company/practice with a practice owner (admin).

    Business Rules:
    - Company name is required
    - Owner email is required and must not exist
    - Owner is created as Admin role
    - Welcome email is sent to owner
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    def execute(self, data: dict, created_by_id: str) -> UseCaseResult:
        """
        Execute the company creation process.

        Args:
            data: Dictionary containing company and owner details
            created_by_id: ID of the user creating the company

        Returns:
            UseCaseResult with company, owner, and temp_password on success
        """
        logger.info(f"CreateCompanyUseCase: Starting company creation by user_id={created_by_id}")

        try:
            # Step 1: Validate required fields
            logger.debug("Validating required fields...")
            if not data.get('name'):
                logger.warning("Validation failed: Company name is required")
                return UseCaseResult.fail('Company name is required', 'VALIDATION_ERROR')

            if not data.get('owner_email'):
                logger.warning("Validation failed: Owner email is required")
                return UseCaseResult.fail('Practice owner email is required', 'VALIDATION_ERROR')

            owner_email = data['owner_email'].lower().strip()
            logger.debug(f"Processing company: name={data['name']}, owner_email={owner_email}")

            # Step 2: Check if owner email already exists
            if self.user_repo.email_exists(owner_email):
                logger.warning(f"Email already exists: {owner_email}")
                return UseCaseResult.fail(f'A user with email {owner_email} already exists', 'EMAIL_EXISTS')

            # Step 3: Get admin role for the owner
            admin_role = self.role_repo.find_by_name(Role.ADMIN)
            if not admin_role:
                logger.error("Admin role not found in database - run initialization")
                return UseCaseResult.fail('Admin role not found. Please run database initialization.', 'ROLE_NOT_FOUND')

            # Step 4: Create the company entity
            logger.debug("Creating company entity...")
            company = Company(
                name=data['name'],
                trading_name=data.get('trading_name'),
                abn=data.get('abn'),
                acn=data.get('acn'),
                email=data.get('company_email'),
                phone=data.get('phone'),
                website=data.get('website'),
                address_line1=data.get('address_line1'),
                address_line2=data.get('address_line2'),
                city=data.get('city'),
                state=data.get('state'),
                postcode=data.get('postcode'),
                country=data.get('country', 'Australia'),
                company_type=data.get('company_type', 'tax_agent'),
                plan_type=data.get('plan_type', 'standard'),
                max_users=data.get('max_users', 10),
                max_clients=data.get('max_clients', 100)
            )
            self.company_repo.create(company)
            logger.debug(f"Company entity created: company_id={company.id}")

            # Step 5: Generate temporary password for owner
            temp_password = generate_password()
            logger.debug("Generated temporary password for owner")

            # Step 6: Create the practice owner (admin user)
            logger.debug("Creating practice owner user...")
            owner = User(
                email=owner_email,
                first_name=data.get('owner_first_name', ''),
                last_name=data.get('owner_last_name', ''),
                phone=data.get('owner_phone'),
                role_id=admin_role.id,
                company_id=company.id,
                invited_by_id=created_by_id,
                is_first_login=True,
                is_active=True
            )
            owner.set_password(temp_password)
            self.user_repo.create(owner)
            logger.debug(f"Owner user created: user_id={owner.id}")

            # Step 7: Link owner to company
            company.owner_id = owner.id

            # Step 8: Commit all changes
            db.session.commit()
            logger.info(f"Company created successfully: company_id={company.id}, owner_id={owner.id}")

            # Step 9: Send welcome email (non-blocking)
            self._send_welcome_email(owner_email, owner.full_name, company.name, temp_password)

            return UseCaseResult.ok({
                'company': company.to_dict(include_owner=True),
                'owner': owner.to_dict(),
                'temp_password': temp_password
            })

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error creating company: {str(e)}")
            return UseCaseResult.fail(f'Failed to create company: {str(e)}', 'INTERNAL_ERROR')

    def _send_welcome_email(self, email: str, name: str, company_name: str, password: str):
        """Send welcome email to practice owner"""
        try:
            NotificationService.send_practice_owner_welcome_email(
                to_email=email,
                owner_name=name or email,
                company_name=company_name,
                temp_password=password
            )
        except Exception as e:
            current_app.logger.error(f'Failed to send welcome email: {str(e)}')


class UpdateCompanyUseCase(BaseCommandUseCase):
    """
    Updates company details.

    Business Rules:
    - Only owner or super admin can update
    - Only super admin can update plan details
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, data: dict, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission - allow super admin, owner, or company admin
        user = self.user_repo.get_by_id(user_id)
        is_super_admin = user.role.name == Role.SUPER_ADMIN
        is_owner = company.owner_id == user_id
        is_company_admin = user.role.name == Role.ADMIN and str(user.company_id) == str(company_id)

        if not (is_super_admin or is_owner or is_company_admin):
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Update allowed fields
        updateable_fields = [
            'name', 'trading_name', 'abn', 'acn', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postcode', 'country',
            'logo_url', 'primary_color', 'secondary_color', 'tertiary_color', 'is_active',
            # Sidebar branding colors
            'sidebar_bg_color', 'sidebar_text_color', 'sidebar_hover_bg_color',
            # Invoice template fields
            'invoice_prefix', 'invoice_footer', 'invoice_notes', 'invoice_bank_details',
            'invoice_payment_terms',
            # Invoice section visibility
            'invoice_show_logo', 'invoice_show_company_details', 'invoice_show_client_details',
            'invoice_show_bank_details', 'invoice_show_payment_terms', 'invoice_show_notes',
            'invoice_show_footer', 'invoice_show_tax',
            # Currency and tax settings
            'currency', 'currency_symbol', 'tax_type', 'tax_label', 'default_tax_rate'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(company, field, data[field])

        # Super admin can update plan details and company type
        if user.role.name == Role.SUPER_ADMIN:
            if 'company_type' in data:
                company.company_type = data['company_type']
            if 'plan_type' in data:
                company.plan_type = data['plan_type']
            if 'max_users' in data:
                company.max_users = data['max_users']
            if 'max_clients' in data:
                company.max_clients = data['max_clients']

        db.session.commit()
        return UseCaseResult.ok({'company': company.to_dict()})


class GetCompanyUseCase(BaseQueryUseCase):
    """Gets company details by ID"""

    def __init__(self):
        self.company_repo = CompanyRepository()

    def execute(self, company_id: str, include_owner: bool = True, include_stats: bool = False) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        return UseCaseResult.ok({
            'company': company.to_dict(include_owner=include_owner, include_stats=include_stats)
        })


class ListCompaniesUseCase(BaseQueryUseCase):
    """Lists all companies with pagination and search"""

    def __init__(self):
        self.company_repo = CompanyRepository()

    def execute(self, page: int = 1, per_page: int = 20, search: str = None,
                active_only: bool = True) -> UseCaseResult:
        pagination = self.company_repo.search(
            search_term=search,
            active_only=active_only,
            page=page,
            per_page=per_page
        )

        return UseCaseResult.ok({
            'companies': [c.to_dict(include_stats=True) for c in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class DeleteCompanyUseCase(BaseCommandUseCase):
    """
    Soft deletes (deactivates) a company.

    Business Rules:
    - Only super admin can delete
    - Deactivates all company users
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, user_id: str) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if user.role.name != Role.SUPER_ADMIN:
            return UseCaseResult.fail('Only super admin can delete companies', 'FORBIDDEN')

        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Soft delete - deactivate company and all its users
        company.is_active = False
        self.company_repo.deactivate_company_users(company_id)

        db.session.commit()
        return UseCaseResult.ok({'message': 'Company deactivated'})


class AddUserToCompanyUseCase(BaseCommandUseCase):
    """
    Adds a new user (accountant or client) to a company.

    Business Rules:
    - Only company owner, admin, or super admin can add
    - Email must not exist
    - Role must be accountant or user (client)
    - Respects company user/client limits
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    def execute(self, company_id: str, user_data: dict, added_by_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        adding_user = self.user_repo.get_by_id(added_by_id)
        if adding_user.role.name == Role.SUPER_ADMIN:
            pass  # Super admin can add to any company
        elif adding_user.company_id != company_id:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')
        elif adding_user.role.name not in [Role.ADMIN, Role.SENIOR_ACCOUNTANT, Role.ACCOUNTANT]:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Check if email exists
        email = user_data['email'].lower().strip()
        if self.user_repo.email_exists(email):
            return UseCaseResult.fail(f'User with email {email} already exists', 'EMAIL_EXISTS')

        # Validate role based on who is adding
        role_name = user_data.get('role', Role.USER)

        # Role permissions for inviting users:
        # - Super admin: can invite all roles
        # - Admin: can invite senior_accountant, accountant, external_accountant, user
        # - Senior Accountant: can invite accountant, external_accountant, user
        # - Accountant: can invite external_accountant, user
        # - External accountant & user: cannot invite anyone
        if adding_user.role.name == Role.SUPER_ADMIN:
            allowed_roles = [Role.SUPER_ADMIN, Role.ADMIN, Role.SENIOR_ACCOUNTANT, Role.ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT, Role.USER]
        elif adding_user.role.name == Role.ADMIN:
            allowed_roles = [Role.SENIOR_ACCOUNTANT, Role.ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT, Role.USER]
        elif adding_user.role.name == Role.SENIOR_ACCOUNTANT:
            allowed_roles = [Role.ACCOUNTANT, Role.EXTERNAL_ACCOUNTANT, Role.USER]
        elif adding_user.role.name == Role.ACCOUNTANT:
            allowed_roles = [Role.EXTERNAL_ACCOUNTANT, Role.USER]
        else:
            allowed_roles = []

        if role_name not in allowed_roles:
            return UseCaseResult.fail(f'You can only add: {", ".join(allowed_roles)}', 'INVALID_ROLE')

        role = self.role_repo.find_by_name(role_name)
        if not role:
            return UseCaseResult.fail(f'Role {role_name} not found', 'ROLE_NOT_FOUND')

        # Note: User/client limits are currently disabled

        # Check if external accountant (skip onboarding)
        is_external_accountant = user_data.get('is_external_accountant', False)

        # Generate password and create user
        temp_password = generate_password()

        new_user = User(
            email=email,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone=user_data.get('phone'),
            role_id=role.id,
            company_id=company_id,
            invited_by_id=added_by_id,
            is_first_login=not is_external_accountant,  # External accountants skip onboarding
            is_external_accountant=is_external_accountant,
            is_active=True
        )
        new_user.set_password(temp_password)
        self.user_repo.create(new_user)
        db.session.commit()

        # Send invitation email
        self._send_invitation_email(email, new_user.full_name, company.name, temp_password, role_name)

        return UseCaseResult.ok({
            'user': new_user.to_dict(),
            'temp_password': temp_password
        })

    def _send_invitation_email(self, email: str, name: str, company_name: str,
                                password: str, role: str):
        """Send invitation email to new user"""
        try:
            NotificationService.send_user_invitation_email(
                to_email=email,
                user_name=name or email,
                company_name=company_name,
                temp_password=password,
                role=role
            )
        except Exception as e:
            current_app.logger.error(f'Failed to send invitation email: {str(e)}')


class GetCompanyUsersUseCase(BaseQueryUseCase):
    """Gets users in a company with pagination"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, user_id: str, role_filter: str = None,
                page: int = 1, per_page: int = 20) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        requesting_user = self.user_repo.get_by_id(user_id)
        if requesting_user.role.name != Role.SUPER_ADMIN and requesting_user.company_id != company_id:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        pagination = self.company_repo.get_company_users(
            company_id, role_filter, page, per_page
        )

        return UseCaseResult.ok({
            'users': [u.to_dict() for u in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class TransferOwnershipUseCase(BaseCommandUseCase):
    """
    Transfers company ownership to another user.

    Business Rules:
    - Only owner or super admin can transfer
    - New owner must be a company member
    - Old owner is demoted to accountant
    - New owner is promoted to admin
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    def execute(self, company_id: str, new_owner_id: str, current_user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        current_user = self.user_repo.get_by_id(current_user_id)
        if current_user.role.name != Role.SUPER_ADMIN and company.owner_id != current_user_id:
            return UseCaseResult.fail('Only the owner or super admin can transfer ownership', 'FORBIDDEN')

        new_owner = self.user_repo.get_by_id(new_owner_id)
        if not new_owner:
            return UseCaseResult.fail('New owner not found', 'NOT_FOUND')

        if new_owner.company_id != company_id:
            return UseCaseResult.fail('New owner must be a member of the company', 'INVALID_USER')

        # Update roles
        admin_role = self.role_repo.find_by_name(Role.ADMIN)
        accountant_role = self.role_repo.find_by_name(Role.ACCOUNTANT)

        # Demote old owner to accountant (if they're not super admin)
        old_owner = company.owner
        if old_owner and old_owner.role.name != Role.SUPER_ADMIN:
            old_owner.role_id = accountant_role.id

        # Promote new owner to admin
        new_owner.role_id = admin_role.id
        company.owner_id = new_owner_id

        db.session.commit()
        return UseCaseResult.ok({'company': company.to_dict(include_owner=True)})


class GetMyCompanyUseCase(BaseQueryUseCase):
    """Gets the current user's company"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, user_id: str) -> UseCaseResult:
        user = self.user_repo.get_by_id(user_id)
        if not user.company_id:
            return UseCaseResult.fail('You are not associated with any company', 'NOT_FOUND')

        company = self.company_repo.get_by_id(user.company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        return UseCaseResult.ok({
            'company': company.to_dict(include_owner=True, include_stats=True)
        })


# ============== Company Contact Use Cases ==============

class ListCompanyContactsUseCase(BaseQueryUseCase):
    """Lists contacts for a company"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, user_id: str, include_inactive: bool = False) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Query contacts
        query = CompanyContact.query.filter_by(company_id=company_id)
        if not include_inactive:
            query = query.filter_by(is_active=True)

        contacts = query.order_by(
            CompanyContact.is_primary.desc(),
            CompanyContact.created_at.desc()
        ).all()

        return UseCaseResult.ok({
            'contacts': [c.to_dict() for c in contacts]
        })


class GetCompanyContactHistoryUseCase(BaseQueryUseCase):
    """Gets all contacts including historical (inactive) ones"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name != Role.SUPER_ADMIN and str(user.company_id) != str(company_id):
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Get all contacts including inactive
        contacts = CompanyContact.query.filter_by(company_id=company_id).order_by(
            CompanyContact.is_active.desc(),
            CompanyContact.is_primary.desc(),
            CompanyContact.effective_to.desc().nullslast(),
            CompanyContact.created_at.desc()
        ).all()

        return UseCaseResult.ok({
            'contacts': [c.to_dict() for c in contacts]
        })


class AddCompanyContactUseCase(BaseCommandUseCase):
    """
    Adds a new contact to a company.

    Business Rules:
    - Company owner, admin, or super admin can add contacts
    - If is_primary is set, unset other primary contacts
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, data: dict, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name == Role.SUPER_ADMIN:
            pass
        elif user.role.name == Role.ADMIN and str(user.company_id) == str(company_id):
            pass
        elif company.owner_id == user_id:
            pass
        else:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Validate required fields
        if not data.get('first_name'):
            return UseCaseResult.fail('First name is required', 'VALIDATION_ERROR')
        if not data.get('last_name'):
            return UseCaseResult.fail('Last name is required', 'VALIDATION_ERROR')

        # Parse contact type
        contact_type = ContactType.PRIMARY
        if data.get('contact_type'):
            try:
                contact_type = ContactType(data['contact_type'])
            except ValueError:
                return UseCaseResult.fail(f"Invalid contact type. Must be one of: {', '.join([t.value for t in ContactType])}", 'VALIDATION_ERROR')

        # Parse dates
        effective_from = None
        effective_to = None
        if data.get('effective_from'):
            try:
                from datetime import date
                effective_from = date.fromisoformat(data['effective_from'])
            except ValueError:
                return UseCaseResult.fail('Invalid effective_from date format. Use YYYY-MM-DD', 'VALIDATION_ERROR')
        if data.get('effective_to'):
            try:
                from datetime import date
                effective_to = date.fromisoformat(data['effective_to'])
            except ValueError:
                return UseCaseResult.fail('Invalid effective_to date format. Use YYYY-MM-DD', 'VALIDATION_ERROR')

        # If setting as primary, unset other primary contacts
        is_primary = data.get('is_primary', False)
        if is_primary:
            CompanyContact.query.filter_by(
                company_id=company_id,
                is_primary=True
            ).update({'is_primary': False})

        # Create contact
        contact = CompanyContact(
            company_id=company_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            position=data.get('position'),
            contact_type=contact_type,
            is_primary=is_primary,
            effective_from=effective_from,
            effective_to=effective_to,
            is_active=data.get('is_active', True),
            notes=data.get('notes')
        )

        db.session.add(contact)
        db.session.commit()

        return UseCaseResult.ok({
            'contact': contact.to_dict(),
            'message': 'Contact added successfully'
        })


class UpdateCompanyContactUseCase(BaseCommandUseCase):
    """Updates an existing contact"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, contact_id: str, data: dict, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name == Role.SUPER_ADMIN:
            pass
        elif user.role.name == Role.ADMIN and str(user.company_id) == str(company_id):
            pass
        elif company.owner_id == user_id:
            pass
        else:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Find contact
        contact = CompanyContact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            return UseCaseResult.fail('Contact not found', 'NOT_FOUND')

        # Update fields
        updateable_fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'notes', 'is_active']
        for field in updateable_fields:
            if field in data:
                setattr(contact, field, data[field])

        # Handle contact type
        if 'contact_type' in data:
            try:
                contact.contact_type = ContactType(data['contact_type'])
            except ValueError:
                return UseCaseResult.fail(f"Invalid contact type. Must be one of: {', '.join([t.value for t in ContactType])}", 'VALIDATION_ERROR')

        # Handle dates
        if 'effective_from' in data:
            if data['effective_from']:
                try:
                    from datetime import date
                    contact.effective_from = date.fromisoformat(data['effective_from'])
                except ValueError:
                    return UseCaseResult.fail('Invalid effective_from date format. Use YYYY-MM-DD', 'VALIDATION_ERROR')
            else:
                contact.effective_from = None

        if 'effective_to' in data:
            if data['effective_to']:
                try:
                    from datetime import date
                    contact.effective_to = date.fromisoformat(data['effective_to'])
                except ValueError:
                    return UseCaseResult.fail('Invalid effective_to date format. Use YYYY-MM-DD', 'VALIDATION_ERROR')
            else:
                contact.effective_to = None

        # Handle is_primary
        if 'is_primary' in data and data['is_primary']:
            # Unset other primary contacts
            CompanyContact.query.filter(
                CompanyContact.company_id == company_id,
                CompanyContact.id != contact_id,
                CompanyContact.is_primary == True
            ).update({'is_primary': False})
            contact.is_primary = True
        elif 'is_primary' in data:
            contact.is_primary = data['is_primary']

        db.session.commit()

        return UseCaseResult.ok({
            'contact': contact.to_dict(),
            'message': 'Contact updated successfully'
        })


class DeleteCompanyContactUseCase(BaseCommandUseCase):
    """
    Soft deletes a contact by setting effective_to date and is_active to False.
    """

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, contact_id: str, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name == Role.SUPER_ADMIN:
            pass
        elif user.role.name == Role.ADMIN and str(user.company_id) == str(company_id):
            pass
        elif company.owner_id == user_id:
            pass
        else:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Find contact
        contact = CompanyContact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            return UseCaseResult.fail('Contact not found', 'NOT_FOUND')

        # Soft delete - set effective_to to today and is_active to False
        from datetime import date
        contact.effective_to = date.today()
        contact.is_active = False

        # If this was primary, clear the flag
        contact.is_primary = False

        db.session.commit()

        return UseCaseResult.ok({
            'message': 'Contact deleted successfully'
        })


class SetPrimaryContactUseCase(BaseCommandUseCase):
    """Sets a contact as the primary contact for a company"""

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.user_repo = UserRepository()

    def execute(self, company_id: str, contact_id: str, user_id: str) -> UseCaseResult:
        company = self.company_repo.get_by_id(company_id)
        if not company:
            return UseCaseResult.fail('Company not found', 'NOT_FOUND')

        # Check permission
        user = self.user_repo.get_by_id(user_id)
        if user.role.name == Role.SUPER_ADMIN:
            pass
        elif user.role.name == Role.ADMIN and str(user.company_id) == str(company_id):
            pass
        elif company.owner_id == user_id:
            pass
        else:
            return UseCaseResult.fail('Permission denied', 'FORBIDDEN')

        # Find contact
        contact = CompanyContact.query.filter_by(id=contact_id, company_id=company_id).first()
        if not contact:
            return UseCaseResult.fail('Contact not found', 'NOT_FOUND')

        if not contact.is_active:
            return UseCaseResult.fail('Cannot set inactive contact as primary', 'VALIDATION_ERROR')

        # Unset other primary contacts
        CompanyContact.query.filter(
            CompanyContact.company_id == company_id,
            CompanyContact.id != contact_id,
            CompanyContact.is_primary == True
        ).update({'is_primary': False})

        # Set this contact as primary
        contact.is_primary = True
        db.session.commit()

        return UseCaseResult.ok({
            'contact': contact.to_dict(),
            'message': 'Contact set as primary successfully'
        })
