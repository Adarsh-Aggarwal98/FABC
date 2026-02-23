"""
Backward compatibility layer - SMTPClient is now in clients/ folder

This file re-exports SMTPClient and EmailClientFactory from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.clients import SMTPClient, EmailClientFactory
"""
from app.modules.notifications.clients.smtp_client import SMTPClient, EmailClientFactory

__all__ = ['SMTPClient', 'EmailClientFactory']
