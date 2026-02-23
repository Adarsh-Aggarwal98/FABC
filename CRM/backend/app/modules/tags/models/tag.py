"""
Tag model for labeling clients within a company.
"""
from datetime import datetime
from app.extensions import db


# Association table for many-to-many relationship between Users and Tags
user_tags = db.Table(
    'user_tags',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('client_tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class ClientTag(db.Model):
    """Tag model for labeling clients within a company"""
    __tablename__ = 'client_tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#3B82F6')  # Hex color, default blue
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('tags', lazy='dynamic'))
    users = db.relationship('User', secondary=user_tags, backref=db.backref('tags', lazy='dynamic'))

    # Unique constraint: tag name must be unique within a company
    __table_args__ = (
        db.UniqueConstraint('name', 'company_id', name='uq_tag_name_company'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'company_id': self.company_id,
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ClientTag {self.name}>'
