"""
Xero Sync Log Model

Logs all sync operations for debugging and auditing.
"""

from datetime import datetime


def create_xero_sync_log_model(db):
    """
    Factory function to create XeroSyncLog model.

    Args:
        db: SQLAlchemy database instance

    Returns:
        XeroSyncLog model class
    """

    class XeroSyncLog(db.Model):
        """
        Logs all sync operations for debugging and auditing.
        """
        __tablename__ = 'xero_sync_logs'

        id = db.Column(db.Integer, primary_key=True)
        xero_connection_id = db.Column(db.String(36), db.ForeignKey('xero_connections.id', ondelete='CASCADE'), nullable=False)

        # Sync details
        sync_type = db.Column(db.String(50), nullable=False)  # contacts, invoices, payments, full
        direction = db.Column(db.String(20), nullable=False)  # push, pull, bidirectional
        status = db.Column(db.String(20), nullable=False)  # started, completed, failed

        # Results
        records_processed = db.Column(db.Integer, default=0)
        records_created = db.Column(db.Integer, default=0)
        records_updated = db.Column(db.Integer, default=0)
        records_failed = db.Column(db.Integer, default=0)
        error_details = db.Column(db.JSON)

        # Timing
        started_at = db.Column(db.DateTime, default=datetime.utcnow)
        completed_at = db.Column(db.DateTime)
        duration_seconds = db.Column(db.Integer)

        # Who triggered it
        triggered_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
        is_manual = db.Column(db.Boolean, default=False)  # Manual vs automatic sync

        def complete(self, status: str = 'completed'):
            self.status = status
            self.completed_at = datetime.utcnow()
            if self.started_at:
                self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())

        def to_dict(self):
            return {
                'id': self.id,
                'xero_connection_id': self.xero_connection_id,
                'sync_type': self.sync_type,
                'direction': self.direction,
                'status': self.status,
                'records_processed': self.records_processed,
                'records_created': self.records_created,
                'records_updated': self.records_updated,
                'records_failed': self.records_failed,
                'error_details': self.error_details,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'duration_seconds': self.duration_seconds,
                'is_manual': self.is_manual
            }

        def __repr__(self):
            return f'<XeroSyncLog {self.sync_type} {self.status}>'

    return XeroSyncLog
