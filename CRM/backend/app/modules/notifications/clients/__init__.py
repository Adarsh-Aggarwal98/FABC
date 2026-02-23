"""
Email Clients Package
"""
from app.modules.notifications.clients.graph_client import GraphAPIClient
from app.modules.notifications.clients.smtp_client import SMTPClient, EmailClientFactory
from app.modules.notifications.clients.mailersend_client import MailerSendClient
from app.modules.notifications.clients.sendgrid_client import SendGridClient

__all__ = [
    'GraphAPIClient',
    'SMTPClient',
    'EmailClientFactory',
    'MailerSendClient',
    'SendGridClient',
]
