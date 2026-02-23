"""
CompanyContact Model
====================

Company contact model for managing multiple contacts per company with role-based types.
"""
import uuid
from datetime import datetime
from app.extensions import db
from app.modules.company.models.enums import ContactType


class CompanyContact(db.Model):
    """Company contact model for managing multiple contacts per company with role-based types"""
    __tablename__ = 'company_contacts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Contact details
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))  # Job title

    # Contact classification
    contact_type = db.Column(db.Enum(ContactType), default=ContactType.PRIMARY)
    is_primary = db.Column(db.Boolean, default=False)

    # Temporal tracking
    effective_from = db.Column(db.Date)
    effective_to = db.Column(db.Date)  # NULL means currently active

    # Status
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    company = db.relationship('Company', backref=db.backref('contacts', lazy='dynamic'))

    @property
    def full_name(self):
        """Get full name of the contact"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ''

    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'contact_type': self.contact_type.value if self.contact_type else None,
            'is_primary': self.is_primary,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<CompanyContact {self.full_name} ({self.contact_type.value if self.contact_type else "N/A"})>'
