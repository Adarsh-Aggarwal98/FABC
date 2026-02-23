"""
Currency Model
==============

Currency model for managing supported currencies.
"""
from datetime import datetime
from app.extensions import db


class Currency(db.Model):
    """Currency model for managing supported currencies"""
    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'is_active': self.is_active,
            'label': f"{self.code} - {self.name}"
        }

    def __repr__(self):
        return f'<Currency {self.code}>'
