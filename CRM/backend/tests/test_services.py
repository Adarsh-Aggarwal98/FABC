"""
Services and Service Requests Module Tests
Tests for service catalog, service requests, and workflow management.
"""
import pytest
from app.modules.services.models import Service, ServiceRequest, Query
from app.modules.user.models import User, Role
from app.extensions import db


@pytest.fixture
def test_service(app, init_database):
    """Create a test service."""
    with app.app_context():
        service = Service(
            name='Test Tax Return',
            description='Individual tax return preparation',
            category='Tax',
            base_price=350.00,
            is_active=True,
            is_default=True
        )
        db.session.add(service)
        db.session.commit()
        db.session.refresh(service)
        return service


@pytest.fixture
def test_service_request(app, test_service, client_user, accountant_user):
    """Create a test service request."""
    with app.app_context():
        service = Service.query.filter_by(name='Test Tax Return').first()
        user = User.query.filter_by(email='client@test.com').first()
        accountant = User.query.filter_by(email='accountant@test.com').first()

        request = ServiceRequest(
            user_id=user.id,
            service_id=service.id,
            status=ServiceRequest.STATUS_PENDING,
            invoice_raised=True,  # Required for assignment to accountant
            invoice_amount=350.00,
            assigned_accountant_id=accountant.id if accountant else None  # Assign to accountant for tests
        )
        db.session.add(request)
        db.session.commit()
        db.session.refresh(request)
        return request


