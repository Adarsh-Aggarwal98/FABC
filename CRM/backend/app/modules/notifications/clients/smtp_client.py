"""
SMTP Email Client for sending emails via Gmail/Outlook/Custom SMTP
Supports both company-level and system-level SMTP configurations
"""
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import current_app

# Global CC email - set via GLOBAL_CC_EMAIL env var if needed (empty = disabled)
GLOBAL_CC_EMAIL = os.getenv('GLOBAL_CC_EMAIL', '')


class SMTPClient:
    """SMTP client for sending emails via Gmail, Outlook, or custom SMTP servers"""

    def __init__(self, config=None):
        """
        Initialize SMTP client with configuration.

        Args:
            config: Either a CompanyEmailConfig or SystemEmailConfig object,
                   or a dict with SMTP settings
        """
        self.config = config
        self._extract_settings()

    def _extract_settings(self):
        """Extract SMTP settings from config object or dict"""
        if self.config is None:
            self.smtp_host = None
            self.smtp_port = 587
            self.smtp_username = None
            self.smtp_password = None
            self.smtp_use_tls = True
            self.smtp_use_ssl = False
            self.sender_email = None
            self.sender_name = None
            self.reply_to_email = None
            return

        if hasattr(self.config, 'smtp_host'):
            # It's a model object
            self.smtp_host = self.config.smtp_host
            self.smtp_port = self.config.smtp_port or 587
            self.smtp_username = self.config.smtp_username
            self.smtp_password = self.config.smtp_password
            self.smtp_use_tls = self.config.smtp_use_tls
            self.smtp_use_ssl = self.config.smtp_use_ssl
            self.sender_email = self.config.sender_email
            self.sender_name = getattr(self.config, 'sender_name', None)
            self.reply_to_email = getattr(self.config, 'reply_to_email', None)
        else:
            # It's a dict
            self.smtp_host = self.config.get('smtp_host')
            self.smtp_port = self.config.get('smtp_port', 587)
            self.smtp_username = self.config.get('smtp_username')
            self.smtp_password = self.config.get('smtp_password')
            self.smtp_use_tls = self.config.get('smtp_use_tls', True)
            self.smtp_use_ssl = self.config.get('smtp_use_ssl', False)
            self.sender_email = self.config.get('sender_email')
            self.sender_name = self.config.get('sender_name')
            self.reply_to_email = self.config.get('reply_to_email')

    def is_configured(self):
        """Check if SMTP is properly configured"""
        return all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_username,
            self.smtp_password,
            self.sender_email
        ])

    def _get_connection(self):
        """Create and return SMTP connection"""
        if self.smtp_use_ssl:
            # Use SSL from the start (port 465 typically)
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context)
        else:
            # Use STARTTLS (port 587 typically)
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)

        server.login(self.smtp_username, self.smtp_password)
        return server

    def _create_message(self, to_email, subject, body, is_html=True, cc_email=None):
        """Create email message"""
        msg = MIMEMultipart('alternative')

        # Set headers
        sender = f'{self.sender_name} <{self.sender_email}>' if self.sender_name else self.sender_email
        msg['From'] = sender
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add CC (use global CC if not specified)
        cc = cc_email or GLOBAL_CC_EMAIL
        if cc:
            msg['Cc'] = cc

        if self.reply_to_email:
            msg['Reply-To'] = self.reply_to_email

        # Attach body
        if is_html:
            # Add plain text version first (fallback)
            plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
            import re
            plain_text = re.sub(r'<[^>]+>', '', plain_text)
            msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        return msg

    def send_email(self, to_email, subject, body, is_html=True):
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            is_html: Whether body is HTML (default True)

        Returns:
            dict with success status and error if failed
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMTP not configured properly'
            }

        try:
            msg = self._create_message(to_email, subject, body, is_html)

            # Include CC in recipients
            recipients = [to_email]
            if GLOBAL_CC_EMAIL:
                recipients.append(GLOBAL_CC_EMAIL)

            server = self._get_connection()
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()

            current_app.logger.info(f'[SMTP] Email sent to {to_email} (CC: {GLOBAL_CC_EMAIL})')
            return {'success': True}

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f'SMTP authentication failed: {str(e)}'
            current_app.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        except smtplib.SMTPException as e:
            error_msg = f'SMTP error: {str(e)}'
            current_app.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to send email: {str(e)}'
            current_app.logger.error(f'[SMTP] {error_msg}')
            current_app.logger.error(f'[SMTP] Host: {self.smtp_host}, Port: {self.smtp_port}, Username: {self.smtp_username}')
            return {'success': False, 'error': error_msg}

    def send_email_to_multiple(self, to_emails, subject, body, is_html=True):
        """
        Send email to multiple recipients.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Email body (HTML or plain text)
            is_html: Whether body is HTML (default True)

        Returns:
            dict with success status, sent count, and errors
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMTP not configured properly'
            }

        results = {
            'success': True,
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        try:
            server = self._get_connection()

            for email in to_emails:
                try:
                    msg = self._create_message(email, subject, body, is_html)
                    # Include CC in recipients
                    recipients = [email]
                    if GLOBAL_CC_EMAIL:
                        recipients.append(GLOBAL_CC_EMAIL)
                    server.sendmail(self.sender_email, recipients, msg.as_string())
                    results['sent'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f'{email}: {str(e)}')

            server.quit()

            if results['failed'] > 0:
                results['success'] = results['sent'] > 0

            return results

        except Exception as e:
            error_msg = f'Failed to send bulk emails: {str(e)}'
            current_app.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'sent': results.get('sent', 0),
                'failed': len(to_emails) - results.get('sent', 0)
            }

    def send_email_with_attachment(self, to_email, subject, body,
                                   attachment_bytes, attachment_name,
                                   attachment_content_type='application/octet-stream',
                                   is_html=True):
        """
        Send an email with an attachment.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            attachment_bytes: Attachment content as bytes
            attachment_name: Filename for the attachment
            attachment_content_type: MIME type of attachment
            is_html: Whether body is HTML (default True)

        Returns:
            dict with success status and error if failed
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMTP not configured properly'
            }

        try:
            msg = MIMEMultipart('mixed')

            # Set headers
            sender = f'{self.sender_name} <{self.sender_email}>' if self.sender_name else self.sender_email
            msg['From'] = sender
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add CC
            if GLOBAL_CC_EMAIL:
                msg['Cc'] = GLOBAL_CC_EMAIL

            if self.reply_to_email:
                msg['Reply-To'] = self.reply_to_email

            # Create body part
            body_part = MIMEMultipart('alternative')
            if is_html:
                import re
                plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
                plain_text = re.sub(r'<[^>]+>', '', plain_text)
                body_part.attach(MIMEText(plain_text, 'plain'))
                body_part.attach(MIMEText(body, 'html'))
            else:
                body_part.attach(MIMEText(body, 'plain'))

            msg.attach(body_part)

            # Add attachment
            maintype, subtype = attachment_content_type.split('/', 1) if '/' in attachment_content_type else ('application', 'octet-stream')
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(attachment_bytes)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
            msg.attach(attachment)

            # Send - include CC in recipients
            recipients = [to_email]
            if GLOBAL_CC_EMAIL:
                recipients.append(GLOBAL_CC_EMAIL)

            server = self._get_connection()
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()

            current_app.logger.info(f'[SMTP] Email with attachment sent to {to_email} (CC: {GLOBAL_CC_EMAIL})')
            return {'success': True}

        except Exception as e:
            error_msg = f'Failed to send email with attachment: {str(e)}'
            current_app.logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def test_connection(self):
        """
        Test SMTP connection without sending an email.

        Returns:
            dict with success status and error if failed
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SMTP not configured properly'
            }

        try:
            server = self._get_connection()
            server.quit()
            return {'success': True, 'message': 'SMTP connection successful'}
        except smtplib.SMTPAuthenticationError as e:
            return {'success': False, 'error': f'Authentication failed: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Connection failed: {str(e)}'}


class EmailClientFactory:
    """Factory for getting the appropriate email client for a company or system"""

    @staticmethod
    def get_client_for_company(company_id):
        """
        Get email client for a company.
        Priority: Company SMTP > System SMTP > Microsoft Graph

        Args:
            company_id: Company ID

        Returns:
            tuple: (client, client_type) where client_type is 'smtp', 'graph', or None
        """
        from app.modules.company.models import CompanyEmailConfig, SystemEmailConfig

        # Check company SMTP config first
        company_config = CompanyEmailConfig.query.filter_by(
            company_id=company_id,
            is_enabled=True
        ).first()

        if company_config and company_config.smtp_host:
            client = SMTPClient(company_config)
            if client.is_configured():
                return client, 'smtp'

        # Fallback to system SMTP config
        system_config = SystemEmailConfig.get_config()
        if system_config and system_config.is_enabled and system_config.smtp_host:
            client = SMTPClient(system_config)
            if client.is_configured():
                return client, 'smtp'

        # Fallback to Microsoft Graph
        from app.modules.notifications.clients.graph_client import GraphAPIClient
        graph_client = GraphAPIClient()
        if graph_client.is_configured():
            return graph_client, 'graph'

        return None, None

    @staticmethod
    def get_system_client():
        """
        Get system-level email client.
        Priority: System SMTP > Microsoft Graph

        Returns:
            tuple: (client, client_type)
        """
        from app.modules.company.models import SystemEmailConfig

        # Check system SMTP config
        system_config = SystemEmailConfig.get_config()
        if system_config and system_config.is_enabled and system_config.smtp_host:
            client = SMTPClient(system_config)
            if client.is_configured():
                return client, 'smtp'

        # Fallback to Microsoft Graph
        from app.modules.notifications.clients.graph_client import GraphAPIClient
        graph_client = GraphAPIClient()
        if graph_client.is_configured():
            return graph_client, 'graph'

        return None, None
