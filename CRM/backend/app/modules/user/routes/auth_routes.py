"""
Auth Routes - Authentication API Endpoints

Authentication Endpoints (/api/auth):
-----------------------------------
POST /api/auth/login
    Login step 1: Validate credentials and send OTP (if 2FA enabled).

POST /api/auth/verify-otp
    Login step 2: Verify OTP and get JWT tokens.

POST /api/auth/forgot-password
    Request password reset OTP.

POST /api/auth/reset-password
    Reset password with OTP.

GET  /api/auth/me
    Get current authenticated user info.

POST /api/auth/refresh
    Refresh access token using refresh token.
"""
import logging
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from marshmallow import ValidationError as MarshmallowValidationError

from . import auth_bp
from app.modules.audit.services import AccessLogger
from app.modules.user.usecases import (
    LoginUseCase,
    VerifyOTPUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
)
from app.modules.user.schemas import (
    LoginSchema, VerifyOTPSchema, ForgotPasswordSchema, ResetPasswordSchema, UserSchema
)
from app.common.decorators import get_current_user
from app.common.responses import success_response, error_response

# Module-level logger
logger = logging.getLogger(__name__)


def _get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes"""
    status_map = {
        'NOT_FOUND': 404,
        'INVALID_CREDENTIALS': 401,
        'INVALID_OTP': 401,
        'INVALID_EMAIL': 400,
        'INVALID_PASSWORD': 401,
        'ACCOUNT_INACTIVE': 403,
        'EMAIL_EXISTS': 409,
        'INVALID_ROLE': 400,
        'PASSWORD_MISMATCH': 400,
        'WEAK_PASSWORD': 400,
        'ALREADY_COMPLETED': 400,
        'FORBIDDEN': 403
    }
    return status_map.get(error_code, 400)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - Step 1: Validate credentials and send OTP.

    If 2FA is enabled, sends OTP to user's email and returns
    requires_2fa=True. Otherwise returns JWT tokens directly.
    """
    logger.info("POST /auth/login - Login attempt")
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
        logger.debug(f"Login attempt for email={data['email']}")

        usecase = LoginUseCase()
        result = usecase.execute(data['email'], data['password'])

        if result.success:
            # If 2FA is disabled and tokens are returned directly, log the access
            if not result.data.get('requires_2fa') and result.data.get('user'):
                logger.info(f"Login successful for user_id={result.data['user']['id']} (2FA disabled)")
                try:
                    AccessLogger.log_login(
                        user_id=result.data['user']['id'],
                        session_id=result.data.get('access_token', '')[:50]
                    )
                except Exception as e:
                    logger.warning(f"Failed to log access: {str(e)}")
            else:
                logger.info(f"Login credentials valid for {data['email']}, OTP sent")
            return success_response(result.data)
        else:
            logger.warning(f"Login failed for {data['email']}: {result.error}")
            # Log failed login attempt
            try:
                AccessLogger.log_failed_login(
                    email=data['email'],
                    failure_reason=result.error
                )
            except Exception:
                pass
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Login endpoint - Step 2: Verify OTP and get tokens"""
    try:
        schema = VerifyOTPSchema()
        data = schema.load(request.json)

        usecase = VerifyOTPUseCase()
        result = usecase.execute(data['email'], data['otp'])

        if result.success:
            # Log successful 2FA verification and login
            try:
                AccessLogger.log_login(
                    user_id=result.data['user']['id'],
                    session_id=result.data.get('access_token', '')[:50]
                )
            except Exception:
                pass
            return success_response(result.data)
        else:
            # Log failed 2FA attempt
            try:
                AccessLogger.log_failed_login(
                    email=data['email'],
                    failure_reason=result.error
                )
            except Exception:
                pass
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset OTP"""
    try:
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)

        usecase = ForgotPasswordUseCase()
        result = usecase.execute(data['email'])

        return success_response(result.data)

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with OTP"""
    try:
        schema = ResetPasswordSchema()
        data = schema.load(request.json)

        usecase = ResetPasswordUseCase()
        result = usecase.execute(
            data['email'],
            data['otp'],
            data['new_password'],
            data['confirm_password']
        )

        if result.success:
            return success_response(result.data)
        else:
            return error_response(result.error, _get_status_code(result.error_code))

    except MarshmallowValidationError as e:
        return error_response('Validation error', errors=e.messages)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """Get current authenticated user info (includes own sensitive data)"""
    user = get_current_user()
    if not user:
        return error_response('User not found', 404)

    return success_response(user.to_dict(include_sensitive=True))


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    # Log token refresh
    try:
        AccessLogger.log_token_refresh(
            user_id=user_id,
            session_id=access_token[:50]
        )
    except Exception:
        pass

    return success_response({'access_token': access_token})
