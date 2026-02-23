"""
ClientServicePricing Model - Client-specific pricing for services
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db


class ClientServicePricing(db.Model):
    """
    Client-specific pricing overrides for services.

    Allows admins to set custom prices per service for specific clients.
    Can be linked to either a user (individual client) or a client_entity (organization).
    """
    __tablename__ = 'client_service_pricing'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    # Client reference: either user_id OR client_entity_id (mutually exclusive)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    client_entity_id = db.Column(db.String(36), db.ForeignKey('client_entities.id', ondelete='CASCADE'), nullable=True)

    # Service reference
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='CASCADE'), nullable=False)

    # Pricing options (at least one must be set)
    custom_price = db.Column(db.Numeric(10, 2), nullable=True)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=True)

    # Additional metadata
    notes = db.Column(db.Text, nullable=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Audit fields
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('client_pricing', lazy='dynamic'))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('custom_pricing', lazy='dynamic'))
    client_entity = db.relationship('ClientEntity', backref=db.backref('custom_pricing', lazy='dynamic'))
    service = db.relationship('Service', backref=db.backref('client_pricing', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def is_valid_now(self) -> bool:
        """Check if this pricing is currently valid based on date range."""
        if not self.is_active:
            return False

        today = date.today()

        if self.valid_from and today < self.valid_from:
            return False

        if self.valid_until and today > self.valid_until:
            return False

        return True

    def calculate_price(self, base_price: Decimal) -> Decimal:
        """
        Calculate the effective price for this client.

        Args:
            base_price: The service's base price

        Returns:
            The calculated price (custom_price if set, otherwise base_price with discount)
        """
        if self.custom_price is not None:
            return Decimal(str(self.custom_price))

        if self.discount_percentage is not None and base_price is not None:
            discount = Decimal(str(self.discount_percentage)) / Decimal('100')
            return base_price * (Decimal('1') - discount)

        return base_price

    def to_dict(self, include_service=False, include_client=False):
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'client_entity_id': self.client_entity_id,
            'service_id': self.service_id,
            'custom_price': float(self.custom_price) if self.custom_price else None,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else None,
            'notes': self.notes,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'is_valid_now': self.is_valid_now(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_service and self.service:
            data['service'] = {
                'id': self.service.id,
                'name': self.service.name,
                'base_price': float(self.service.base_price) if self.service.base_price else None,
            }

        if include_client:
            if self.user:
                data['client'] = {
                    'type': 'user',
                    'id': self.user.id,
                    'name': self.user.full_name,
                    'email': self.user.email,
                }
            elif self.client_entity:
                data['client'] = {
                    'type': 'entity',
                    'id': self.client_entity.id,
                    'name': self.client_entity.name,
                    'entity_type': self.client_entity.entity_type,
                }

        return data

    def __repr__(self):
        client_ref = f"user={self.user_id}" if self.user_id else f"entity={self.client_entity_id}"
        return f'<ClientServicePricing {client_ref} service={self.service_id}>'
