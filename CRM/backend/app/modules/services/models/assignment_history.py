"""
AssignmentHistory Model - Tracks assignment changes for service requests
"""
from datetime import datetime
from app.extensions import db


class AssignmentHistory(db.Model):
    """Tracks assignment changes for service requests"""
    __tablename__ = 'assignment_history'

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id', ondelete='CASCADE'), nullable=False)
    from_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    to_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    assigned_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    assignment_type = db.Column(db.String(50), default='reassignment')  # 'initial', 'reassignment', 'escalation'
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('assignment_history', lazy='dynamic', order_by='AssignmentHistory.created_at.desc()'))
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='assignments_from')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='assignments_to')
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], backref='assignments_made')

    # Type constants
    TYPE_INITIAL = 'initial'
    TYPE_REASSIGNMENT = 'reassignment'
    TYPE_ESCALATION = 'escalation'

    @classmethod
    def record_assignment(cls, request_id, from_user_id, to_user_id, assigned_by_id, assignment_type='reassignment', reason=None):
        """Record an assignment change"""
        entry = cls(
            service_request_id=request_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            assigned_by_id=assigned_by_id,
            assignment_type=assignment_type,
            reason=reason
        )
        db.session.add(entry)
        return entry

    def to_dict(self):
        return {
            'id': self.id,
            'service_request_id': self.service_request_id,
            'assignment_type': self.assignment_type,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'from_user': {
                'id': self.from_user.id,
                'full_name': self.from_user.full_name
            } if self.from_user else None,
            'to_user': {
                'id': self.to_user.id,
                'full_name': self.to_user.full_name
            } if self.to_user else None,
            'assigned_by': {
                'id': self.assigned_by.id,
                'full_name': self.assigned_by.full_name
            } if self.assigned_by else None
        }

    def __repr__(self):
        return f'<AssignmentHistory {self.id} for request {self.service_request_id}>'
