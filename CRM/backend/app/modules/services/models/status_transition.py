"""
Status Transition Model
========================
Defines allowed transitions between statuses with role-based access control.
"""

from app.extensions import db


class StatusTransition(db.Model):
    """
    Defines allowed status transitions.
    NULL company_id = system default rule.
    Company-specific rules override system defaults.
    """
    __tablename__ = 'status_transitions'

    id = db.Column(db.Integer, primary_key=True)
    from_status_key = db.Column(db.String(50), nullable=False)
    to_status_key = db.Column(db.String(50), nullable=False)
    allowed_roles = db.Column(db.JSON)  # List of role names, NULL = all roles
    requires_note = db.Column(db.Boolean, default=False)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('from_status_key', 'to_status_key', 'company_id',
                            name='unique_status_transition'),
    )

    # Relationships
    company = db.relationship('Company', backref=db.backref('status_transitions', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'from_status_key': self.from_status_key,
            'to_status_key': self.to_status_key,
            'allowed_roles': self.allowed_roles,
            'requires_note': self.requires_note,
            'company_id': self.company_id,
            'is_system': self.company_id is None,
        }

    def __repr__(self):
        return f'<StatusTransition {self.from_status_key} -> {self.to_status_key}>'
