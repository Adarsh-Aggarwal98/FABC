"""
User Model - User entity definition
"""
import uuid
from datetime import datetime
from app.extensions import db
import bcrypt


class User(db.Model):
    """User model - designed to be reusable across products"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))  # Mobile number
    personal_email = db.Column(db.String(120))  # Personal email (not official)
    address = db.Column(db.Text)  # Current residential address
    company_name = db.Column(db.String(100))

    # Australian-specific information
    visa_status = db.Column(db.String(50))  # citizen, permanent_resident, temporary_resident, working_holiday, student, other
    tfn = db.Column(db.String(20))  # Tax File Number (encrypted/sensitive)
    date_of_birth = db.Column(db.Date)
    occupation = db.Column(db.String(100))

    # Bank account details (for tax refunds)
    bsb = db.Column(db.String(10))
    bank_account_number = db.Column(db.String(20))
    bank_account_holder_name = db.Column(db.String(100))

    # Documents
    id_document_url = db.Column(db.String(500))  # Legacy/general ID document
    passport_url = db.Column(db.String(500))
    bank_statement_url = db.Column(db.String(500))
    driving_licence_url = db.Column(db.String(500))

    # Terms acceptance
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_at = db.Column(db.DateTime)

    # Status flags
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_first_login = db.Column(db.Boolean, default=True)
    two_fa_enabled = db.Column(db.Boolean, default=True)
    is_external_accountant = db.Column(db.Boolean, default=False)  # External accountants skip onboarding

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Company relationship
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)

    # Client portal: which SMSF fund this user belongs to (for 'user' role clients)
    client_entity_id = db.Column(db.String(36), db.ForeignKey('client_entities.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    invited_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    invited_by = db.relationship('User', remote_side=[id], backref='invited_users', foreign_keys=[invited_by_id])

    # Senior accountant supervisor relationship (for accountants managed by senior accountants)
    supervisor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    supervisor = db.relationship('User', remote_side=[id], backref='supervised_accountants', foreign_keys=[supervisor_id])

    # OTPs
    otps = db.relationship('OTP', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Verify the password against the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @property
    def full_name(self):
        """Return the user's full name"""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name or self.last_name or self.email

    def to_dict(self, include_sensitive=False, include_company=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'personal_email': self.personal_email,
            'address': self.address,
            'company_name': self.company_name,
            'company_id': self.company_id,
            'role': self.role.name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_first_login': self.is_first_login,
            'is_external_accountant': self.is_external_accountant,
            'two_factor_enabled': self.two_fa_enabled,
            'visa_status': self.visa_status,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'occupation': self.occupation,
            'terms_accepted': self.terms_accepted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

        if include_sensitive:
            data['tfn'] = self.tfn
            data['bsb'] = self.bsb
            data['bank_account_number'] = self.bank_account_number
            data['bank_account_holder_name'] = self.bank_account_holder_name
            data['id_document_url'] = self.id_document_url
            data['passport_url'] = self.passport_url
            data['bank_statement_url'] = self.bank_statement_url
            data['driving_licence_url'] = self.driving_licence_url
            data['two_fa_enabled'] = self.two_fa_enabled

        if include_company and self.company:
            data['company'] = {
                'id': self.company.id,
                'name': self.company.name
            }

        # Include supervisor info for accountants
        if self.supervisor_id:
            data['supervisor_id'] = self.supervisor_id
            if self.supervisor:
                data['supervisor'] = {
                    'id': self.supervisor.id,
                    'email': self.supervisor.email,
                    'full_name': self.supervisor.full_name
                }

        return data

    def __repr__(self):
        return f'<User {self.email}>'
