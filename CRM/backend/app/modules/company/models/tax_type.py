"""
TaxType Model
=============

Tax type model for managing supported tax types.
"""
from datetime import datetime
from app.extensions import db


class TaxType(db.Model):
    """Tax type model for managing supported tax types"""
    __tablename__ = 'tax_types'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    default_rate = db.Column(db.Numeric(5, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'default_rate': float(self.default_rate) if self.default_rate else 0,
            'is_active': self.is_active,
            'label': f"{self.code} - {self.name}"
        }

    def __repr__(self):
        return f'<TaxType {self.code}>'
