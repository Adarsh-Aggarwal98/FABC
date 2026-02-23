"""
RequestStateHistory Model - Tracks state transitions for service requests
"""
from datetime import datetime
from app.extensions import db


class RequestStateHistory(db.Model):
    """
    Tracks state transitions for service requests.
    Used for analytics to understand how long jobs spend in each state.
    """
    __tablename__ = 'request_state_history'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)

    # State information
    from_state = db.Column(db.String(50))  # NULL for initial state
    to_state = db.Column(db.String(50), nullable=False)

    # Who made the change
    changed_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))

    # Timing
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Duration in the previous state (in seconds)
    duration_in_previous_state = db.Column(db.Integer)  # NULL for initial state

    # Optional notes about the transition
    notes = db.Column(db.Text)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('state_history', lazy='dynamic', order_by='RequestStateHistory.changed_at'))
    changed_by = db.relationship('User', backref='state_changes_made')

    @classmethod
    def record_state_change(cls, request_id, from_state, to_state, user_id=None, notes=None):
        """
        Record a state transition for a service request.
        Automatically calculates duration in previous state.
        """
        # Get the last state history entry for this request
        last_entry = cls.query.filter_by(
            service_request_id=request_id
        ).order_by(cls.changed_at.desc()).first()

        duration = None
        if last_entry:
            # Calculate duration in seconds
            duration = int((datetime.utcnow() - last_entry.changed_at).total_seconds())

        # Create new entry
        entry = cls(
            service_request_id=request_id,
            from_state=from_state,
            to_state=to_state,
            changed_by_id=user_id,
            duration_in_previous_state=duration,
            notes=notes
        )
        db.session.add(entry)
        return entry

    @classmethod
    def get_state_durations(cls, request_id):
        """
        Get duration summary for each state a request has been in.
        Returns dict with state names as keys and total seconds as values.
        """
        entries = cls.query.filter_by(service_request_id=request_id).order_by(cls.changed_at).all()

        durations = {}
        for i, entry in enumerate(entries):
            if entry.to_state not in durations:
                durations[entry.to_state] = 0

            # Add duration from this state to the next
            if i < len(entries) - 1:
                next_entry = entries[i + 1]
                duration = (next_entry.changed_at - entry.changed_at).total_seconds()
                durations[entry.to_state] += duration
            else:
                # Current state - calculate time since entering
                duration = (datetime.utcnow() - entry.changed_at).total_seconds()
                durations[entry.to_state] += duration

        return durations

    @classmethod
    def get_average_state_durations(cls, company_id=None, days=30):
        """
        Get average duration for each state across all requests.
        Optionally filter by company and time period.
        """
        from sqlalchemy import func
        from .service_request import ServiceRequest

        query = db.session.query(
            cls.to_state,
            func.count(cls.id).label('count'),
            func.avg(cls.duration_in_previous_state).label('avg_duration'),
            func.min(cls.duration_in_previous_state).label('min_duration'),
            func.max(cls.duration_in_previous_state).label('max_duration')
        ).filter(
            cls.duration_in_previous_state.isnot(None)
        )

        if days:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(cls.changed_at >= cutoff)

        if company_id:
            query = query.join(ServiceRequest).filter(
                ServiceRequest.user.has(company_id=company_id)
            )

        return query.group_by(cls.to_state).all()

    def to_dict(self, include_user=True):
        data = {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'from_state': self.from_state,
            'to_state': self.to_state,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'duration_in_previous_state': self.duration_in_previous_state,
            'duration_formatted': self._format_duration(self.duration_in_previous_state),
            'notes': self.notes
        }

        if include_user and self.changed_by:
            data['changed_by'] = {
                'id': self.changed_by.id,
                'email': self.changed_by.email,
                'full_name': self.changed_by.full_name
            }

        return data

    @staticmethod
    def _format_duration(seconds):
        """Format duration in human-readable format"""
        if seconds is None:
            return None

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"

    def __repr__(self):
        return f'<RequestStateHistory {self.from_state} -> {self.to_state}>'
