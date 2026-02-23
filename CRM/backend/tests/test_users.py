"""
User Management Module Tests
Tests for user CRUD operations, profile management, and user invitations.
"""
import pytest
from app.modules.user.models import User, Role
from app.extensions import db


class TestGetUserProfile:
    """Test cases for getting user profile."""

    def test_get_current_user_profile(self, client, admin_token):
        """USER-001: Test getting current user profile."""
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['email'] == 'admin@test.com'
        assert 'password_hash' not in data['data']

    def test_get_user_by_id_as_admin(self, client, admin_token, client_user):
        """Test admin can get any user by ID."""
        response = client.get(f'/api/users/{client_user.id}',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_get_user_by_id_as_client(self, client, client_token, admin_user):
        """Test client cannot get other user's profile."""
        response = client.get(f'/api/users/{admin_user.id}',
            headers={'Authorization': f'Bearer {client_token}'})

        # Should be forbidden
        assert response.status_code == 403

    def test_get_own_profile_as_client(self, client, client_token, client_user):
        """Test client can get their own profile."""
        response = client.get(f'/api/users/{client_user.id}',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200


class TestUpdateProfile:
    """Test cases for updating user profile."""

    def test_update_profile_valid(self, client, client_token):
        """USER-002: Test updating own profile with valid data."""
        response = client.patch('/api/users/profile', json={
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+61 400 123 456'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['user']['first_name'] == 'Updated'

    def test_update_profile_no_token(self, client):
        """Test updating profile without authentication."""
        response = client.patch('/api/users/profile', json={
            'first_name': 'Test'
        })

        assert response.status_code == 401


class TestInviteUser:
    """Test cases for user invitation."""

    def test_invite_user_as_admin(self, client, admin_token):
        """USER-003: Test admin inviting new user."""
        response = client.post('/api/users/invite', json={
            'email': 'newuser@test.com',
            'role': 'user',
            'first_name': 'New',
            'last_name': 'User'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'temp_password' in data['data']

    def test_invite_user_as_accountant_should_fail(self, client, accountant_token):
        """Test accountant cannot invite users."""
        response = client.post('/api/users/invite', json={
            'email': 'newuser2@test.com',
            'role': 'user',
            'first_name': 'New',
            'last_name': 'User'
        }, headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 403

    def test_invite_user_as_client_should_fail(self, client, client_token):
        """Test client cannot invite users."""
        response = client.post('/api/users/invite', json={
            'email': 'newuser3@test.com',
            'role': 'user',
            'first_name': 'New',
            'last_name': 'User'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    def test_invite_user_duplicate_email(self, client, admin_token, client_user):
        """Test inviting user with existing email."""
        response = client.post('/api/users/invite', json={
            'email': 'client@test.com',  # Already exists
            'role': 'user',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 409

    def test_admin_cannot_create_super_admin(self, client, admin_token):
        """Test admin cannot create super admin role."""
        response = client.post('/api/users/invite', json={
            'email': 'superadmin2@test.com',
            'role': 'super_admin',
            'first_name': 'Super',
            'last_name': 'Admin'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 403

    def test_super_admin_can_create_admin(self, client, super_admin_token, test_company):
        """Test super admin can create admin users."""
        response = client.post('/api/users/invite', json={
            'email': 'newadmin@test.com',
            'role': 'admin',
            'first_name': 'New',
            'last_name': 'Admin',
            'company_id': test_company.id
        }, headers={'Authorization': f'Bearer {super_admin_token}'})

        assert response.status_code == 201


class TestListUsers:
    """Test cases for listing users."""

    def test_list_users_as_admin(self, client, admin_token):
        """USER-005: Test admin can list users."""
        response = client.get('/api/users/',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Items may be in 'items' or 'data' depending on response format
        assert 'items' in data or 'data' in data

    def test_list_users_with_pagination(self, client, admin_token):
        """Test listing users with pagination."""
        response = client.get('/api/users/?page=1&per_page=5',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Pagination may be at top level or nested
        assert 'pagination' in data or 'page' in data

    def test_list_users_filter_by_role(self, client, admin_token):
        """Test filtering users by role."""
        response = client.get('/api/users/?role=accountant',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_list_users_as_client_should_fail(self, client, client_token):
        """Test client cannot list users."""
        response = client.get('/api/users/',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestToggleUserStatus:
    """Test cases for activating/deactivating users."""

    def test_deactivate_user(self, app, client, admin_token, client_user):
        """USER-006: Test admin can deactivate user."""
        response = client.post(f'/api/users/{client_user.id}/toggle-status', json={
            'is_active': False
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # Verify user is deactivated
        with app.app_context():
            user = User.query.get(client_user.id)
            assert user.is_active is False

    def test_reactivate_user(self, app, client, admin_token, inactive_user):
        """Test admin can reactivate user."""
        response = client.post(f'/api/users/{inactive_user.id}/toggle-status', json={
            'is_active': True
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_toggle_status_as_client_should_fail(self, client, client_token, admin_user):
        """Test client cannot toggle user status."""
        response = client.post(f'/api/users/{admin_user.id}/toggle-status', json={
            'is_active': False
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestListAccountants:
    """Test cases for listing accountants."""

    def test_list_accountants_as_admin(self, client, admin_token, accountant_user):
        """Test admin can list accountants."""
        response = client.get('/api/users/accountants',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'accountants' in data['data']


class TestChangePassword:
    """Test cases for changing password."""

    def test_change_password_valid(self, client, admin_token):
        """Test changing password with valid current password."""
        response = client.post('/api/users/change-password', json={
            'current_password': 'Admin@123',
            'new_password': 'NewAdmin@456',
            'confirm_password': 'NewAdmin@456'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, admin_token):
        """Test changing password with wrong current password."""
        response = client.post('/api/users/change-password', json={
            'current_password': 'WrongPassword',
            'new_password': 'NewAdmin@456',
            'confirm_password': 'NewAdmin@456'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 401

    def test_change_password_mismatch(self, client, admin_token):
        """Test changing password with mismatched passwords."""
        response = client.post('/api/users/change-password', json={
            'current_password': 'Admin@123',
            'new_password': 'NewAdmin@456',
            'confirm_password': 'DifferentPassword'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 400


class TestClientNotes:
    """Test cases for client notes."""

    def test_create_client_note(self, client, accountant_token, client_user):
        """Test accountant can create note on client."""
        response = client.post(f'/api/users/{client_user.id}/notes', json={
            'content': 'Test note content',
            'is_pinned': False
        }, headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    def test_get_client_notes(self, client, accountant_token, client_user):
        """Test accountant can get client notes."""
        # First create a note
        client.post(f'/api/users/{client_user.id}/notes', json={
            'content': 'Test note'
        }, headers={'Authorization': f'Bearer {accountant_token}'})

        response = client.get(f'/api/users/{client_user.id}/notes',
            headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 200

    def test_client_cannot_create_notes(self, client, client_token, admin_user):
        """Test client cannot create notes."""
        response = client.post(f'/api/users/{admin_user.id}/notes', json={
            'content': 'Test note'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestMultiTenantAccess:
    """Test cases for multi-tenant isolation."""

    def test_cannot_access_user_from_different_company(self, app, client, admin_token):
        """USER-007: Test cannot access users from different company."""
        with app.app_context():
            # Create a different company
            from app.modules.company.models import Company

            other_company = Company(
                name='Other Company',
                abn='98765432101',
                email='info@other.com',
                plan_type='starter'
            )
            db.session.add(other_company)
            db.session.commit()

            # Create user in different company
            role = Role.query.filter_by(name=Role.USER).first()
            other_user = User(
                email='otheruser@other.com',
                role_id=role.id,
                company_id=other_company.id,
                first_name='Other',
                last_name='User',
                is_verified=True,
                two_fa_enabled=False
            )
            other_user.set_password('Other@123')
            db.session.add(other_user)
            db.session.commit()

            # Try to access other company's user
            response = client.get(f'/api/users/{other_user.id}',
                headers={'Authorization': f'Bearer {admin_token}'})

            # Should be forbidden or not found
            assert response.status_code in [403, 404]
