"""
OTP Repository - Data access for OTP entity
"""
from typing import Optional
from app.common.repository import BaseRepository
from app.modules.user.models import OTP


class OTPRepository(BaseRepository[OTP]):
    """Repository for OTP data access"""
    model = OTP

    def find_valid_otp(self, user_id: str, code: str, purpose: str) -> Optional[OTP]:
        """Find a valid (unused) OTP for user"""
        return OTP.query.filter_by(
            user_id=user_id,
            code=code,
            purpose=purpose,
            is_used=False
        ).first()

    def invalidate_user_otps(self, user_id: str, purpose: str) -> int:
        """Invalidate all existing OTPs for a user and purpose"""
        return OTP.query.filter_by(
            user_id=user_id,
            purpose=purpose,
            is_used=False
        ).update({'is_used': True})
