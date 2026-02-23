"""
ClientNote Model - Notes/comments added to client profiles by staff
"""
from datetime import datetime
from app.extensions import db


class ClientNote(db.Model):
    """Notes/comments added to client profiles by staff"""
    __tablename__ = 'client_notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('client_notes', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_notes')

    def to_dict(self, include_creator=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_creator and self.created_by:
            data['created_by'] = {
                'id': self.created_by.id,
                'email': self.created_by.email,
                'full_name': self.created_by.full_name
            }

        return data

    def __repr__(self):
        return f'<ClientNote {self.id} for user {self.user_id}>'
