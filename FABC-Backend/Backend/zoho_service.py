"""Zoho WorkDrive Service for document management"""
import os
import requests
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

class ZohoWorkDriveService:
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
        self.base_url = "https://www.zohoapis.com.au/workdrive/api/v1"
        self.auth_url = "https://accounts.zoho.com.au/oauth/v2/token"

    @property
    def client_id(self):
        return os.getenv('ZOHO_CLIENT_ID', '')

    @property
    def client_secret(self):
        return os.getenv('ZOHO_CLIENT_SECRET', '')

    @property
    def refresh_token(self):
        return os.getenv('ZOHO_REFRESH_TOKEN', '')

    @property
    def parent_folder_id(self):
        return os.getenv('ZOHO_PARENT_FOLDER_ID', '')

    def is_configured(self):
        return bool(self.client_id and self.client_secret and self.refresh_token and self.parent_folder_id)

    def get_access_token(self):
        """Get or refresh access token"""
        # Return cached token if still valid
        if self.access_token and self.token_expiry and self.token_expiry > datetime.now():
            return self.access_token

        if not self.is_configured():
            raise Exception("Zoho WorkDrive is not configured")

        try:
            response = requests.post(self.auth_url, data={
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
            })

            if not response.ok:
                logger.error(f"Zoho token refresh failed: {response.text}")
                raise Exception("Failed to refresh Zoho access token")

            data = response.json()
            self.access_token = data['access_token']
            # Set expiry 5 minutes before actual expiry
            self.token_expiry = datetime.now() + timedelta(seconds=data['expires_in'] - 300)

            return self.access_token

        except Exception as e:
            logger.error(f"Zoho auth error: {e}")
            raise

    def create_user_folder(self, user_id, user_email):
        """Create a folder for a user using their email"""
        token = self.get_access_token()

        # Sanitize email for folder name
        sanitized_email = re.sub(r'[^a-zA-Z0-9@._-]', '_', user_email).replace('@', '_at_')
        folder_name = f"Client_{sanitized_email}"

        response = requests.post(
            f"{self.base_url}/files",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            json={
                'data': {
                    'attributes': {
                        'name': folder_name,
                        'parent_id': self.parent_folder_id,
                    },
                    'type': 'files',
                }
            }
        )

        if not response.ok:
            logger.error(f"Zoho folder creation failed: {response.text}")
            raise Exception("Failed to create Zoho folder")

        data = response.json()
        return data['data']['id']

    def upload_file(self, folder_id, file_data, file_name, mime_type):
        """Upload a file to Zoho WorkDrive"""
        token = self.get_access_token()

        files = {
            'content': (file_name, file_data, mime_type)
        }
        data = {
            'parent_id': folder_id,
            'override-name-exist': 'false'
        }

        response = requests.post(
            f"{self.base_url}/upload",
            headers={'Authorization': f'Bearer {token}'},
            files=files,
            data=data
        )

        if not response.ok:
            logger.error(f"Zoho file upload failed: {response.text}")
            raise Exception("Failed to upload file to Zoho")

        result = response.json()
        return {
            'file_id': result['data'][0]['attributes']['resource_id'],
            'download_url': result['data'][0]['attributes'].get('download_url', '')
        }

    def get_download_url(self, file_id):
        """Get download URL for a file"""
        token = self.get_access_token()

        response = requests.get(
            f"{self.base_url}/files/{file_id}",
            headers={'Authorization': f'Bearer {token}'}
        )

        if not response.ok:
            raise Exception("Failed to get file info from Zoho")

        data = response.json()
        return data['data']['attributes']['download_url']

    def delete_file(self, file_id):
        """Delete a file from Zoho WorkDrive"""
        token = self.get_access_token()

        response = requests.delete(
            f"{self.base_url}/files/{file_id}",
            headers={'Authorization': f'Bearer {token}'}
        )

        return response.ok

    def list_folder_contents(self, folder_id):
        """List contents of a folder"""
        token = self.get_access_token()

        response = requests.get(
            f"{self.base_url}/files/{folder_id}/files",
            headers={'Authorization': f'Bearer {token}'}
        )

        if not response.ok:
            raise Exception("Failed to list folder contents")

        data = response.json()
        return data.get('data', [])


# Singleton instance
zoho_service = ZohoWorkDriveService()
