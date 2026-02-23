"""
ClientEntityContact Model
==========================
Model for contact persons associated with client entities.
"""

from datetime import datetime, date
from app.extensions import db


class ClientEntityContact(db.Model):
    """
    Contact person for a client entity with effective dating for history tracking.
    Supports POC changes while preserving historical records.
    """
    __tablename__ = 'client_entity_contacts'

    # Contact type constants (reuse from CompanyContact)
    TYPE_PRIMARY = 'PRIMARY'
    TYPE_BILLING = 'BILLING'
    TYPE_TECHNICAL = 'TECHNICAL'
    TYPE_COMPLIANCE = 'COMPLIANCE'
    TYPE_OTHER = 'OTHER'

    VALID_TYPES = [TYPE_PRIMARY, TYPE_BILLING, TYPE_TECHNICAL, TYPE_COMPLIANCE, TYPE_OTHER]

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Entity relationship
    client_entity_id = db.Column(db.String(36), db.ForeignKey('client_entities.id', ondelete='CASCADE'), nullable=False)

    # Optional link to User (if they have login access)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))

    # Contact details (stored even if user_id exists, for historical record)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))

    # Classification
    contact_type = db.Column(db.String(20), default=TYPE_PRIMARY)
    is_primary = db.Column(db.Boolean, default=False)

    # Temporal tracking for POC history
    effective_from = db.Column(db.Date, nullable=False, default=date.today)
    effective_to = db.Column(db.Date)  # NULL = currently active

    # Status
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('client_entity_contacts', lazy='dynamic'))

    @property
    def full_name(self):
        """Get full name of the contact."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ''

    @property
    def is_current(self):
        """Check if contact is currently active."""
        return self.is_active and self.effective_to is None

    def end_contact(self, end_date=None, reason=None):
        """End this contact's effective period."""
        self.effective_to = end_date or date.today()
        self.is_active = False
        if reason:
            self.notes = f"{self.notes or ''}\nEnded: {reason}".strip()

    def to_dict(self, include_user=False):
        """Convert contact to dictionary."""
        data = {
            'id': self.id,
            'client_entity_id': self.client_entity_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'contact_type': self.contact_type,
            'is_primary': self.is_primary,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'is_current': self.is_current,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if self.user_id:
            data['user_id'] = self.user_id
            if include_user and self.user:
                data['user'] = {
                    'id': self.user.id,
                    'email': self.user.email,
                    'full_name': self.user.full_name
                }

        return data

    def __repr__(self):
        return f'<ClientEntityContact {self.full_name} ({self.contact_type})>'
