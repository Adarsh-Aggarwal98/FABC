"""
SMTP2GO Email Client for sending emails via SMTP2GO HTTP API
"""
import base64
import re

import requests
from flask import current_app


class SMTP2GoClient:
    """SMTP2GO client for sending emails via HTTP API"""

    API_URL = "https://api.smtp2go.com/v3/email/send"

    def __init__(self, api_key=None, sender_email=None, sender_name=None):
        self.api_key = api_key
        self.sender_email = sender_email
        self.sender_name = sender_name or 'Accountant CRM'

    def is_configured(self):
        """Check if SMTP2GO is properly configured"""
        return bool(self.api_key and self.sender_email)

    def send_email(self, to_email, subject, body, is_html=True):
        if not self.is_configured():
            return {'success': False, 'error': 'SMTP2GO not configured properly'}

        try:
            payload = {
                "sender": self.sender_email,
                "to": [to_email],
                "subject": subject,
            }

            if is_html:
                payload["html_body"] = body
                plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
                plain_text = re.sub(r'<[^>]+>', '', plain_text)
                payload["text_body"] = plain_text
            else:
                payload["text_body"] = body

            response = requests.post(
                self.API_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-Smtp2go-Api-Key": self.api_key,
                    "accept": "application/json",
                },
                json=payload,
                timeout=30,
            )

            current_app.logger.info(f'[SMTP2GO] Email sent to {to_email}, status: {response.status_code}')

            try:
                result = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                result = {}

            if response.status_code == 200 and result.get("data", {}).get("succeeded", 0) > 0:
                return {'success': True}
            else:
                error_msg = result.get("data", {}).get("error", response.text)
                current_app.logger.error(f'[SMTP2GO] Failed: {error_msg}')
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to send email via SMTP2GO: {str(e)}'
            current_app.logger.error(f'[SMTP2GO] {error_msg}')
            return {'success': False, 'error': error_msg}

    def send_email_with_attachment(self, to_email, subject, body,
                                   attachment_bytes, attachment_name,
                                   attachment_content_type='application/octet-stream',
                                   is_html=True):
        if not self.is_configured():
            return {'success': False, 'error': 'SMTP2GO not configured properly'}

        try:
            payload = {
                "sender": self.sender_email,
                "to": [to_email],
                "subject": subject,
                "attachments": [
                    {
                        "filename": attachment_name,
                        "fileblob": base64.b64encode(attachment_bytes).decode('utf-8'),
                        "mimetype": attachment_content_type,
                    }
                ],
            }

            if is_html:
                payload["html_body"] = body
                plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
                plain_text = re.sub(r'<[^>]+>', '', plain_text)
                payload["text_body"] = plain_text
            else:
                payload["text_body"] = body

            response = requests.post(
                self.API_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-Smtp2go-Api-Key": self.api_key,
                    "accept": "application/json",
                },
                json=payload,
                timeout=30,
            )

            current_app.logger.info(f'[SMTP2GO] Email with attachment sent to {to_email}')

            try:
                result = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                result = {}

            if response.status_code == 200 and result.get("data", {}).get("succeeded", 0) > 0:
                return {'success': True}
            else:
                error_msg = result.get("data", {}).get("error", response.text)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to send email with attachment via SMTP2GO: {str(e)}'
            current_app.logger.error(f'[SMTP2GO] {error_msg}')
            return {'success': False, 'error': error_msg}

    def test_connection(self):
        if not self.is_configured():
            return {'success': False, 'error': 'SMTP2GO not configured properly'}

        try:
            if self.api_key and len(self.api_key) > 10:
                return {'success': True, 'message': 'SMTP2GO configured'}
            else:
                return {'success': False, 'error': 'Invalid API key format'}
        except Exception as e:
            return {'success': False, 'error': f'Connection test failed: {str(e)}'}
