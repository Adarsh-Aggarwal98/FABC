"""
Microsoft Graph API Client for sending emails
"""
import msal
import requests
import base64
from flask import current_app


class GraphAPIClient:
    """Microsoft Graph API client for sending emails"""

    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

    def __init__(self):
        self.client_id = current_app.config.get('GRAPH_CLIENT_ID')
        self.client_secret = current_app.config.get('GRAPH_CLIENT_SECRET')
        self.tenant_id = current_app.config.get('GRAPH_TENANT_ID')
        self.sender_email = current_app.config.get('GRAPH_SENDER_EMAIL')

        # Debug logging
        current_app.logger.info(f'[GraphAPI] Loaded config - client_id: {bool(self.client_id)}, '
                                f'client_secret: {bool(self.client_secret)}, '
                                f'tenant_id: {bool(self.tenant_id)}, '
                                f'sender_email: {self.sender_email or "NOT SET"}')

    def is_configured(self):
        """Check if Graph API is properly configured"""
        configured = all([
            self.client_id,
            self.client_secret,
            self.tenant_id,
            self.sender_email
        ])
        current_app.logger.info(f'[GraphAPI] is_configured: {configured}')
        return configured

    def get_access_token(self):
        """Get access token using client credentials flow"""
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError('Graph API credentials not configured')

        authority = f'https://login.microsoftonline.com/{self.tenant_id}'

        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

        if 'access_token' in result:
            return result['access_token']
        else:
            raise Exception(f"Failed to get token: {result.get('error_description', 'Unknown error')}")

    def send_email(self, to_email, subject, body, is_html=True):
        """Send email via Microsoft Graph API"""
        try:
            access_token = self.get_access_token()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            email_data = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML' if is_html else 'Text',
                        'content': body
                    },
                    'toRecipients': [
                        {
                            'emailAddress': {
                                'address': to_email
                            }
                        }
                    ]
                },
                'saveToSentItems': 'true'
            }

            endpoint = f'{self.GRAPH_API_ENDPOINT}/users/{self.sender_email}/sendMail'
            response = requests.post(endpoint, headers=headers, json=email_data)

            if response.status_code == 202:
                return True
            else:
                current_app.logger.error(f'Failed to send email: {response.text}')
                return False

        except Exception as e:
            current_app.logger.error(f'Error sending email: {str(e)}')
            return False

    def send_email_to_multiple(self, to_emails, subject, body, is_html=True):
        """Send email to multiple recipients"""
        try:
            access_token = self.get_access_token()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            recipients = [{'emailAddress': {'address': email}} for email in to_emails]

            email_data = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML' if is_html else 'Text',
                        'content': body
                    },
                    'toRecipients': recipients
                },
                'saveToSentItems': 'true'
            }

            endpoint = f'{self.GRAPH_API_ENDPOINT}/users/{self.sender_email}/sendMail'
            response = requests.post(endpoint, headers=headers, json=email_data)

            if response.status_code == 202:
                return True
            else:
                current_app.logger.error(f'Failed to send email: {response.text}')
                return False

        except Exception as e:
            current_app.logger.error(f'Error sending email: {str(e)}')
            return False

    def send_email_with_attachment(self, to_email, subject, body, attachment_bytes, attachment_name, attachment_content_type='application/pdf', is_html=True):
        """Send email with an attachment via Microsoft Graph API"""
        try:
            access_token = self.get_access_token()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Encode attachment as base64
            attachment_base64 = base64.b64encode(attachment_bytes).decode('utf-8')

            email_data = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'HTML' if is_html else 'Text',
                        'content': body
                    },
                    'toRecipients': [
                        {
                            'emailAddress': {
                                'address': to_email
                            }
                        }
                    ],
                    'attachments': [
                        {
                            '@odata.type': '#microsoft.graph.fileAttachment',
                            'name': attachment_name,
                            'contentType': attachment_content_type,
                            'contentBytes': attachment_base64
                        }
                    ]
                },
                'saveToSentItems': 'true'
            }

            endpoint = f'{self.GRAPH_API_ENDPOINT}/users/{self.sender_email}/sendMail'
            response = requests.post(endpoint, headers=headers, json=email_data)

            if response.status_code == 202:
                return True
            else:
                current_app.logger.error(f'Failed to send email with attachment: {response.text}')
                return False

        except Exception as e:
            current_app.logger.error(f'Error sending email with attachment: {str(e)}')
            return False
