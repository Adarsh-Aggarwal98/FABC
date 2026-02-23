"""
Company Services - Domain Logic Layer
======================================

This module contains domain services for company-related operations.
Services handle complex business logic that spans multiple entities
or requires external integrations.

Services vs Use Cases:
--------------------
- Use Cases: Application-level orchestration, one per user action
- Services: Reusable domain logic, can be called by multiple use cases

Available Services:
-----------------
PlanLimitService:
    Enforces subscription plan limits (users, clients, features)
    - get_plan_limits(): Get limits for a plan type
    - get_usage_stats(): Get current usage statistics
    - can_add_user(): Check if new user can be added
    - has_feature(): Check if feature is available

CompanyService:
    Legacy service with company CRUD operations
    (Prefer using use cases for new code)

Author: CRM Development Team
"""

import logging
from flask import current_app
from app.extensions import db
from app.modules.company.models import Company
from app.modules.user.models import User, Role
from app.modules.user.utils import generate_password
from app.modules.notifications.services import NotificationService
from app.common.exceptions import ValidationError, NotFoundError

# Configure module-level logger
logger = logging.getLogger(__name__)


# ============== Plan Limit Configuration ==============

PLAN_LIMITS = {
    'starter': {
        'max_users': 5,
        'max_clients': 50,
        'max_services': 10,
        'max_forms': 5,
        'max_storage_mb': 1024,  # 1 GB
        'features': {
            'bulk_email': False,
            'custom_branding': False,
            'api_access': False,
            'custom_forms': False,
            'advanced_reporting': False
        }
    },
    'standard': {
        'max_users': 10,
        'max_clients': 100,
        'max_services': 25,
        'max_forms': 20,
        'max_storage_mb': 5120,  # 5 GB
        'features': {
            'bulk_email': True,
            'custom_branding': True,
            'api_access': False,
            'custom_forms': True,
            'advanced_reporting': True
        }
    },
    'premium': {
        'max_users': 50,
        'max_clients': 500,
        'max_services': -1,  # Unlimited
        'max_forms': -1,  # Unlimited
        'max_storage_mb': 51200,  # 50 GB
        'features': {
            'bulk_email': True,
            'custom_branding': True,
            'api_access': True,
            'custom_forms': True,
            'advanced_reporting': True
        }
    },
    'enterprise': {
        'max_users': -1,  # Unlimited
        'max_clients': -1,  # Unlimited
        'max_services': -1,  # Unlimited
        'max_forms': -1,  # Unlimited
        'max_storage_mb': -1,  # Unlimited
        'features': {
            'bulk_email': True,
            'custom_branding': True,
            'api_access': True,
            'custom_forms': True,
            'advanced_reporting': True
        }
    }
}


class PlanLimitError(Exception):
    """Exception raised when a plan limit is exceeded"""
    def __init__(self, message, limit_type, current_usage, max_allowed):
        self.message = message
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.max_allowed = max_allowed
        super().__init__(self.message)


