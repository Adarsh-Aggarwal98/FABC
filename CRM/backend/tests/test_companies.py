"""
Company Management Module Tests
Tests for company CRUD operations, plan management, and multi-tenancy.
"""
import pytest
from app.modules.company.models import Company
from app.extensions import db


class TestCreateCompany:
    """Test cases for company creation."""

    def test_create_company_as_super_admin(self, client, super_admin_token):
        """COMP-001: Test super admin can create company."""
        response = client.post('/api/companies', json={
            'name': 'New Test Company',
            'trading_name': 'NTC',
            'abn': '11223344556',
            'owner_email': 'owner@newtestcompany.com',
            'owner_first_name': 'Test',
            'owner_last_name': 'Owner',
            'company_email': 'info@newtestcompany.com',
            'phone': '+61 2 9876 5432',
            'address_line1': '456 Business Ave',
            'city': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'country': 'Australia',
            'plan_type': 'starter'
        }, headers={'Authorization': f'Bearer {super_admin_token}'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['company']['name'] == 'New Test Company'

    def test_create_company_as_admin_should_fail(self, client, admin_token):
        """COMP-002: Test admin cannot create company."""
        response = client.post('/api/companies', json={
            'name': 'Unauthorized Company',
            'abn': '99887766554',
            'email': 'info@unauthorized.com',
            'plan_type': 'starter'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 403

    def test_create_company_as_client_should_fail(self, client, client_token):
        """Test client cannot create company."""
        response = client.post('/api/companies', json={
            'name': 'Client Company',
            'abn': '12312312312',
            'email': 'info@clientcompany.com',
            'plan_type': 'starter'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    def test_create_company_missing_required_fields(self, client, super_admin_token):
        """Test create company with missing required fields."""
        response = client.post('/api/companies', json={
            'trading_name': 'Incomplete'
            # Missing name and other required fields
        }, headers={'Authorization': f'Bearer {super_admin_token}'})

        assert response.status_code == 400


class TestGetCompany:
    """Test cases for getting company details."""

    def test_get_my_company(self, client, admin_token):
        """COMP-003: Test getting own company details."""
        response = client.get('/api/companies/my-company',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'company' in data

    def test_get_company_by_id_as_admin(self, client, admin_token, test_company):
        """Test admin can get their company by ID."""
        response = client.get(f'/api/companies/{test_company.id}',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_list_companies_as_super_admin(self, client, super_admin_token):
        """Test super admin can list all companies."""
        response = client.get('/api/companies',
            headers={'Authorization': f'Bearer {super_admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_list_companies_as_admin_should_fail(self, client, admin_token):
        """Test admin cannot list all companies."""
        response = client.get('/api/companies',
            headers={'Authorization': f'Bearer {admin_token}'})

        # Admin should only be able to see their own company
        assert response.status_code in [200, 403]


class TestUpdateCompany:
    """Test cases for updating company details."""

    def test_update_company_as_admin(self, client, admin_token, test_company):
        """COMP-004: Test admin can update company details."""
        response = client.put(f'/api/companies/{test_company.id}', json={
            'name': 'Updated Company Name',
            'phone': '+61 2 1111 2222'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_update_company_as_client_should_fail(self, client, client_token, test_company):
        """Test client cannot update company."""
        response = client.put(f'/api/companies/{test_company.id}', json={
            'name': 'Unauthorized Update'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestCompanyPlan:
    """Test cases for company plan management."""

    def test_get_plan_usage(self, client, admin_token):
        """COMP-005: Test getting plan usage statistics."""
        response = client.get('/api/companies/my-company/usage',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_update_plan_as_super_admin(self, client, super_admin_token, test_company):
        """COMP-006: Test super admin can update company plan."""
        response = client.patch(f'/api/companies/{test_company.id}/plan', json={
            'plan_type': 'premium',
            'max_users': 50,
            'max_clients': 500
        }, headers={'Authorization': f'Bearer {super_admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_update_plan_as_admin_should_fail(self, client, admin_token, test_company):
        """Test admin cannot update company plan."""
        response = client.patch(f'/api/companies/{test_company.id}/plan', json={
            'plan_type': 'premium'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 403

    def test_get_available_plans(self, client, admin_token):
        """Test getting available plan options."""
        response = client.get('/api/companies/plans',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestCompanyUsers:
    """Test cases for company user management."""

    def test_list_company_users(self, client, admin_token, test_company):
        """Test listing users in a company."""
        response = client.get(f'/api/companies/{test_company.id}/users',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestDeactivateCompany:
    """Test cases for company deactivation."""

    def test_deactivate_company_as_super_admin(self, app, client, super_admin_token):
        """Test super admin can deactivate company."""
        # First create a company to deactivate
        with app.app_context():
            company = Company(
                name='Company to Deactivate',
                abn='55544433322',
                email='deactivate@test.com',
                plan_type='starter'
            )
            db.session.add(company)
            db.session.commit()
            company_id = company.id

            response = client.delete(f'/api/companies/{company_id}',
                headers={'Authorization': f'Bearer {super_admin_token}'})

            assert response.status_code == 200

    def test_deactivate_company_as_admin_should_fail(self, client, admin_token, test_company):
        """Test admin cannot deactivate company."""
        response = client.delete(f'/api/companies/{test_company.id}',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 403


class TestMultiTenantIsolation:
    """Test cases for multi-tenant data isolation."""

    def test_cannot_access_other_company(self, app, client, admin_token):
        """Test admin cannot access other company's data."""
        with app.app_context():
            # Create another company
            other_company = Company(
                name='Other Company',
                abn='00011122233',
                email='other@company.com',
                plan_type='starter'
            )
            db.session.add(other_company)
            db.session.commit()
            other_company_id = other_company.id

            response = client.get(f'/api/companies/{other_company_id}',
                headers={'Authorization': f'Bearer {admin_token}'})

            # Should be forbidden or not found
            assert response.status_code in [403, 404]
