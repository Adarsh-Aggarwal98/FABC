"""
Access Log model
Tracks user login locations and devices for security monitoring.
"""
import uuid
from datetime import datetime
from app.extensions import db


class AccessLog(db.Model):
    """
    Access log for tracking user login locations and devices.
    Captures IP address, geolocation, device info, and session details.
    """
    __tablename__ = 'access_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User who accessed
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Access type
    access_type = db.Column(db.String(50), nullable=False, default='login')  # login, logout, token_refresh, password_reset

    # IP Address information
    ip_address = db.Column(db.String(50), nullable=False)
    ip_type = db.Column(db.String(20))  # ipv4, ipv6

    # Geolocation data (from IP lookup)
    country = db.Column(db.String(100))
    country_code = db.Column(db.String(10))
    region = db.Column(db.String(100))  # State/Province
    region_code = db.Column(db.String(20))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))
    isp = db.Column(db.String(200))  # Internet Service Provider
    organization = db.Column(db.String(200))  # Organization/Company owning the IP
    as_number = db.Column(db.String(50))  # Autonomous System Number

    # Device/Browser information
    user_agent = db.Column(db.String(500))
    browser = db.Column(db.String(100))
    browser_version = db.Column(db.String(50))
    operating_system = db.Column(db.String(100))
    os_version = db.Column(db.String(50))
    device_type = db.Column(db.String(50))  # desktop, mobile, tablet
    device_brand = db.Column(db.String(100))
    device_model = db.Column(db.String(100))

    # Session information
    session_id = db.Column(db.String(100))  # JWT jti or session identifier
    is_successful = db.Column(db.Boolean, default=True)  # Was login successful
    failure_reason = db.Column(db.String(200))  # Reason if login failed

    # Security flags
    is_vpn = db.Column(db.Boolean, default=False)
    is_proxy = db.Column(db.Boolean, default=False)
    is_tor = db.Column(db.Boolean, default=False)
    is_suspicious = db.Column(db.Boolean, default=False)
    threat_level = db.Column(db.String(20))  # low, medium, high

    # Company scope
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('access_logs', lazy='dynamic'))
    company = db.relationship('Company', backref=db.backref('access_logs', lazy='dynamic'))

    # Access type constants
    ACCESS_LOGIN = 'login'
    ACCESS_LOGOUT = 'logout'
    ACCESS_TOKEN_REFRESH = 'token_refresh'
    ACCESS_PASSWORD_RESET = 'password_reset'
    ACCESS_FAILED_LOGIN = 'failed_login'
    ACCESS_2FA_VERIFICATION = '2fa_verification'

    # Device type constants
    DEVICE_DESKTOP = 'desktop'
    DEVICE_MOBILE = 'mobile'
    DEVICE_TABLET = 'tablet'
    DEVICE_UNKNOWN = 'unknown'

    def to_dict(self, include_user=True, include_location=True, include_device=True):
        data = {
            'id': self.id,
            'access_type': self.access_type,
            'ip_address': self.ip_address,
            'is_successful': self.is_successful,
            'failure_reason': self.failure_reason,
            'is_suspicious': self.is_suspicious,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'full_name': self.user.full_name,
                'role': self.user.role.name if self.user.role else None
            }

        if include_location:
            data['location'] = {
                'country': self.country,
                'country_code': self.country_code,
                'region': self.region,
                'city': self.city,
                'postal_code': self.postal_code,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'timezone': self.timezone,
                'isp': self.isp,
                'organization': self.organization
            }

        if include_device:
            data['device'] = {
                'user_agent': self.user_agent,
                'browser': self.browser,
                'browser_version': self.browser_version,
                'operating_system': self.operating_system,
                'os_version': self.os_version,
                'device_type': self.device_type,
                'device_brand': self.device_brand,
                'device_model': self.device_model
            }

        data['security'] = {
            'is_vpn': self.is_vpn,
            'is_proxy': self.is_proxy,
            'is_tor': self.is_tor,
            'threat_level': self.threat_level
        }

        return data

    def to_dict_summary(self):
        """Return a compact summary for list views"""
        return {
            'id': self.id,
            'access_type': self.access_type,
            'ip_address': self.ip_address,
            'location': f"{self.city}, {self.region}, {self.country}" if self.city else self.country or 'Unknown',
            'device': f"{self.browser} on {self.operating_system}" if self.browser else self.device_type or 'Unknown',
            'is_successful': self.is_successful,
            'is_suspicious': self.is_suspicious,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AccessLog {self.access_type} by {self.user_id} from {self.ip_address}>'
