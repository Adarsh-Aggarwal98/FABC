"""
ClientEntity Model
===================
Model for client organizations (companies, trusts, SMSFs, etc.).
"""

import uuid
from datetime import datetime, date
from app.extensions import db


class ClientEntity(db.Model):
    """
    Represents a client organization (company, trust, SMSF, etc.) being serviced.
    Persists across POC changes and enables tracking work for an organization.
    """
    __tablename__ = 'client_entities'

    # Entity type constants
    TYPE_COMPANY = 'COMPANY'
    TYPE_TRUST = 'TRUST'
    TYPE_SMSF = 'SMSF'
    TYPE_PARTNERSHIP = 'PARTNERSHIP'
    TYPE_INDIVIDUAL = 'INDIVIDUAL'
    TYPE_SOLE_TRADER = 'SOLE_TRADER'
    TYPE_OTHER = 'OTHER'

    VALID_TYPES = [
        TYPE_COMPANY, TYPE_TRUST, TYPE_SMSF, TYPE_PARTNERSHIP,
        TYPE_INDIVIDUAL, TYPE_SOLE_TRADER, TYPE_OTHER
    ]

    # Trust type constants
    TRUST_DISCRETIONARY = 'discretionary'
    TRUST_UNIT = 'unit'
    TRUST_HYBRID = 'hybrid'
    TRUST_FIXED = 'fixed'

    VALID_TRUST_TYPES = [TRUST_DISCRETIONARY, TRUST_UNIT, TRUST_HYBRID, TRUST_FIXED]

    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Company relationship (which practice manages this entity)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Entity identification
    name = db.Column(db.String(200), nullable=False)
    trading_name = db.Column(db.String(200))
    entity_type = db.Column(db.String(50), nullable=False, default=TYPE_COMPANY)

    # Australian business identifiers
    abn = db.Column(db.String(20))
    acn = db.Column(db.String(20))
    tfn = db.Column(db.String(20))

    # Trust-specific fields
    trust_type = db.Column(db.String(50))
    trustee_name = db.Column(db.String(200))
    trust_deed_date = db.Column(db.Date)

    # Contact information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))

    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postcode = db.Column(db.String(10))
    country = db.Column(db.String(100), default='Australia')

    # Financial year end
    financial_year_end_month = db.Column(db.Integer, default=6)
    financial_year_end_day = db.Column(db.Integer, default=30)

    # External integrations
    xero_contact_id = db.Column(db.String(100))

    # Status & metadata
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))

    # Relationships
    company = db.relationship('Company', backref=db.backref('client_entities', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_client_entities')
    contacts = db.relationship('ClientEntityContact', backref='client_entity', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='ClientEntityContact.effective_from.desc()')

    def get_primary_contact(self):
        """Get the current primary contact for this entity."""
        from .client_entity_contact import ClientEntityContact
        return ClientEntityContact.query.filter_by(
            client_entity_id=self.id,
            is_primary=True,
            is_active=True
        ).filter(
            ClientEntityContact.effective_to.is_(None)
        ).first()

    def get_active_contacts(self):
        """Get all currently active contacts for this entity."""
        from .client_entity_contact import ClientEntityContact
        return ClientEntityContact.query.filter_by(
            client_entity_id=self.id,
            is_active=True
        ).filter(
            ClientEntityContact.effective_to.is_(None)
        ).order_by(ClientEntityContact.is_primary.desc()).all()

    def get_contact_at_date(self, target_date):
        """Get the primary contact as of a specific date."""
        from .client_entity_contact import ClientEntityContact
        return ClientEntityContact.query.filter_by(
            client_entity_id=self.id,
            is_primary=True
        ).filter(
            ClientEntityContact.effective_from <= target_date,
            db.or_(
                ClientEntityContact.effective_to.is_(None),
                ClientEntityContact.effective_to >= target_date
            )
        ).first()

    @property
    def full_address(self):
        """Get formatted full address."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city or self.state or self.postcode:
            city_state = ', '.join(filter(None, [self.city, self.state, self.postcode]))
            parts.append(city_state)
        if self.country and self.country != 'Australia':
            parts.append(self.country)
        return ', '.join(parts) if parts else None

    def to_dict(self, include_contacts=False, include_primary_contact=True, include_company=False):
        """Convert entity to dictionary."""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'trading_name': self.trading_name,
            'entity_type': self.entity_type,
            'abn': self.abn,
            'acn': self.acn,
            'tfn': self.tfn,
            'email': self.email,
            'phone': self.phone,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postcode': self.postcode,
                'country': self.country,
                'full_address': self.full_address
            },
            'financial_year_end': {
                'month': self.financial_year_end_month,
                'day': self.financial_year_end_day
            },
            'xero_contact_id': self.xero_contact_id,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Add trust-specific fields if applicable
        if self.entity_type == self.TYPE_TRUST:
            data['trust_details'] = {
                'trust_type': self.trust_type,
                'trustee_name': self.trustee_name,
                'trust_deed_date': self.trust_deed_date.isoformat() if self.trust_deed_date else None
            }

        # Include primary contact
        if include_primary_contact:
            primary_contact = self.get_primary_contact()
            if primary_contact:
                data['primary_contact'] = primary_contact.to_dict()
            else:
                data['primary_contact'] = None

        # Include all contacts
        if include_contacts:
            data['contacts'] = [c.to_dict() for c in self.contacts.all()]

        # Include company
        if include_company and self.company:
            data['company'] = {
                'id': self.company.id,
                'name': self.company.name
            }

        return data

    def __repr__(self):
        return f'<ClientEntity {self.name} ({self.entity_type})>'
