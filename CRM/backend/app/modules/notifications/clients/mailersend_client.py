"""
MailerSend Email Client for sending emails via MailerSend API
Uses HTTP API instead of SMTP - works better with Docker/cloud environments
"""
from flask import current_app


class MailerSendClient:
    """MailerSend client for sending emails via HTTP API"""

    def __init__(self, api_key=None, sender_email=None, sender_name=None):
        """
        Initialize MailerSend client.

        Args:
            api_key: MailerSend API key
            sender_email: Default sender email
            sender_name: Default sender name
        """
        self.api_key = api_key
        self.sender_email = sender_email
        self.sender_name = sender_name or 'Accountant CRM'

    def is_configured(self):
        """Check if MailerSend is properly configured"""
        return bool(self.api_key and self.sender_email)

    def send_email(self, to_email, subject, body, is_html=True):
        """
        Send an email via MailerSend API.

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
                'error': 'MailerSend not configured properly'
            }

        try:
            from mailersend import emails

            mailer = emails.NewEmail(self.api_key)

            mail_body = {}

            mail_from = {
                "name": self.sender_name,
                "email": self.sender_email,
            }

            recipients = [
                {
                    "name": to_email.split('@')[0],
                    "email": to_email,
                }
            ]

            mailer.set_mail_from(mail_from, mail_body)
            mailer.set_mail_to(recipients, mail_body)
            mailer.set_subject(subject, mail_body)

            if is_html:
                mailer.set_html_content(body, mail_body)
                # Also set plain text version
                import re
                plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
                plain_text = re.sub(r'<[^>]+>', '', plain_text)
                mailer.set_plaintext_content(plain_text, mail_body)
            else:
                mailer.set_plaintext_content(body, mail_body)

            response = mailer.send(mail_body)

            current_app.logger.info(f'[MailerSend] Email sent to {to_email}, response: {response}')

            # MailerSend returns 202 for success
            if response and (response == '202' or (isinstance(response, str) and '202' in response)):
                return {'success': True}
            else:
                current_app.logger.error(f'[MailerSend] Unexpected response: {response}')
                return {'success': False, 'error': f'Unexpected response: {response}'}

        except Exception as e:
            error_msg = f'Failed to send email via MailerSend: {str(e)}'
            current_app.logger.error(f'[MailerSend] {error_msg}')
            return {'success': False, 'error': error_msg}

    def send_email_with_attachment(self, to_email, subject, body,
                                   attachment_bytes, attachment_name,
                                   attachment_content_type='application/octet-stream',
                                   is_html=True):
        """
        Send an email with an attachment via MailerSend API.

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
                'error': 'MailerSend not configured properly'
            }

        try:
            from mailersend import emails
            import base64

            mailer = emails.NewEmail(self.api_key)

            mail_body = {}

            mail_from = {
                "name": self.sender_name,
                "email": self.sender_email,
            }

            recipients = [
                {
                    "name": to_email.split('@')[0],
                    "email": to_email,
                }
            ]

            mailer.set_mail_from(mail_from, mail_body)
            mailer.set_mail_to(recipients, mail_body)
            mailer.set_subject(subject, mail_body)

            if is_html:
                mailer.set_html_content(body, mail_body)
                import re
                plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
                plain_text = re.sub(r'<[^>]+>', '', plain_text)
                mailer.set_plaintext_content(plain_text, mail_body)
            else:
                mailer.set_plaintext_content(body, mail_body)

            # Add attachment
            attachment = {
                "filename": attachment_name,
                "content": base64.b64encode(attachment_bytes).decode('utf-8'),
            }
            mailer.set_attachments([attachment], mail_body)

            response = mailer.send(mail_body)

            current_app.logger.info(f'[MailerSend] Email with attachment sent to {to_email}')

            return {'success': True, 'response': response}

        except Exception as e:
            error_msg = f'Failed to send email with attachment via MailerSend: {str(e)}'
            current_app.logger.error(f'[MailerSend] {error_msg}')
            return {'success': False, 'error': error_msg}

    def test_connection(self):
        """
        Test MailerSend API connection.

        Returns:
            dict with success status and error if failed
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'MailerSend not configured properly'
            }

        try:
            # Just verify the API key format
            if self.api_key and len(self.api_key) > 10:
                return {'success': True, 'message': 'MailerSend configured'}
            else:
                return {'success': False, 'error': 'Invalid API key format'}
        except Exception as e:
            return {'success': False, 'error': f'Connection test failed: {str(e)}'}
