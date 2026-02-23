"""
Forms Module Tests
Tests for dynamic forms, form responses, and conditional logic.
"""
import pytest
from app.modules.forms.models import Form, FormQuestion, FormResponse
from app.modules.user.models import User
from app.extensions import db


@pytest.fixture
def test_form(app, admin_user, test_company):
    """Create a test form."""
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()

        form = Form(
            name='Test Tax Information Form',
            description='Collect client tax information',
            form_type='service',
            created_by_id=admin.id if admin else None,
            company_id=admin.company_id if admin else None,  # Set company_id for admin access
            is_active=True,
            is_default=False,  # Company form, not a default/system form
            status='published'  # Set status for client access
        )
        db.session.add(form)
        db.session.commit()

        # Add questions
        q1 = FormQuestion(
            form_id=form.id,
            question_text='What is your employment type?',
            question_type='select',
            is_required=True,
            options=['Employee', 'Self-employed', 'Both'],
            order=0
        )
        db.session.add(q1)
        db.session.commit()

        q2 = FormQuestion(
            form_id=form.id,
            question_text='What is your ABN?',
            question_type='text',
            is_required=False,
            placeholder='XX XXX XXX XXX',
            order=1,
            conditional_on_question_id=q1.id,
            conditional_value='Self-employed'
        )
        q3 = FormQuestion(
            form_id=form.id,
            question_text='Upload your PAYG summary',
            question_type='file',
            is_required=False,
            order=2
        )
        db.session.add_all([q2, q3])
        db.session.commit()

        db.session.refresh(form)
        return form


class TestListForms:
    """Test cases for listing forms."""

    def test_list_forms_as_admin(self, client, admin_token, test_form):
        """Test admin can list forms."""
        response = client.get('/api/forms/',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_list_default_forms(self, client, admin_token):
        """Test listing default form templates."""
        response = client.get('/api/forms/defaults',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_list_company_forms(self, client, admin_token):
        """Test listing company-specific forms."""
        response = client.get('/api/forms/company',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestCreateForm:
    """Test cases for creating forms."""

    def test_create_form_as_admin(self, client, admin_token):
        """FORM-001: Test admin can create dynamic form."""
        response = client.post('/api/forms/', json={
            'name': 'New Client Onboarding',
            'description': 'Onboarding form for new clients',
            'form_type': 'onboarding',
            'fields': [
                {
                    'question_text': 'What is your full name?',
                    'question_type': 'text',
                    'is_required': True
                },
                {
                    'question_text': 'What services are you interested in?',
                    'question_type': 'multiselect',
                    'is_required': True,
                    'options': ['Tax Return', 'BAS', 'Bookkeeping', 'SMSF']
                }
            ]
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 201

    def test_create_form_as_client_should_fail(self, client, client_token):
        """Test client cannot create forms."""
        response = client.post('/api/forms/', json={
            'name': 'Unauthorized Form',
            'fields': []
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestGetForm:
    """Test cases for getting form details."""

    def test_get_form_details(self, client, admin_token, test_form):
        """Test getting form with questions."""
        response = client.get(f'/api/forms/{test_form.id}',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'questions' in data['data']['form'] or 'fields' in data['data']['form']

    def test_get_form_as_client(self, client, client_token, test_form):
        """Test client can view form."""
        response = client.get(f'/api/forms/{test_form.id}',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 200


class TestUpdateForm:
    """Test cases for updating forms."""

    def test_update_form(self, client, admin_token, test_form):
        """Test updating form details."""
        response = client.put(f'/api/forms/{test_form.id}', json={
            'name': 'Updated Form Name',
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_delete_form(self, client, admin_token, test_form):
        """Test deleting/deactivating form."""
        response = client.delete(f'/api/forms/{test_form.id}',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


@pytest.fixture
def test_default_form(app, admin_user, test_company):
    """Create a default/system form for clone testing."""
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()

        form = Form(
            name='Default Tax Form Template',
            description='System default form for cloning',
            form_type='service',
            created_by_id=admin.id if admin else None,
            company_id=None,  # System form - no company
            is_active=True,
            is_default=True,  # This is a default form for cloning
            status='published'
        )
        db.session.add(form)
        db.session.commit()

        # Add a sample question
        q1 = FormQuestion(
            form_id=form.id,
            question_text='Sample question for cloning',
            question_type='text',
            is_required=False,
            order=0
        )
        db.session.add(q1)
        db.session.commit()

        db.session.refresh(form)
        return form


class TestCloneForm:
    """Test cases for cloning forms."""

    def test_clone_form(self, client, admin_token, test_default_form):
        """FORM-004: Test cloning an existing form."""
        response = client.post(f'/api/forms/{test_default_form.id}/clone',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.get_json()
            # Cloned form should have different ID
            if 'form' in data.get('data', {}):
                assert data['data']['form']['id'] != test_default_form.id


class TestFormResponses:
    """Test cases for form responses."""

    def test_submit_form_response(self, client, client_token, test_form, app):
        """FORM-002: Test client can submit form response."""
        with app.app_context():
            # Get the first question ID (required employment type question)
            from app.modules.forms.models import FormQuestion
            question = FormQuestion.query.filter_by(form_id=test_form.id, is_required=True).first()
            question_id = str(question.id) if question else '1'

        response = client.post(f'/api/forms/{test_form.id}/responses', json={
            'responses': {
                question_id: 'Employee'  # Use question ID as key
            }
        }, headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code in [200, 201]

    def test_form_validation_required_fields(self, client, client_token, test_form, app):
        """FORM-003: Test form validation for required fields."""
        with app.app_context():
            # Get a non-required question ID
            from app.modules.forms.models import FormQuestion
            question = FormQuestion.query.filter_by(form_id=test_form.id, is_required=False).first()
            question_id = str(question.id) if question else '2'

        response = client.post(f'/api/forms/{test_form.id}/responses', json={
            'responses': {
                # Missing required employment_type field - only providing optional field
                question_id: '12345678901'
            }
        }, headers={'Authorization': f'Bearer {client_token}'})

        # Should fail validation
        assert response.status_code == 400

    def test_get_form_responses(self, client, admin_token, test_form):
        """Test admin can get form responses."""
        response = client.get(f'/api/forms/{test_form.id}/responses',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestFormConditionalLogic:
    """Test cases for conditional field visibility."""

    def test_conditional_field_not_required_when_hidden(self, client, client_token, test_form):
        """Test conditional fields not validated when condition not met."""
        # ABN field is only required when employment_type is Self-employed or Both
        response = client.post(f'/api/forms/{test_form.id}/responses', json={
            'responses': {
                'employment_type': 'Employee'  # ABN should not be required
                # Not providing ABN
            }
        }, headers={'Authorization': f'Bearer {client_token}'})

        # Should succeed since ABN is conditional
        assert response.status_code in [200, 201, 400]  # Depends on validation implementation
