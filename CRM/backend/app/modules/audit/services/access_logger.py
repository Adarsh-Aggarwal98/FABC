"""
Access Logger Service
Handles logging of user access events with geolocation and device information.
"""
from flask import request, has_request_context, current_app
from app.extensions import db
from app.modules.audit.models import AccessLog
from .geolocation_service import GeolocationService


class AccessLogger:
    """
    Service for logging user access with geolocation and device information.
    Tracks login attempts, logouts, and other access events.
    """

    @staticmethod
    def log_access(
        user_id: str,
        access_type: str,
        is_successful: bool = True,
        failure_reason: str = None,
        session_id: str = None,
        company_id: str = None,
        request_obj=None
    ) -> AccessLog:
        """
        Log an access event with full geolocation and device information.

        Args:
            user_id: ID of the user accessing the system
            access_type: Type of access (login, logout, etc.)
            is_successful: Whether the access was successful
            failure_reason: Reason for failure (if applicable)
            session_id: JWT jti or session identifier
            company_id: Company ID for scoping
            request_obj: Flask request object (uses current request if not provided)

        Returns:
            AccessLog object
        """
        # Use provided request or current request
        req = request_obj or (request if has_request_context() else None)

        if not req:
            current_app.logger.warning('AccessLogger.log_access called without request context')
            return None

        try:
            # Get full access information (IP, geolocation, device)
            access_info = GeolocationService.get_full_access_info(req)

            # Get user for company_id if not provided
            if company_id is None:
                try:
                    from app.modules.user.models import User
                    user = User.query.get(user_id)
                    if user:
                        company_id = user.company_id
                except Exception:
                    pass

            # Check for suspicious access
            is_suspicious = False
            threat_level = 'low'
            if is_successful:
                try:
                    from app.modules.user.models import User
                    user = User.query.get(user_id)
                    is_suspicious, threat_level, reasons = GeolocationService.check_suspicious_access(
                        access_info, user
                    )
                    if is_suspicious:
                        current_app.logger.warning(
                            f'Suspicious access detected for user {user_id}: {reasons}'
                        )
                except Exception as e:
                    current_app.logger.warning(f'Error checking suspicious access: {str(e)}')

            # Create access log entry
            log_entry = AccessLog(
                user_id=user_id,
                access_type=access_type,
                ip_address=access_info.get('ip_address'),
                ip_type=access_info.get('ip_type'),

                # Geolocation
                country=access_info.get('country'),
                country_code=access_info.get('country_code'),
                region=access_info.get('region'),
                region_code=access_info.get('region_code'),
                city=access_info.get('city'),
                postal_code=access_info.get('postal_code'),
                latitude=access_info.get('latitude'),
                longitude=access_info.get('longitude'),
                timezone=access_info.get('timezone'),
                isp=access_info.get('isp'),
                organization=access_info.get('organization'),
                as_number=access_info.get('as_number'),

                # Device info
                user_agent=access_info.get('user_agent', '')[:500],
                browser=access_info.get('browser'),
                browser_version=access_info.get('browser_version'),
                operating_system=access_info.get('operating_system'),
                os_version=access_info.get('os_version'),
                device_type=access_info.get('device_type'),
                device_brand=access_info.get('device_brand'),
                device_model=access_info.get('device_model'),

                # Session info
                session_id=session_id,
                is_successful=is_successful,
                failure_reason=failure_reason,

                # Security
                is_vpn=access_info.get('is_vpn', False),
                is_proxy=access_info.get('is_proxy', False),
                is_tor=access_info.get('is_tor', False),
                is_suspicious=is_suspicious,
                threat_level=threat_level,

                # Company
                company_id=company_id
            )

            db.session.add(log_entry)
            db.session.flush()

            return log_entry

        except Exception as e:
            current_app.logger.error(f'Error logging access: {str(e)}')
            # Don't let logging failures break the application
            return None

    @staticmethod
    def log_login(user_id: str, session_id: str = None, **kwargs) -> AccessLog:
        """Log successful login"""
        return AccessLogger.log_access(
            user_id=user_id,
            access_type=AccessLog.ACCESS_LOGIN,
            is_successful=True,
            session_id=session_id,
            **kwargs
        )

    @staticmethod
    def log_failed_login(user_id: str = None, email: str = None, failure_reason: str = None, **kwargs) -> AccessLog:
        """
        Log failed login attempt.

        Args:
            user_id: User ID if known
            email: Email attempted (for logging when user doesn't exist)
            failure_reason: Reason for failure
        """
        # If user_id not provided but email is, try to find user
        if not user_id and email:
            try:
                from app.modules.user.models import User
                user = User.query.filter_by(email=email).first()
                if user:
                    user_id = user.id
            except Exception:
                pass

        # If still no user_id, we can't log (foreign key constraint)
        if not user_id:
            current_app.logger.warning(f'Failed login attempt for unknown email: {email}')
            return None

        return AccessLogger.log_access(
            user_id=user_id,
            access_type=AccessLog.ACCESS_FAILED_LOGIN,
            is_successful=False,
            failure_reason=failure_reason or 'Invalid credentials',
            **kwargs
        )

    @staticmethod
    def log_logout(user_id: str, **kwargs) -> AccessLog:
        """Log logout"""
        return AccessLogger.log_access(
            user_id=user_id,
            access_type=AccessLog.ACCESS_LOGOUT,
            is_successful=True,
            **kwargs
        )

    @staticmethod
    def log_token_refresh(user_id: str, session_id: str = None, **kwargs) -> AccessLog:
        """Log token refresh"""
        return AccessLogger.log_access(
            user_id=user_id,
            access_type=AccessLog.ACCESS_TOKEN_REFRESH,
            is_successful=True,
            session_id=session_id,
            **kwargs
        )

    @staticmethod
    def log_2fa_verification(user_id: str, is_successful: bool = True, **kwargs) -> AccessLog:
        """Log 2FA verification attempt"""
        return AccessLogger.log_access(
            user_id=user_id,
            access_type=AccessLog.ACCESS_2FA_VERIFICATION,
            is_successful=is_successful,
            failure_reason='Invalid OTP' if not is_successful else None,
            **kwargs
        )

    @staticmethod
    def get_user_access_logs(user_id: str, limit: int = 50, include_failed: bool = True):
        """Get access logs for a specific user"""
        query = AccessLog.query.filter_by(user_id=user_id)

        if not include_failed:
            query = query.filter_by(is_successful=True)

        logs = query.order_by(AccessLog.created_at.desc()).limit(limit).all()
        return [log.to_dict_summary() for log in logs]

    @staticmethod
    def get_recent_access_logs(company_id: str = None, limit: int = 100, access_type: str = None):
        """Get recent access logs, optionally filtered by company"""
        query = AccessLog.query

        if company_id:
            query = query.filter_by(company_id=company_id)

        if access_type:
            query = query.filter_by(access_type=access_type)

        logs = query.order_by(AccessLog.created_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

    @staticmethod
    def get_suspicious_access_logs(company_id: str = None, limit: int = 50):
        """Get suspicious access attempts"""
        query = AccessLog.query.filter_by(is_suspicious=True)

        if company_id:
            query = query.filter_by(company_id=company_id)

        logs = query.order_by(AccessLog.created_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

    @staticmethod
    def get_access_stats(user_id: str = None, company_id: str = None, days: int = 30):
        """Get access statistics"""
        from datetime import datetime, timedelta
        from sqlalchemy import func

        since = datetime.utcnow() - timedelta(days=days)
        query = AccessLog.query.filter(AccessLog.created_at >= since)

        if user_id:
            query = query.filter_by(user_id=user_id)
        if company_id:
            query = query.filter_by(company_id=company_id)

        # Total accesses
        total = query.count()

        # Successful logins
        successful_logins = query.filter_by(
            access_type=AccessLog.ACCESS_LOGIN,
            is_successful=True
        ).count()

        # Failed logins
        failed_logins = query.filter_by(
            access_type=AccessLog.ACCESS_FAILED_LOGIN
        ).count()

        # Suspicious accesses
        suspicious = query.filter_by(is_suspicious=True).count()

        # Unique countries
        countries = db.session.query(
            AccessLog.country_code
        ).filter(
            AccessLog.created_at >= since,
            AccessLog.country_code.isnot(None)
        )
        if user_id:
            countries = countries.filter(AccessLog.user_id == user_id)
        if company_id:
            countries = countries.filter(AccessLog.company_id == company_id)

        unique_countries = countries.distinct().count()

        # Unique devices (by user agent)
        devices = db.session.query(
            AccessLog.device_type
        ).filter(
            AccessLog.created_at >= since
        )
        if user_id:
            devices = devices.filter(AccessLog.user_id == user_id)
        if company_id:
            devices = devices.filter(AccessLog.company_id == company_id)

        device_breakdown = {}
        for row in devices.distinct().all():
            if row[0]:
                count = query.filter_by(device_type=row[0]).count()
                device_breakdown[row[0]] = count

        return {
            'total_accesses': total,
            'successful_logins': successful_logins,
            'failed_logins': failed_logins,
            'suspicious_accesses': suspicious,
            'unique_countries': unique_countries,
            'device_breakdown': device_breakdown,
            'period_days': days
        }
