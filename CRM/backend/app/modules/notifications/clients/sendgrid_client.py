"""
SendGrid Email Client for sending emails via SendGrid API
Uses HTTPS (port 443) - works even when SMTP ports are blocked
"""
import requests
from flask import current_app


class SendGridClient:
    """SendGrid client for sending emails via REST API"""

    API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key=None, sender_email=None, sender_name=None):
        """
        Initialize SendGrid client.

        Args:
            api_key: SendGrid API key (or reads from config)
            sender_email: Sender email address (or reads from config)
            sender_name: Sender name (or reads from config)
        """
        self.api_key = api_key or current_app.config.get('SENDGRID_API_KEY', '')
        self.sender_email = sender_email or current_app.config.get('SENDGRID_SENDER_EMAIL', '')
        self.sender_name = sender_name or current_app.config.get('SENDGRID_SENDER_NAME', 'Accountant CRM')

    def is_configured(self):
        """Check if SendGrid is properly configured"""
        return bool(self.api_key and self.sender_email)

    def send_email(self, to_email, subject, body, is_html=True):
        """
        Send an email via SendGrid API.

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
                'error': 'SendGrid not configured properly'
            }

        try:
            content_type = "text/html" if is_html else "text/plain"

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {
                    "email": self.sender_email,
                    "name": self.sender_name
                },
                "content": [
                    {
                        "type": content_type,
                        "value": body
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )

            # SendGrid returns 202 for successful queued emails
            if response.status_code in [200, 201, 202]:
                current_app.logger.info(f'[SendGrid] Email sent successfully to {to_email}')
                return {'success': True}
            else:
                error_msg = f'SendGrid API error: {response.status_code} - {response.text}'
                current_app.logger.error(f'[SendGrid] {error_msg}')
                return {'success': False, 'error': error_msg}

        except requests.Timeout:
            error_msg = 'SendGrid API timeout'
            current_app.logger.error(f'[SendGrid] {error_msg}')
            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to send email via SendGrid: {str(e)}'
            current_app.logger.error(f'[SendGrid] {error_msg}')
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
                'error': 'SendGrid not configured properly'
            }

        results = {
            'success': True,
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        for email in to_emails:
            result = self.send_email(email, subject, body, is_html)
            if result.get('success'):
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"{email}: {result.get('error')}")

        if results['failed'] > 0:
            results['success'] = results['sent'] > 0

        return results

    def send_email_with_attachment(self, to_email, subject, body,
                                   attachment_bytes, attachment_name,
                                   attachment_content_type='application/octet-stream',
                                   is_html=True):
        """
        Send an email with an attachment via SendGrid API.

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
                'error': 'SendGrid not configured properly'
            }

        try:
            import base64
            content_type = "text/html" if is_html else "text/plain"

            # Encode attachment as base64
            attachment_base64 = base64.b64encode(attachment_bytes).decode('utf-8')

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {
                    "email": self.sender_email,
                    "name": self.sender_name
                },
                "content": [
                    {
                        "type": content_type,
                        "value": body
                    }
                ],
                "attachments": [
                    {
                        "content": attachment_base64,
                        "filename": attachment_name,
                        "type": attachment_content_type,
                        "disposition": "attachment"
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code in [200, 201, 202]:
                current_app.logger.info(f'[SendGrid] Email with attachment sent to {to_email}')
                return {'success': True}
            else:
                error_msg = f'SendGrid API error: {response.status_code} - {response.text}'
                current_app.logger.error(f'[SendGrid] {error_msg}')
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to send email with attachment: {str(e)}'
            current_app.logger.error(f'[SendGrid] {error_msg}')
            return {'success': False, 'error': error_msg}

    def test_connection(self):
        """
        Test SendGrid API connection.

        Returns:
            dict with success status and error if failed
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'SendGrid not configured. Set SENDGRID_API_KEY and SENDGRID_SENDER_EMAIL.'
            }

        try:
            # Test by checking API key validity
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Use the scopes endpoint to verify API key
            response = requests.get(
                "https://api.sendgrid.com/v3/scopes",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': 'SendGrid API connection successful'}
            else:
                return {'success': False, 'error': f'API key validation failed: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': f'Connection test failed: {str(e)}'}
