"""
OTP Model - One-time password for 2FA and password reset
"""
from datetime import datetime, timedelta
from app.extensions import db


class OTP(db.Model):
    """OTP model for 2FA and password reset"""
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # 'login_2fa', 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    PURPOSE_LOGIN = 'login_2fa'
    PURPOSE_PASSWORD_RESET = 'password_reset'

    @classmethod
    def create_otp(cls, user_id, purpose, expiry_minutes=10):
        """Create a new OTP for a user"""
        import random

        # Invalidate any existing unused OTPs for this purpose
        cls.query.filter_by(
            user_id=user_id,
            purpose=purpose,
            is_used=False
        ).update({'is_used': True})

        # Generate new OTP
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        otp = cls(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        db.session.add(otp)
        db.session.commit()

        return otp

    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and datetime.utcnow() < self.expires_at

    def mark_used(self):
        """Mark OTP as used"""
        self.is_used = True
        db.session.commit()

    def __repr__(self):
        return f'<OTP {self.code} for user {self.user_id}>'
