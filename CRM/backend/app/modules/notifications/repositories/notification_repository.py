"""
NotificationRepository - Data access layer for Notification model
"""
from app.extensions import db
from app.modules.notifications.models.notification import Notification


class NotificationRepository:
    """Repository for notification data access operations"""

    @staticmethod
    def create(user_id, title, message, notification_type='info', link=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_by_id(notification_id):
        """Get notification by ID"""
        return Notification.query.get(notification_id)

    @staticmethod
    def get_by_user(user_id, unread_only=False, page=1, per_page=20):
        """Get notifications for a user with pagination"""
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        query = query.order_by(Notification.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read"""
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()

        if notification:
            notification.is_read = True
            db.session.commit()
            return notification
        return None

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()

    @staticmethod
    def delete(notification_id):
        """Delete a notification"""
        notification = Notification.query.get(notification_id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_old_notifications(user_id, days=30):
        """Delete notifications older than specified days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        Notification.query.filter(
            Notification.user_id == user_id,
            Notification.created_at < cutoff_date
        ).delete()
        db.session.commit()
