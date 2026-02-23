"""
Query Model - Query/message on a service request
"""
from datetime import datetime
from app.extensions import db


class Query(db.Model):
    """Query/message on a service request"""
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id'), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500))
    # Internal messages are only visible to staff (admin, accountant), not clients
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', backref='sent_queries')

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'attachment_url': self.attachment_url,
            'is_internal': self.is_internal,
            'sender': {
                'id': self.sender.id,
                'full_name': self.sender.full_name,
                'role': self.sender.role.name
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Query {self.id}>'
