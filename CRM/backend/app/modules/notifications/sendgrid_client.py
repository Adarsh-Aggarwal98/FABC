"""
Backward compatibility layer - SendGridClient is now in clients/ folder

This file re-exports SendGridClient from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.clients import SendGridClient
"""
from app.modules.notifications.clients.sendgrid_client import SendGridClient

__all__ = ['SendGridClient']
