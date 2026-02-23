"""
Notification Model - In-app notification for users
"""
from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """In-app notification model"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, error
    link = db.Column(db.String(500))  # Optional link to relevant page
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    TYPE_INFO = 'info'
    TYPE_SUCCESS = 'success'
    TYPE_WARNING = 'warning'
    TYPE_ERROR = 'error'

    @classmethod
    def create(cls, user_id, title, message, notification_type='info', link=None):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Notification {self.id} for user {self.user_id}>'
