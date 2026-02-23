"""
Backward compatibility layer - MailerSendClient is now in clients/ folder

This file re-exports MailerSendClient from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.clients import MailerSendClient
"""
from app.modules.notifications.clients.mailersend_client import MailerSendClient

__all__ = ['MailerSendClient']
