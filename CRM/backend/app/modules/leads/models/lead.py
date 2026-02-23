"""Lead Model - Website form submissions"""
from datetime import datetime
from app.extensions import db


class Lead(db.Model):
    """Model for website contact/appointment form submissions"""
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)

    # Contact info
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    message = db.Column(db.Text)

    # Form type
    form_type = db.Column(db.String(20), nullable=False, default='contact')  # 'contact' or 'appointment'

    # Appointment-specific fields
    appointment_date = db.Column(db.String(50))
    appointment_time = db.Column(db.String(50))
    service = db.Column(db.String(200))
    hear_about_us = db.Column(db.String(200))

    # Management
    status = db.Column(db.String(20), nullable=False, default='new')  # new, contacted, converted, closed
    notes = db.Column(db.Text)

    # Tracking
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'form_type': self.form_type,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'service': self.service,
            'hear_about_us': self.hear_about_us,
            'status': self.status,
            'notes': self.notes,
            'ip_address': self.ip_address,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        }

    def to_export_dict(self):
        """Export-friendly format"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'form_type': self.form_type,
            'service': self.service,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'hear_about_us': self.hear_about_us,
            'status': self.status,
            'notes': self.notes,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        }
