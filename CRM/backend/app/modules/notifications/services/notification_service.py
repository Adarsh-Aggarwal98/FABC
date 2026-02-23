"""
NotificationService - Service for handling in-app notifications
"""
from app.extensions import db
from app.modules.notifications.models.notification import Notification


class NotificationService:
    """Service for in-app notification operations"""

    @classmethod
    def create_notification(cls, user_id, title, message, notification_type='info', link=None):
        """Create a new in-app notification"""
        return Notification.create(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )

    @classmethod
    def get_user_notifications(cls, user_id, unread_only=False, page=1, per_page=20):
        """Get notifications for a user"""
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        query = query.order_by(Notification.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def mark_notification_read(cls, notification_id, user_id):
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()

        if notification:
            notification.mark_read()
            return notification
        return None

    @classmethod
    def mark_all_read(cls, user_id):
        """Mark all notifications as read for a user"""
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()

    @classmethod
    def get_unread_count(cls, user_id):
        """Get count of unread notifications"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
