"""ATO Alert model — regulatory updates shown on the AusSuperSource website."""
import uuid
from datetime import datetime
from app.extensions import db


class AtoAlert(db.Model):
    __tablename__ = 'ato_alerts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)   # update | alert | reminder
    link = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)       # lower = higher priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'link': self.link,
            'active': self.active,
            'priority': self.priority,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
        }

    def __repr__(self):
        return f'<AtoAlert {self.title[:40]}>'
