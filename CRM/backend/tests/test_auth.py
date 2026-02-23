"""
Authentication Module Tests
Tests for login, logout, OTP verification, password reset functionality.
"""
import pytest
from app.modules.user.models import User, OTP, Role
from app.extensions import db


class TestLogin:
    """Test cases for user login."""

    def test_login_valid_credentials_2fa_disabled(self, client, admin_user):
        """AUTH-001: Test login with valid credentials (2FA disabled)."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'Admin@123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Since 2FA is disabled, should get access token directly
        assert 'access_token' in data.get('data', {})

    def test_login_invalid_password(self, client, admin_user):
        """AUTH-002: Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'WrongPassword123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_login_nonexistent_user(self, client, init_database):
        """AUTH-003: Test login with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'AnyPassword123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_login_missing_email(self, client):
        """Test login with missing email field."""
        response = client.post('/api/auth/login', json={
            'password': 'Password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_login_missing_password(self, client):
        """Test login with missing password field."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post('/api/auth/login', json={
            'email': 'invalid-email',
            'password': 'Password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_login_inactive_account(self, client, inactive_user):
        """AUTH-010: Test login with deactivated account."""
        response = client.post('/api/auth/login', json={
            'email': 'inactive@test.com',
            'password': 'Inactive@123'
        })

        # Should be rejected
        assert response.status_code in [401, 403]
        data = response.get_json()
        assert data['success'] is False


class TestOTPVerification:
    """Test cases for OTP verification."""

    def test_verify_otp_valid(self, app, client, admin_user):
        """AUTH-004: Test OTP verification with valid code."""
        with app.app_context():
            # Create a valid OTP
            user = User.query.filter_by(email='admin@test.com').first()
            otp = OTP.create_otp(user.id, OTP.PURPOSE_LOGIN)
            otp_code = otp.code

            response = client.post('/api/auth/verify-otp', json={
                'email': 'admin@test.com',
                'otp': otp_code
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'access_token' in data.get('data', {})

    def test_verify_otp_invalid_code(self, client, admin_user):
        """Test OTP verification with invalid code."""
        response = client.post('/api/auth/verify-otp', json={
            'email': 'admin@test.com',
            'otp': '000000'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_verify_otp_expired(self, app, client, admin_user):
        """AUTH-005: Test OTP verification with expired code."""
        from datetime import datetime, timedelta

        with app.app_context():
            user = User.query.filter_by(email='admin@test.com').first()
            # Create an expired OTP
            otp = OTP(
                user_id=user.id,
                code='123456',
                purpose=OTP.PURPOSE_LOGIN,
                expires_at=datetime.utcnow() - timedelta(minutes=5)  # Already expired
            )
            db.session.add(otp)
            db.session.commit()

            response = client.post('/api/auth/verify-otp', json={
                'email': 'admin@test.com',
                'otp': '123456'
            })

            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False


class TestForgotPassword:
    """Test cases for forgot password functionality."""

    def test_forgot_password_valid_email(self, client, admin_user):
        """AUTH-008: Test forgot password with valid email."""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'admin@test.com'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_forgot_password_nonexistent_email(self, client, init_database):
        """Test forgot password with non-existent email."""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'nonexistent@test.com'
        })

        # Should still return 200 to prevent email enumeration
        assert response.status_code == 200


class TestResetPassword:
    """Test cases for password reset functionality."""

    def test_reset_password_valid(self, app, client, admin_user):
        """AUTH-009: Test password reset with valid OTP."""
        with app.app_context():
            user = User.query.filter_by(email='admin@test.com').first()
            otp = OTP.create_otp(user.id, OTP.PURPOSE_PASSWORD_RESET)
            otp_code = otp.code

            response = client.post('/api/auth/reset-password', json={
                'email': 'admin@test.com',
                'otp': otp_code,
                'new_password': 'NewPassword@123',
                'confirm_password': 'NewPassword@123'
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True

            # Verify can login with new password
            login_response = client.post('/api/auth/login', json={
                'email': 'admin@test.com',
                'password': 'NewPassword@123'
            })
            assert login_response.status_code == 200

    def test_reset_password_mismatch(self, app, client, admin_user):
        """Test password reset with mismatched passwords."""
        with app.app_context():
            user = User.query.filter_by(email='admin@test.com').first()
            otp = OTP.create_otp(user.id, OTP.PURPOSE_PASSWORD_RESET)
            otp_code = otp.code

            response = client.post('/api/auth/reset-password', json={
                'email': 'admin@test.com',
                'otp': otp_code,
                'new_password': 'NewPassword@123',
                'confirm_password': 'DifferentPassword@123'
            })

            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False

    def test_reset_password_invalid_otp(self, client, admin_user):
        """Test password reset with invalid OTP."""
        response = client.post('/api/auth/reset-password', json={
            'email': 'admin@test.com',
            'otp': '000000',
            'new_password': 'NewPassword@123',
            'confirm_password': 'NewPassword@123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False


class TestTokenRefresh:
    """Test cases for token refresh functionality."""

    def test_refresh_token_valid(self, client, admin_user):
        """AUTH-006: Test token refresh with valid refresh token."""
        # First login to get tokens
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'Admin@123'
        })

        data = login_response.get_json()
        refresh_token = data.get('data', {}).get('refresh_token')

        if refresh_token:
            response = client.post('/api/auth/refresh',
                headers={'Authorization': f'Bearer {refresh_token}'})

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'access_token' in data.get('data', {})

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token."""
        response = client.post('/api/auth/refresh',
            headers={'Authorization': 'Bearer invalid_token'})

        assert response.status_code == 401


class TestGetCurrentUser:
    """Test cases for getting current user info."""

    def test_get_current_user_authenticated(self, client, admin_token):
        """Test getting current user with valid token."""
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'email' in data.get('data', {})

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get('/api/auth/me')

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get('/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token'})

        assert response.status_code == 401


class TestHealthCheck:
    """Test cases for API health check."""

    def test_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
