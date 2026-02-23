from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.modules.user.models import User, Role, OTP
from app.modules.user.utils import generate_password, validate_password_strength
from app.common.exceptions import ValidationError, AuthenticationError, NotFoundError, ConflictError


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def login(email, password):
        """
        Step 1 of login: Validate credentials and send OTP (if 2FA enabled).
        Returns user data if credentials are valid.
        """
        user = User.query.filter_by(email=email.lower()).first()

        if not user or not user.check_password(password):
            raise AuthenticationError('Invalid email or password')

        if not user.is_active:
            raise AuthenticationError('Your account has been deactivated')

        # If 2FA is disabled, directly return tokens
        if not user.two_fa_enabled:
            user.last_login = datetime.utcnow()
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                'requires_2fa': False,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(include_sensitive=True),
                'is_first_login': user.is_first_login
            }

        # Generate and send OTP
        otp = OTP.create_otp(user.id, OTP.PURPOSE_LOGIN)

        # Send OTP via email (will be handled by notification service)
        from app.modules.notifications.services import NotificationService
        NotificationService.send_otp_email(user, otp.code)

        return {
            'requires_2fa': True,
            'email': user.email,
            'message': 'OTP sent to your email'
        }

    @staticmethod
    def verify_otp(email, otp_code):
        """
        Step 2 of login: Verify OTP and issue tokens.
        """
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            raise AuthenticationError('Invalid email')

        # Find valid OTP
        otp = OTP.query.filter_by(
            user_id=user.id,
            code=otp_code,
            purpose=OTP.PURPOSE_LOGIN,
            is_used=False
        ).first()

        if not otp or not otp.is_valid():
            raise AuthenticationError('Invalid or expired OTP')

        # Mark OTP as used
        otp.mark_used()

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_sensitive=True),
            'is_first_login': user.is_first_login
        }

    @staticmethod
    def forgot_password(email):
        """Send password reset OTP"""
        user = User.query.filter_by(email=email.lower()).first()

        if not user:
            # Don't reveal if email exists
            return {'message': 'If the email exists, an OTP has been sent'}

        otp = OTP.create_otp(user.id, OTP.PURPOSE_PASSWORD_RESET)

        from app.modules.notifications.services import NotificationService
        NotificationService.send_password_reset_email(user, otp.code)

        return {'message': 'If the email exists, an OTP has been sent'}

    @staticmethod
    def reset_password(email, otp_code, new_password, confirm_password):
        """Reset password using OTP"""
        if new_password != confirm_password:
            raise ValidationError('Passwords do not match')

        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(error)

        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            raise AuthenticationError('Invalid email')

        otp = OTP.query.filter_by(
            user_id=user.id,
            code=otp_code,
            purpose=OTP.PURPOSE_PASSWORD_RESET,
            is_used=False
        ).first()

        if not otp or not otp.is_valid():
            raise AuthenticationError('Invalid or expired OTP')

        otp.mark_used()
        user.set_password(new_password)
        db.session.commit()

        return {'message': 'Password reset successfully'}


class UserService:
    """Service for user operations"""

    @staticmethod
    def invite_user(email, role_name, invited_by, first_name=None, last_name=None):
        """
        Invite a new user (Super Admin/Admin only).
        Generates password and sends invite email.
        """
        email = email.lower()

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ConflictError('User with this email already exists')

        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValidationError(f'Invalid role: {role_name}')

        # Generate password
        password = generate_password()

        # Create user
        user = User(
            email=email,
            role_id=role.id,
            first_name=first_name,
            last_name=last_name,
            invited_by_id=invited_by.id,
            is_first_login=True,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Send invite email
        from app.modules.notifications.services import NotificationService
        NotificationService.send_invite_email(user, password)

        return user

    @staticmethod
    def complete_onboarding(user, data):
        """
        Complete first-time onboarding.
        Updates password, profile, and creates service requests.
        """
        if data['new_password'] != data['confirm_password']:
            raise ValidationError('Passwords do not match')

        is_valid, error = validate_password_strength(data['new_password'])
        if not is_valid:
            raise ValidationError(error)

        # Update password
        user.set_password(data['new_password'])

        # Update profile
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.phone = data.get('phone')
        user.address = data.get('address')
        user.company_name = data.get('company_name')

        # Update additional fields
        user.personal_email = data.get('personal_email')
        user.date_of_birth = data.get('date_of_birth')
        user.occupation = data.get('occupation')
        user.visa_status = data.get('visa_status')
        user.tfn = data.get('tfn')
        user.bsb = data.get('bsb')
        user.bank_account_number = data.get('bank_account_number')
        user.bank_account_holder_name = data.get('bank_account_holder_name')

        # Update document URLs from onboarding uploads
        if data.get('passport_url'):
            user.passport_url = data.get('passport_url')
        if data.get('bank_statement_url'):
            user.bank_statement_url = data.get('bank_statement_url')
        if data.get('driving_licence_url'):
            user.driving_licence_url = data.get('driving_licence_url')

        # Terms acceptance
        if data.get('terms_accepted'):
            user.terms_accepted = True
            user.terms_accepted_at = datetime.utcnow()

        # Mark onboarding complete
        user.is_first_login = False
        user.is_verified = True

        db.session.commit()

        # Create service requests
        if data.get('service_ids'):
            from app.modules.services.services import ServiceRequestService
            ServiceRequestService.create_requests_for_user(user, data['service_ids'])

        return user

    @staticmethod
    def update_profile(user, data):
        """Update user profile"""
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'company_name' in data:
            user.company_name = data['company_name']

        db.session.commit()
        return user

    @staticmethod
    def update_password(user, current_password, new_password, confirm_password):
        """Update user password"""
        if not user.check_password(current_password):
            raise AuthenticationError('Current password is incorrect')

        if new_password != confirm_password:
            raise ValidationError('Passwords do not match')

        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(error)

        user.set_password(new_password)
        db.session.commit()

        return {'message': 'Password updated successfully'}

    @staticmethod
    def upload_document(user, file):
        """Upload ID document for user"""
        from app.modules.user.utils import save_uploaded_file

        try:
            file_path = save_uploaded_file(file, subfolder='documents')
            user.id_document_url = file_path
            db.session.commit()
            return {'document_url': file_path}
        except ValueError as e:
            raise ValidationError(str(e))

    @staticmethod
    def get_users(role_filter=None, page=1, per_page=20):
        """Get paginated list of users"""
        query = User.query

        if role_filter:
            role = Role.query.filter_by(name=role_filter).first()
            if role:
                query = query.filter_by(role_id=role.id)

        query = query.order_by(User.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('User not found')
        return user

    @staticmethod
    def toggle_user_status(user_id, is_active):
        """Activate or deactivate a user"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('User not found')

        user.is_active = is_active
        db.session.commit()

        return user

    @staticmethod
    def get_accountants():
        """Get all active accountants"""
        accountant_role = Role.query.filter_by(name=Role.ACCOUNTANT).first()
        if not accountant_role:
            return []

        return User.query.filter_by(
            role_id=accountant_role.id,
            is_active=True
        ).all()