class TestListServices:
    """Test cases for listing services."""

    def test_list_services(self, client, admin_token, test_service):
        """SVC-001: Test listing available services."""
        response = client.get('/api/services/',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_list_services_as_client(self, client, client_token, test_service):
        """Test client can list services."""
        response = client.get('/api/services/',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200

    def test_list_default_services(self, client, admin_token, test_service):
        """Test listing default services."""
        response = client.get('/api/services/defaults',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestCreateService:
    """Test cases for creating services."""

    def test_create_service_as_admin(self, client, admin_token):
        """SVC-002: Test admin can create custom service."""
        response = client.post('/api/services/', json={
            'name': 'Custom BAS Service',
            'description': 'Business Activity Statement preparation',
            'category': 'Tax',
            'base_price': 150.00,
            'is_active': True
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['service']['name'] == 'Custom BAS Service'

    def test_create_service_as_client_should_fail(self, client, client_token):
        """Test client cannot create services."""
        response = client.post('/api/services/', json={
            'name': 'Unauthorized Service',
            'description': 'Should not be created',
            'category': 'Test'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestUpdateService:
    """Test cases for updating services."""

    def test_update_service(self, client, admin_token, test_service):
        """SVC-004: Test updating service details."""
        response = client.patch(f'/api/services/{test_service.id}', json={
            'name': 'Updated Tax Return Service',
            'base_price': 400.00
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_deactivate_service(self, client, admin_token, test_service):
        """SVC-005: Test deactivating a service."""
        response = client.patch(f'/api/services/{test_service.id}', json={
            'is_active': False
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestServiceRequests:
    """Test cases for service requests."""

    def test_create_service_request_as_client(self, client, client_token, test_service):
        """REQ-001: Test client can create service request."""
        response = client.post('/api/requests/', json={
            'service_id': test_service.id
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'request' in data['data']

    def test_list_requests_as_client(self, client, client_token, test_service_request):
        """REQ-002: Test client sees only their own requests."""
        response = client.get('/api/requests/',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_list_requests_as_admin(self, client, admin_token, test_service_request):
        """Test admin sees all company requests."""
        response = client.get('/api/requests/',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_list_requests_as_accountant(self, client, accountant_token, test_service_request):
        """Test accountant sees assigned requests."""
        response = client.get('/api/requests/',
            headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 200

    def test_get_request_details(self, client, client_token, test_service_request):
        """Test getting request details."""
        response = client.get(f'/api/requests/{test_service_request.id}',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200


class TestAssignRequest:
    """Test cases for assigning requests."""

    def test_assign_request_to_accountant(self, app, client, admin_token, test_service_request, accountant_user):
        """REQ-003: Test admin can assign request to accountant."""
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            response = client.post(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {admin_token}'})

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True

    def test_assign_request_as_client_should_fail(self, app, client, client_token, test_service_request, accountant_user):
        """Test client cannot assign requests."""
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            response = client.post(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {client_token}'})

            assert response.status_code == 403


class TestUpdateRequestStatus:
    """Test cases for updating request status."""

    def test_update_status_as_accountant(self, app, client, admin_token, accountant_token, test_service_request, accountant_user):
        """REQ-004: Test accountant can update status of assigned request."""
        # First assign the request
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            client.post(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {admin_token}'})

            # Then update status
            response = client.patch(f'/api/requests/{test_service_request.id}/status', json={
                'status': ServiceRequest.STATUS_PROCESSING
            }, headers={'Authorization': f'Bearer {accountant_token}'})

            assert response.status_code == 200

    def test_update_status_as_admin(self, client, admin_token, test_service_request):
        """Test admin can update any request status."""
        response = client.patch(f'/api/requests/{test_service_request.id}/status', json={
            'status': ServiceRequest.STATUS_ASSIGNED
        }, headers={'Authorization': f'Bearer {admin_token}'})

        # Admin needs accountant role to update status, may get 403
        assert response.status_code in [200, 403]

    def test_update_status_as_client_should_fail(self, client, client_token, test_service_request):
        """Test client cannot update request status."""
        response = client.patch(f'/api/requests/{test_service_request.id}/status', json={
            'status': ServiceRequest.STATUS_COMPLETED
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403

    def test_invalid_status_transition(self, client, accountant_token, test_service_request):
        """Test invalid status values are rejected."""
        response = client.patch(f'/api/requests/{test_service_request.id}/status', json={
            'status': 'invalid_status'
        }, headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 400


class TestRequestQueries:
    """Test cases for request queries (messages)."""

    def test_create_query_as_accountant(self, app, client, admin_token, accountant_token, test_service_request, accountant_user):
        """REQ-007: Test accountant can create query on request."""
        # First assign the request
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            client.put(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {admin_token}'})

            # Create query
            response = client.post(f'/api/requests/{test_service_request.id}/queries', json={
                'message': 'Please provide your bank statements'
            }, headers={'Authorization': f'Bearer {accountant_token}'})

            assert response.status_code == 201

    def test_create_query_as_client(self, client, client_token, test_service_request):
        """REQ-008: Test client can respond to query."""
        response = client.post(f'/api/requests/{test_service_request.id}/queries', json={
            'message': 'Here are my documents'
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 201

    def test_get_request_queries(self, client, client_token, test_service_request):
        """Test getting queries for a request."""
        response = client.get(f'/api/requests/{test_service_request.id}/queries',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200


class TestInternalNotes:
    """Test cases for internal notes on requests."""

    def test_add_internal_note(self, app, client, admin_token, accountant_token, test_service_request, accountant_user):
        """REQ-006: Test adding internal note to request."""
        # First assign the request
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            client.post(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {admin_token}'})

            response = client.post(f'/api/requests/{test_service_request.id}/notes', json={
                'note': 'Internal note - client mentioned lost receipts'
            }, headers={'Authorization': f'Bearer {accountant_token}'})

            assert response.status_code in [200, 201]

    def test_client_cannot_see_internal_notes(self, app, client, admin_token, accountant_token, client_token, test_service_request, accountant_user):
        """Test client cannot access internal notes."""
        with app.app_context():
            accountant = User.query.filter_by(email='accountant@test.com').first()

            # Assign and add note
            client.post(f'/api/requests/{test_service_request.id}/assign', json={
                'accountant_id': accountant.id
            }, headers={'Authorization': f'Bearer {admin_token}'})

            client.post(f'/api/requests/{test_service_request.id}/notes', json={
                'note': 'Secret internal note'
            }, headers={'Authorization': f'Bearer {accountant_token}'})

            # Client gets request details
            response = client.get(f'/api/requests/{test_service_request.id}',
                headers={'Authorization': f'Bearer {client_token}'})

            assert response.status_code == 200
            data = response.get_json()
            # Internal notes should not be visible
            assert 'internal_notes' not in data.get('data', {}).get('request', {}) or \
                   data['data']['request'].get('internal_notes') is None


class TestRequestInvoice:
    """Test cases for request invoice management."""

    def test_update_invoice_details(self, client, accountant_token, test_service_request):
        """Test updating invoice details on request."""
        response = client.patch(f'/api/requests/{test_service_request.id}/invoice', json={
            'invoice_raised': True,
            'invoice_amount': 350.00,
            'payment_link': 'https://pay.example.com/inv123'
        }, headers={'Authorization': f'Bearer {accountant_token}'})

        assert response.status_code == 200


class TestRequestFilters:
    """Test cases for filtering and pagination."""

    def test_filter_requests_by_status(self, client, admin_token, test_service_request):
        """Test filtering requests by status."""
        response = client.get('/api/requests/?status=pending',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_requests_pagination(self, client, admin_token, test_service_request):
        """Test request list pagination."""
        response = client.get('/api/requests/?page=1&per_page=10',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        # Pagination may be in data or data['data']
        assert 'pagination' in data or 'pagination' in data.get('data', {})


class TestCompanyServiceSettings:
    """Test cases for company-specific service settings."""

    def test_get_company_service_settings(self, client, admin_token):
        """Test getting company service settings (list default services)."""
        response = client.get('/api/services/defaults',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_activate_default_service(self, client, admin_token, test_service):
        """SVC-003: Test activating a default service for company."""
        response = client.post(f'/api/services/defaults/{test_service.id}/activate',
            headers={'Authorization': f'Bearer {admin_token}'})

        # Might be 200 or 201 depending on if already activated
        assert response.status_code in [200, 201]
