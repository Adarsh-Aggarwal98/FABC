"""
CompanyServiceSettings Model - Practice-level settings for services
"""
from datetime import datetime
from app.extensions import db


class CompanyServiceSettings(db.Model):
    """Practice-level settings for default services - allows activate/deactivate and overrides"""
    __tablename__ = 'company_service_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)

    # Activation toggle
    is_active = db.Column(db.Boolean, default=True)

    # Overrides (NULL means use default from Service)
    custom_name = db.Column(db.String(200), nullable=True)
    custom_description = db.Column(db.Text, nullable=True)
    custom_price = db.Column(db.Numeric(10, 2), nullable=True)
    cost_percentage = db.Column(db.Numeric(5, 2), nullable=True)  # Override cost % for this company

    # Display options
    display_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('company_id', 'service_id', name='unique_company_service'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'service_id': self.service_id,
            'is_active': self.is_active,
            'custom_name': self.custom_name,
            'custom_description': self.custom_description,
            'custom_price': float(self.custom_price) if self.custom_price else None,
            'cost_percentage': float(self.cost_percentage) if self.cost_percentage else None,
            'display_order': self.display_order,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<CompanyServiceSettings company={self.company_id} service={self.service_id}>'