class PlanLimitService:
    """
    Service for enforcing plan limits across the application.

    Usage:
        # Check if action is allowed
        can_add, error = PlanLimitService.can_add_user(company_id, 'user')
        if not can_add:
            return error_response(error, 403)

        # Get current usage stats
        stats = PlanLimitService.get_usage_stats(company_id)

        # Check feature availability
        if not PlanLimitService.has_feature(company_id, 'bulk_email'):
            return error_response('This feature is not available in your plan', 403)
    """

    @staticmethod
    def get_plan_limits(plan_type: str) -> dict:
        """
        Get the limits for a specific plan type.

        Args:
            plan_type: The plan name ('starter', 'standard', 'premium', 'enterprise')

        Returns:
            dict: Plan limits including max_users, max_clients, features, etc.
        """
        logger.debug(f"Getting plan limits for plan_type={plan_type}")
        limits = PLAN_LIMITS.get(plan_type, PLAN_LIMITS['standard'])
        logger.debug(f"Plan limits: max_users={limits.get('max_users')}, max_clients={limits.get('max_clients')}")
        return limits

    @staticmethod
    def get_company_limits(company_id: str) -> dict:
        """
        Get the effective limits for a company (plan limits + any overrides).

        Company-specific overrides (max_users, max_clients) take precedence
        if they are higher than the plan defaults.

        Args:
            company_id: The company ID

        Returns:
            dict: Effective limits for the company
        """
        logger.debug(f"Getting company limits for company_id={company_id}")
        company = Company.query.get(company_id)
        if not company:
            logger.warning(f"Company not found, returning standard limits: company_id={company_id}")
            return PLAN_LIMITS['standard']

        plan_limits = PLAN_LIMITS.get(company.plan_type, PLAN_LIMITS['standard']).copy()
        logger.debug(f"Base plan limits for {company.plan_type}: {plan_limits}")

        # Apply company-specific overrides (if higher than plan default)
        if company.max_users and company.max_users > plan_limits.get('max_users', 0):
            logger.debug(f"Applying user override: {plan_limits.get('max_users')} -> {company.max_users}")
            plan_limits['max_users'] = company.max_users
        if company.max_clients and company.max_clients > plan_limits.get('max_clients', 0):
            logger.debug(f"Applying client override: {plan_limits.get('max_clients')} -> {company.max_clients}")
            plan_limits['max_clients'] = company.max_clients

        return plan_limits

    @staticmethod
    def get_usage_stats(company_id: str) -> dict:
        """Get current usage statistics for a company"""
        company = Company.query.get(company_id)
        if not company:
            return None

        # Count users by role
        total_users = company.users.count()
        client_count = company.users.join(Role).filter(Role.name == Role.USER).count()
        staff_count = total_users - client_count  # Admin + Accountants

        # Count services (if applicable)
        from app.modules.services.models import CompanyServiceSettings
        active_services = CompanyServiceSettings.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

        # Count forms
        from app.modules.forms.models import Form
        company_forms = Form.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

        # Get limits
        limits = PlanLimitService.get_company_limits(company_id)

        return {
            'plan_type': company.plan_type,
            'usage': {
                'users': {
                    'current': staff_count,
                    'max': limits.get('max_users', 10),
                    'percentage': (staff_count / limits.get('max_users', 10) * 100) if limits.get('max_users', 10) > 0 else 0
                },
                'clients': {
                    'current': client_count,
                    'max': limits.get('max_clients', 100),
                    'percentage': (client_count / limits.get('max_clients', 100) * 100) if limits.get('max_clients', 100) > 0 else 0
                },
                'services': {
                    'current': active_services,
                    'max': limits.get('max_services', 25),
                    'percentage': (active_services / limits.get('max_services', 25) * 100) if limits.get('max_services', 25) > 0 else 0
                },
                'forms': {
                    'current': company_forms,
                    'max': limits.get('max_forms', 20),
                    'percentage': (company_forms / limits.get('max_forms', 20) * 100) if limits.get('max_forms', 20) > 0 else 0
                }
            },
            'features': limits.get('features', {})
        }

    @staticmethod
    def can_add_user(company_id: str, role_name: str) -> tuple:
        """
        Check if a new user can be added to the company.

        Args:
            company_id: The company ID
            role_name: The role of the user being added ('user', 'accountant', etc.)

        Returns:
            tuple: (can_add: bool, error_message: str or None)
        """
        company = Company.query.get(company_id)
        if not company:
            return False, 'Company not found'

        limits = PlanLimitService.get_company_limits(company_id)

        if role_name == Role.USER:
            # Check client limit
            current_clients = company.users.join(Role).filter(Role.name == Role.USER).count()
            max_clients = limits.get('max_clients', 100)

            if max_clients != -1 and current_clients >= max_clients:
                return False, f'Client limit reached ({current_clients}/{max_clients}). Please upgrade your plan to add more clients.'
        else:
            # Check staff (non-client user) limit
            total_users = company.users.count()
            client_count = company.users.join(Role).filter(Role.name == Role.USER).count()
            current_staff = total_users - client_count
            max_users = limits.get('max_users', 10)

            if max_users != -1 and current_staff >= max_users:
                return False, f'User limit reached ({current_staff}/{max_users}). Please upgrade your plan to add more team members.'

        return True, None

    @staticmethod
    def can_add_service(company_id: str) -> tuple:
        """Check if a new service can be activated for the company"""
        company = Company.query.get(company_id)
        if not company:
            return False, 'Company not found'

        limits = PlanLimitService.get_company_limits(company_id)
        max_services = limits.get('max_services', 25)

        if max_services == -1:
            return True, None

        from app.modules.services.models import CompanyServiceSettings
        current_services = CompanyServiceSettings.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

        if current_services >= max_services:
            return False, f'Service limit reached ({current_services}/{max_services}). Please upgrade your plan to activate more services.'

        return True, None

    @staticmethod
    def can_create_form(company_id: str) -> tuple:
        """Check if a new form can be created for the company"""
        company = Company.query.get(company_id)
        if not company:
            return False, 'Company not found'

        limits = PlanLimitService.get_company_limits(company_id)

        # Check if custom forms feature is enabled
        if not limits.get('features', {}).get('custom_forms', True):
            return False, 'Custom forms are not available in your plan. Please upgrade to create custom forms.'

        max_forms = limits.get('max_forms', 20)

        if max_forms == -1:
            return True, None

        from app.modules.forms.models import Form
        current_forms = Form.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

        if current_forms >= max_forms:
            return False, f'Form limit reached ({current_forms}/{max_forms}). Please upgrade your plan to create more forms.'

        return True, None

    @staticmethod
    def has_feature(company_id: str, feature_name: str) -> bool:
        """Check if a company has access to a specific feature"""
        limits = PlanLimitService.get_company_limits(company_id)
        return limits.get('features', {}).get(feature_name, False)

    @staticmethod
    def check_feature(company_id: str, feature_name: str) -> tuple:
        """
        Check if a feature is available and return appropriate response.

        Returns:
            tuple: (has_feature: bool, error_message: str or None)
        """
        if PlanLimitService.has_feature(company_id, feature_name):
            return True, None

        company = Company.query.get(company_id)
        plan_name = company.plan_type if company else 'standard'

        return False, f'The {feature_name.replace("_", " ")} feature is not available in your {plan_name} plan. Please upgrade to access this feature.'


