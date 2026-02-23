"""
Pytest fixtures and configuration for Accountant CRM tests.
"""
import pytest
import os
from datetime import datetime

# Set testing environment before importing app
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from app.extensions import db
from app.modules.user.models import User, Role, OTP
from app.modules.company.models import Company
from app.modules.services.models import Invoice, InvoiceLineItem, InvoicePayment


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        db.create_all()
        # Create default roles
        Role.get_or_create_default_roles()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        yield db.session

        db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database with test data."""
    with app.app_context():
        # Clear existing data (order matters for foreign key constraints)
        db.session.query(InvoicePayment).delete()
        db.session.query(InvoiceLineItem).delete()
        db.session.query(Invoice).delete()
        db.session.query(OTP).delete()
        db.session.query(User).delete()
        db.session.query(Company).delete()
        db.session.commit()

        yield db

        # Cleanup after test
        db.session.query(InvoicePayment).delete()
        db.session.query(InvoiceLineItem).delete()
        db.session.query(Invoice).delete()
        db.session.query(OTP).delete()
        db.session.query(User).delete()
        db.session.query(Company).delete()
        db.session.commit()


@pytest.fixture
def test_company(app, init_database):
    """Create a test company."""
    with app.app_context():
        company = Company(
            name='Test Company',
            trading_name='Test Co',
            abn='12345678901',
            email='info@testcompany.com',
            phone='+61 2 1234 5678',
            address_line1='123 Test Street',
            city='Sydney',
            state='NSW',
            postcode='2000',
            country='Australia',
            plan_type='standard',
            max_users=10,
            max_clients=100
        )
        db.session.add(company)
        db.session.commit()

        # Refresh to get the ID
        db.session.refresh(company)
        return company


@pytest.fixture
def super_admin_user(app, init_database):
    """Create a super admin user."""
    with app.app_context():
        role = Role.query.filter_by(name=Role.SUPER_ADMIN).first()
        user = User(
            email='superadmin@test.com',
            role_id=role.id,
            first_name='Super',
            last_name='Admin',
            is_verified=True,
            is_first_login=False,
            two_fa_enabled=False
        )
        user.set_password('SuperAdmin@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def admin_user(app, init_database, test_company):
    """Create an admin user."""
    with app.app_context():
        role = Role.query.filter_by(name=Role.ADMIN).first()
        company = Company.query.filter_by(name='Test Company').first()

        user = User(
            email='admin@test.com',
            role_id=role.id,
            company_id=company.id,
            first_name='Admin',
            last_name='User',
            is_verified=True,
            is_first_login=False,
            two_fa_enabled=False
        )
        user.set_password('Admin@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def accountant_user(app, init_database, test_company):
    """Create an accountant user."""
    with app.app_context():
        role = Role.query.filter_by(name=Role.ACCOUNTANT).first()
        company = Company.query.filter_by(name='Test Company').first()

        user = User(
            email='accountant@test.com',
            role_id=role.id,
            company_id=company.id,
            first_name='John',
            last_name='Accountant',
            is_verified=True,
            is_first_login=False,
            two_fa_enabled=False
        )
        user.set_password('Accountant@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def client_user(app, init_database, test_company):
    """Create a client user."""
    with app.app_context():
        role = Role.query.filter_by(name=Role.USER).first()
        company = Company.query.filter_by(name='Test Company').first()

        user = User(
            email='client@test.com',
            role_id=role.id,
            company_id=company.id,
            first_name='Test',
            last_name='Client',
            phone='+61 412 345 678',
            is_verified=True,
            is_first_login=False,
            two_fa_enabled=False
        )
        user.set_password('Client@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def inactive_user(app, init_database, test_company):
    """Create an inactive user."""
    with app.app_context():
        role = Role.query.filter_by(name=Role.USER).first()
        company = Company.query.filter_by(name='Test Company').first()

        user = User(
            email='inactive@test.com',
            role_id=role.id,
            company_id=company.id,
            first_name='Inactive',
            last_name='User',
            is_verified=True,
            is_first_login=False,
            is_active=False,
            two_fa_enabled=False
        )
        user.set_password('Inactive@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


def get_auth_token(client, email, password):
    """Helper function to get authentication token."""
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    data = response.get_json()
    if data.get('success') and data.get('data', {}).get('access_token'):
        return data['data']['access_token']
    return None


def get_auth_headers(token):
    """Helper function to get authorization headers."""
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def super_admin_token(client, super_admin_user):
    """Get authentication token for super admin."""
    token = get_auth_token(client, 'superadmin@test.com', 'SuperAdmin@123')
    return token


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin."""
    token = get_auth_token(client, 'admin@test.com', 'Admin@123')
    return token


@pytest.fixture
def accountant_token(client, accountant_user):
    """Get authentication token for accountant."""
    token = get_auth_token(client, 'accountant@test.com', 'Accountant@123')
    return token


@pytest.fixture
def client_token(client, client_user):
    """Get authentication token for client."""
    token = get_auth_token(client, 'client@test.com', 'Client@123')
    return token
