"""
Status models for Kanban board support.

Provides:
- SystemRequestStatus: Default statuses shared across all companies
- CompanyRequestStatus: Custom statuses per company (practice)
"""

from datetime import datetime
from app.extensions import db


class SystemRequestStatus(db.Model):
    """
    System-wide default statuses for service requests.
    These are used when a company has not customized their statuses.
    """
    __tablename__ = 'system_request_statuses'

    id = db.Column(db.Integer, primary_key=True)
    status_key = db.Column(db.String(50), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#6B7280')
    position = db.Column(db.Integer, nullable=False, default=0)
    is_final = db.Column(db.Boolean, default=False)  # True for completed/cancelled states
    is_active = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(10), nullable=False, default='request')  # request, task, or both
    is_default = db.Column(db.Boolean, default=False)  # True for the default status of new items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'status_key': self.status_key,
            'display_name': self.display_name,
            'description': self.description,
            'color': self.color,
            'position': self.position,
            'is_final': self.is_final,
            'is_active': self.is_active,
            'category': self.category,
            'is_default': self.is_default,
            'is_system': True,  # Flag to indicate this is a system status
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SystemRequestStatus {self.status_key}>'


class CompanyRequestStatus(db.Model):
    """
    Custom statuses defined by a company (accounting practice).
    When a company has custom statuses, these override the system defaults.
    """
    __tablename__ = 'company_request_statuses'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    status_key = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#6B7280')
    position = db.Column(db.Integer, nullable=False, default=0)
    wip_limit = db.Column(db.Integer)  # Work-in-progress limit (NULL = no limit)
    is_final = db.Column(db.Boolean, default=False)  # True for completed/cancelled states
    is_active = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(10), nullable=False, default='request')  # request, task, or both
    is_default = db.Column(db.Boolean, default=False)  # True for the default status of new items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('request_statuses', lazy='dynamic'))

    # Unique constraint on company + status_key
    __table_args__ = (
        db.UniqueConstraint('company_id', 'status_key', name='unique_company_status_key'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'status_key': self.status_key,
            'display_name': self.display_name,
            'description': self.description,
            'color': self.color,
            'position': self.position,
            'wip_limit': self.wip_limit,
            'is_final': self.is_final,
            'is_active': self.is_active,
            'category': self.category,
            'is_default': self.is_default,
            'is_system': False,  # Flag to indicate this is a custom status
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<CompanyRequestStatus {self.status_key} for company {self.company_id}>'