class CompanyService:
    """Service for company/practice management"""

    @staticmethod
    def create_company(data, created_by_id):
        """
        Create a new company/practice with a practice owner (admin)

        Args:
            data: Dictionary containing company details and owner email
            created_by_id: ID of user creating the company (super admin)

        Returns:
            dict with company and owner info
        """
        try:
            # Validate required fields
            if not data.get('name'):
                raise ValidationError('Company name is required')
            if not data.get('owner_email'):
                raise ValidationError('Practice owner email is required')

            owner_email = data['owner_email'].lower().strip()

            # Check if owner email already exists
            existing_user = User.query.filter_by(email=owner_email).first()
            if existing_user:
                raise ValidationError(f'A user with email {owner_email} already exists')

            # Get admin role
            admin_role = Role.query.filter_by(name=Role.ADMIN).first()
            if not admin_role:
                raise ValidationError('Admin role not found. Please run database initialization.')

            # Create the company first
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
                plan_type=data.get('plan_type', 'standard'),
                max_users=data.get('max_users', 10),
                max_clients=data.get('max_clients', 100)
            )
            db.session.add(company)
            db.session.flush()  # Get company ID

            # Generate password for owner
            temp_password = generate_password()

            # Create the practice owner (admin user)
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
            db.session.add(owner)
            db.session.flush()

            # Link owner to company
            company.owner_id = owner.id

            db.session.commit()

            # Send welcome email with credentials
            try:
                NotificationService.send_practice_owner_welcome_email(
                    to_email=owner_email,
                    owner_name=owner.full_name or owner_email,
                    company_name=company.name,
                    temp_password=temp_password
                )
            except Exception as e:
                current_app.logger.error(f'Failed to send welcome email: {str(e)}')
                # Don't fail the whole operation if email fails

            return {
                'success': True,
                'company': company.to_dict(include_owner=True),
                'owner': owner.to_dict(),
                'temp_password': temp_password  # Return for display (only in response, not stored)
            }

        except ValidationError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating company: {str(e)}')
            raise ValidationError(f'Failed to create company: {str(e)}')

    @staticmethod
    def update_company(company_id, data, user_id):
        """Update company details"""
        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')

        # Check permission - only owner or super admin can update
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN and company.owner_id != user_id:
            raise ValidationError('Permission denied')

        # Update allowed fields
        updateable_fields = [
            'name', 'trading_name', 'abn', 'acn', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postcode', 'country',
            'logo_url', 'primary_color', 'is_active'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(company, field, data[field])

        # Super admin can update plan details
        if user.role.name == Role.SUPER_ADMIN:
            if 'plan_type' in data:
                company.plan_type = data['plan_type']
            if 'max_users' in data:
                company.max_users = data['max_users']
            if 'max_clients' in data:
                company.max_clients = data['max_clients']

        db.session.commit()
        return company

    @staticmethod
    def get_company(company_id):
        """Get a company by ID"""
        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')
        return company

    @staticmethod
    def list_companies(page=1, per_page=20, search=None, active_only=True):
        """List all companies (super admin only)"""
        query = Company.query

        if active_only:
            query = query.filter_by(is_active=True)

        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Company.name.ilike(search_term),
                    Company.trading_name.ilike(search_term),
                    Company.email.ilike(search_term),
                    Company.abn.ilike(search_term)
                )
            )

        query = query.order_by(Company.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def delete_company(company_id, user_id):
        """Soft delete a company (super admin only)"""
        user = User.query.get(user_id)
        if user.role.name != Role.SUPER_ADMIN:
            raise ValidationError('Only super admin can delete companies')

        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')

        # Soft delete - deactivate company and all its users
        company.is_active = False
        for company_user in company.users:
            company_user.is_active = False

        db.session.commit()
        return True

    @staticmethod
    def add_user_to_company(company_id, user_data, added_by_id):
        """
        Add a new user (accountant or client) to a company

        Args:
            company_id: ID of the company
            user_data: Dictionary with user details and role
            added_by_id: ID of user adding the new user
        """
        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')

        # Check permission - company owner, admin in company, or super admin
        adding_user = User.query.get(added_by_id)
        if adding_user.role.name == Role.SUPER_ADMIN:
            pass  # Super admin can add to any company
        elif adding_user.company_id != company_id:
            raise ValidationError('Permission denied')
        elif adding_user.role.name not in [Role.ADMIN]:
            raise ValidationError('Permission denied')

        # Check if email exists
        email = user_data['email'].lower().strip()
        existing = User.query.filter_by(email=email).first()
        if existing:
            raise ValidationError(f'User with email {email} already exists')

        # Get role
        role_name = user_data.get('role', Role.USER)
        if role_name not in [Role.ACCOUNTANT, Role.USER]:
            raise ValidationError('Can only add accountants or clients to a company')

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValidationError(f'Role {role_name} not found')

        # Check limits
        if role_name == Role.USER:
            current_clients = company.users.join(Role).filter(Role.name == Role.USER).count()
            if current_clients >= company.max_clients:
                raise ValidationError(f'Company has reached maximum client limit ({company.max_clients})')
        else:
            current_users = company.users.count()
            if current_users >= company.max_users:
                raise ValidationError(f'Company has reached maximum user limit ({company.max_users})')

        # Generate password
        temp_password = generate_password()

        # Create user
        new_user = User(
            email=email,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone=user_data.get('phone'),
            role_id=role.id,
            company_id=company_id,
            invited_by_id=added_by_id,
            is_first_login=True,
            is_active=True
        )
        new_user.set_password(temp_password)
        db.session.add(new_user)
        db.session.commit()

        # Send invitation email
        try:
            NotificationService.send_user_invitation_email(
                to_email=email,
                user_name=new_user.full_name or email,
                company_name=company.name,
                temp_password=temp_password,
                role=role_name
            )
        except Exception as e:
            current_app.logger.error(f'Failed to send invitation email: {str(e)}')

        return {
            'success': True,
            'user': new_user.to_dict(),
            'temp_password': temp_password
        }

    @staticmethod
    def get_company_users(company_id, user_id, role_filter=None, page=1, per_page=20):
        """Get users in a company"""
        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')

        # Check permission
        requesting_user = User.query.get(user_id)
        if requesting_user.role.name != Role.SUPER_ADMIN and requesting_user.company_id != company_id:
            raise ValidationError('Permission denied')

        query = User.query.filter_by(company_id=company_id, is_active=True)

        if role_filter:
            query = query.join(Role).filter(Role.name == role_filter)

        query = query.order_by(User.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def transfer_ownership(company_id, new_owner_id, current_user_id):
        """Transfer company ownership to another user"""
        company = Company.query.get(company_id)
        if not company:
            raise NotFoundError('Company not found')

        current_user = User.query.get(current_user_id)
        if current_user.role.name != Role.SUPER_ADMIN and company.owner_id != current_user_id:
            raise ValidationError('Only the owner or super admin can transfer ownership')

        new_owner = User.query.get(new_owner_id)
        if not new_owner:
            raise NotFoundError('New owner not found')

        if new_owner.company_id != company_id:
            raise ValidationError('New owner must be a member of the company')

        # Update roles
        admin_role = Role.query.filter_by(name=Role.ADMIN).first()
        accountant_role = Role.query.filter_by(name=Role.ACCOUNTANT).first()

        # Demote old owner to accountant (if they're not super admin)
        old_owner = company.owner
        if old_owner and old_owner.role.name != Role.SUPER_ADMIN:
            old_owner.role_id = accountant_role.id

        # Promote new owner to admin
        new_owner.role_id = admin_role.id
        company.owner_id = new_owner_id

        db.session.commit()
        return company
