"""
Geolocation Service for IP address lookup and user agent parsing.
Uses free IP geolocation APIs and user-agent parsing libraries.
"""
import requests
import re
from flask import current_app
from user_agents import parse as parse_user_agent


class GeolocationService:
    """Service for getting location data from IP addresses and parsing user agents"""

    # Free IP Geolocation APIs (no API key required for basic usage)
    IP_API_URL = 'http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query'
    IPAPI_CO_URL = 'https://ipapi.co/{ip}/json/'

    # Fallback API (requires API key for production use)
    IPINFO_URL = 'https://ipinfo.io/{ip}/json'

    @staticmethod
    def get_client_ip(request):
        """
        Extract the real client IP from the request.
        Handles proxies and load balancers.
        """
        # Check for forwarded headers (when behind proxy/load balancer)
        if request.headers.get('X-Forwarded-For'):
            # X-Forwarded-For can contain multiple IPs, the first one is the client
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        elif request.headers.get('CF-Connecting-IP'):
            # Cloudflare
            ip = request.headers.get('CF-Connecting-IP')
        else:
            ip = request.remote_addr

        return ip

    @staticmethod
    def is_private_ip(ip):
        """Check if IP is a private/local address"""
        private_patterns = [
            r'^127\.',  # Loopback
            r'^10\.',  # Class A private
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Class B private
            r'^192\.168\.',  # Class C private
            r'^::1$',  # IPv6 loopback
            r'^fc00:',  # IPv6 private
            r'^fe80:',  # IPv6 link-local
        ]

        for pattern in private_patterns:
            if re.match(pattern, ip):
                return True
        return False

    @staticmethod
    def get_ip_type(ip):
        """Determine if IP is IPv4 or IPv6"""
        if ':' in ip:
            return 'ipv6'
        return 'ipv4'

    @classmethod
    def lookup_ip(cls, ip_address):
        """
        Look up geolocation data for an IP address.
        Uses multiple fallback APIs for reliability.

        Returns:
            dict with geolocation data or empty dict on failure
        """
        # Don't lookup private/local IPs
        if cls.is_private_ip(ip_address):
            return {
                'ip_address': ip_address,
                'ip_type': cls.get_ip_type(ip_address),
                'country': 'Local Network',
                'country_code': 'LO',
                'city': 'Local',
                'is_private': True
            }

        # Try primary API (ip-api.com)
        try:
            result = cls._lookup_ip_api(ip_address)
            if result:
                return result
        except Exception as e:
            current_app.logger.warning(f'ip-api.com lookup failed: {str(e)}')

        # Try fallback API (ipapi.co)
        try:
            result = cls._lookup_ipapi_co(ip_address)
            if result:
                return result
        except Exception as e:
            current_app.logger.warning(f'ipapi.co lookup failed: {str(e)}')

        # Return minimal data if all APIs fail
        return {
            'ip_address': ip_address,
            'ip_type': cls.get_ip_type(ip_address),
            'lookup_failed': True
        }

    @classmethod
    def _lookup_ip_api(cls, ip_address):
        """Lookup using ip-api.com (free, no API key needed)"""
        url = cls.IP_API_URL.format(ip=ip_address)
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data.get('status') == 'success':
                return {
                    'ip_address': ip_address,
                    'ip_type': cls.get_ip_type(ip_address),
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'region_code': data.get('region'),
                    'city': data.get('city'),
                    'postal_code': data.get('zip'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'organization': data.get('org'),
                    'as_number': data.get('as'),
                    'is_proxy': data.get('proxy', False),
                    'is_hosting': data.get('hosting', False)
                }

        return None

    @classmethod
    def _lookup_ipapi_co(cls, ip_address):
        """Lookup using ipapi.co (free tier available)"""
        url = cls.IPAPI_CO_URL.format(ip=ip_address)
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if not data.get('error'):
                return {
                    'ip_address': ip_address,
                    'ip_type': cls.get_ip_type(ip_address),
                    'country': data.get('country_name'),
                    'country_code': data.get('country_code'),
                    'region': data.get('region'),
                    'region_code': data.get('region_code'),
                    'city': data.get('city'),
                    'postal_code': data.get('postal'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('org'),
                    'organization': data.get('org'),
                    'as_number': data.get('asn')
                }

        return None

    @staticmethod
    def parse_user_agent(user_agent_string):
        """
        Parse user agent string to extract browser, OS, and device info.

        Returns:
            dict with parsed user agent data
        """
        if not user_agent_string:
            return {
                'browser': None,
                'browser_version': None,
                'operating_system': None,
                'os_version': None,
                'device_type': 'unknown',
                'device_brand': None,
                'device_model': None
            }

        try:
            ua = parse_user_agent(user_agent_string)

            # Determine device type
            if ua.is_mobile:
                device_type = 'mobile'
            elif ua.is_tablet:
                device_type = 'tablet'
            elif ua.is_pc:
                device_type = 'desktop'
            elif ua.is_bot:
                device_type = 'bot'
            else:
                device_type = 'unknown'

            return {
                'browser': ua.browser.family,
                'browser_version': ua.browser.version_string,
                'operating_system': ua.os.family,
                'os_version': ua.os.version_string,
                'device_type': device_type,
                'device_brand': ua.device.brand,
                'device_model': ua.device.model
            }

        except Exception as e:
            current_app.logger.warning(f'User agent parsing failed: {str(e)}')
            return {
                'browser': None,
                'browser_version': None,
                'operating_system': None,
                'os_version': None,
                'device_type': 'unknown',
                'device_brand': None,
                'device_model': None
            }

    @classmethod
    def get_full_access_info(cls, request):
        """
        Get complete access information from a Flask request.
        Combines IP geolocation and user agent parsing.

        Args:
            request: Flask request object

        Returns:
            dict with all access information
        """
        # Get IP and user agent
        ip_address = cls.get_client_ip(request)
        user_agent_string = request.headers.get('User-Agent', '')

        # Lookup IP geolocation
        geo_data = cls.lookup_ip(ip_address)

        # Parse user agent
        ua_data = cls.parse_user_agent(user_agent_string)

        # Combine all data
        return {
            'ip_address': ip_address,
            'ip_type': geo_data.get('ip_type', cls.get_ip_type(ip_address)),
            'user_agent': user_agent_string,

            # Geolocation
            'country': geo_data.get('country'),
            'country_code': geo_data.get('country_code'),
            'region': geo_data.get('region'),
            'region_code': geo_data.get('region_code'),
            'city': geo_data.get('city'),
            'postal_code': geo_data.get('postal_code'),
            'latitude': geo_data.get('latitude'),
            'longitude': geo_data.get('longitude'),
            'timezone': geo_data.get('timezone'),
            'isp': geo_data.get('isp'),
            'organization': geo_data.get('organization'),
            'as_number': geo_data.get('as_number'),

            # Device info
            'browser': ua_data.get('browser'),
            'browser_version': ua_data.get('browser_version'),
            'operating_system': ua_data.get('operating_system'),
            'os_version': ua_data.get('os_version'),
            'device_type': ua_data.get('device_type'),
            'device_brand': ua_data.get('device_brand'),
            'device_model': ua_data.get('device_model'),

            # Security flags
            'is_proxy': geo_data.get('is_proxy', False),
            'is_vpn': geo_data.get('is_proxy', False),  # ip-api returns proxy for VPNs too
            'is_hosting': geo_data.get('is_hosting', False)
        }

    @classmethod
    def check_suspicious_access(cls, access_info, user=None):
        """
        Check if an access attempt appears suspicious.

        Args:
            access_info: dict from get_full_access_info
            user: Optional User object to check against historical data

        Returns:
            tuple (is_suspicious, threat_level, reasons)
        """
        reasons = []
        threat_level = 'low'

        # Check for proxy/VPN (might be legitimate, so just flag it)
        if access_info.get('is_proxy') or access_info.get('is_vpn'):
            reasons.append('Access via proxy/VPN detected')

        # Check for hosting provider (could indicate bot/automated access)
        if access_info.get('is_hosting'):
            reasons.append('Access from hosting provider IP')
            threat_level = 'medium'

        # Check for Tor exit node (higher risk)
        if access_info.get('is_tor'):
            reasons.append('Access via Tor network')
            threat_level = 'high'

        # Check for bot user agents
        if access_info.get('device_type') == 'bot':
            reasons.append('Bot user agent detected')
            threat_level = 'medium'

        # If user provided, check for unusual location
        if user:
            from app.modules.audit.models import AccessLog

            # Get user's recent successful logins
            recent_logs = AccessLog.query.filter_by(
                user_id=user.id,
                is_successful=True
            ).order_by(AccessLog.created_at.desc()).limit(10).all()

            if recent_logs:
                # Check if this is a new country
                known_countries = set(log.country_code for log in recent_logs if log.country_code)
                current_country = access_info.get('country_code')

                if current_country and known_countries and current_country not in known_countries:
                    reasons.append(f'Login from new country: {access_info.get("country")}')
                    threat_level = 'medium' if threat_level == 'low' else threat_level

        is_suspicious = len(reasons) > 0

        return is_suspicious, threat_level, reasons
