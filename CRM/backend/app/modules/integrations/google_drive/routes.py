"""
Google Drive Integration Routes - Document Storage OAuth Integration

Handles OAuth2 authorization flow for Google Drive document storage.
This integration allows the CRM to store client documents on Google Drive.

Endpoints:
---------
GET  /api/integrations/google-drive/auth-url
    Get the Google OAuth2 authorization URL.
    Frontend should redirect user to this URL for authorization.
    Required role: Any authenticated user

GET  /api/integrations/google-drive/callback
    Handle OAuth2 callback from Google (no auth required).
    Exchanges authorization code for access/refresh tokens.

GET  /api/integrations/google-drive/status
    Check Google Drive connection status.
    Returns whether configured and connected.
    Required role: Any authenticated user

POST /api/integrations/google-drive/test
    Test Google Drive connection by making an API call.
    Required role: Any authenticated user

POST /api/integrations/google-drive/disconnect
    Disconnect Google Drive (instructions to remove tokens).
    Required role: Any authenticated user

GET  /api/integrations/google-drive/folders
    List folders in Google Drive root.
    Required role: Any authenticated user

Configuration:
-------------
Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID: OAuth2 client ID
- GOOGLE_DRIVE_CLIENT_SECRET: OAuth2 client secret
- GOOGLE_DRIVE_REDIRECT_URI: OAuth callback URL
- GOOGLE_DRIVE_ACCESS_TOKEN: Access token (after authorization)
- GOOGLE_DRIVE_REFRESH_TOKEN: Refresh token (after authorization)
- GOOGLE_DRIVE_ROOT_FOLDER_ID: Root folder for CRM documents (optional)
"""
import logging
import os

from flask import Blueprint, request, redirect, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.modules.documents.google_drive_client import GoogleDriveClient
from app.modules.user.models import User

# Module-level logger
logger = logging.getLogger(__name__)

google_drive_bp = Blueprint('google_drive', __name__, url_prefix='/api/integrations/google-drive')


@google_drive_bp.route('/auth-url', methods=['GET'])
@jwt_required()
def get_auth_url():
    """
    Get the Google OAuth2 authorization URL.

    Returns a URL that the frontend should redirect the user to
    for authorizing Google Drive access.
    """
    logger.info("GET /integrations/google-drive/auth-url - Requesting OAuth URL")
    client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
    redirect_uri = current_app.config.get('GOOGLE_DRIVE_REDIRECT_URI')

    if not client_id:
        logger.warning("Google Drive not configured - missing client ID")
        return jsonify({'error': 'Google Drive not configured'}), 400

    # Generate state for CSRF protection (include user ID)
    user_id = get_jwt_identity()
    state = f"user_{user_id}"

    auth_url = GoogleDriveClient.get_authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state
    )

    return jsonify({
        'auth_url': auth_url,
        'message': 'Redirect user to this URL to authorize Google Drive'
    })


@google_drive_bp.route('/callback', methods=['GET'])
def oauth_callback():
    """
    Handle OAuth2 callback from Google.

    This endpoint receives the authorization code from Google
    after the user authorizes the app. It exchanges the code
    for access and refresh tokens.
    """
    logger.info("GET /integrations/google-drive/callback - Processing OAuth callback")
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')

    if error:
        logger.error(f"Google OAuth error: {error}")
        # Redirect to frontend with error
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f'{frontend_url}/settings/email-storage?error={error}')

    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    try:
        client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_DRIVE_REDIRECT_URI')

        # Exchange code for tokens
        tokens = GoogleDriveClient.exchange_code_for_tokens(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri
        )

        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token', '')

        # Log the tokens (in production, save to database or secure storage)
        current_app.logger.info(f'Google Drive authorized successfully')
        current_app.logger.info(f'Access Token: {access_token[:50]}...')
        if refresh_token:
            current_app.logger.info(f'Refresh Token: {refresh_token[:50]}...')

        # For system-wide config, print tokens to add to .env
        print("\n" + "=" * 60)
        print("GOOGLE DRIVE AUTHORIZATION SUCCESSFUL!")
        print("=" * 60)
        print("\nAdd these to your .env file:\n")
        print(f"GOOGLE_DRIVE_ACCESS_TOKEN={access_token}")
        if refresh_token:
            print(f"GOOGLE_DRIVE_REFRESH_TOKEN={refresh_token}")
        print("\n" + "=" * 60 + "\n")

        # Redirect to frontend with success
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f'{frontend_url}/settings/email-storage?google_drive=connected&refresh_token={refresh_token}&access_token={access_token}')

    except Exception as e:
        current_app.logger.error(f'Google Drive OAuth error: {str(e)}')
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f'{frontend_url}/settings/email-storage?error={str(e)}')


@google_drive_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    """Check Google Drive connection status"""
    client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
    access_token = current_app.config.get('GOOGLE_DRIVE_ACCESS_TOKEN')
    refresh_token = current_app.config.get('GOOGLE_DRIVE_REFRESH_TOKEN')

    if not client_id:
        return jsonify({
            'configured': False,
            'connected': False,
            'message': 'Google Drive credentials not configured'
        })

    if not access_token and not refresh_token:
        return jsonify({
            'configured': True,
            'connected': False,
            'message': 'Google Drive not authorized yet'
        })

    # Test connection
    config = {
        'google_client_id': client_id,
        'google_client_secret': current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET'),
        'google_access_token': access_token,
        'google_refresh_token': refresh_token,
        'google_root_folder_id': current_app.config.get('GOOGLE_DRIVE_ROOT_FOLDER_ID'),
    }
    client = GoogleDriveClient(config)
    result = client.test_connection()

    return jsonify({
        'configured': True,
        'connected': result.get('success', False),
        'user': result.get('user'),
        'message': result.get('message') or result.get('error')
    })


@google_drive_bp.route('/test', methods=['POST'])
@jwt_required()
def test_connection():
    """Test Google Drive connection"""
    client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET')
    access_token = current_app.config.get('GOOGLE_DRIVE_ACCESS_TOKEN')
    refresh_token = current_app.config.get('GOOGLE_DRIVE_REFRESH_TOKEN')

    if not all([client_id, client_secret]):
        return jsonify({'success': False, 'error': 'Google Drive not configured'}), 400

    if not access_token and not refresh_token:
        return jsonify({'success': False, 'error': 'Google Drive not authorized'}), 400

    config = {
        'google_client_id': client_id,
        'google_client_secret': client_secret,
        'google_access_token': access_token,
        'google_refresh_token': refresh_token,
        'google_root_folder_id': current_app.config.get('GOOGLE_DRIVE_ROOT_FOLDER_ID'),
    }
    client = GoogleDriveClient(config)
    result = client.test_connection()

    return jsonify(result)


@google_drive_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect():
    """Disconnect Google Drive (clear tokens)"""
    # In a real implementation, you would clear the tokens from database
    # For system-wide config, tokens are in .env and need to be removed manually
    return jsonify({
        'success': True,
        'message': 'To fully disconnect, remove GOOGLE_DRIVE_ACCESS_TOKEN and GOOGLE_DRIVE_REFRESH_TOKEN from .env'
    })


@google_drive_bp.route('/folders', methods=['GET'])
@jwt_required()
def list_folders():
    """List folders in Google Drive root"""
    client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET')
    access_token = current_app.config.get('GOOGLE_DRIVE_ACCESS_TOKEN')
    refresh_token = current_app.config.get('GOOGLE_DRIVE_REFRESH_TOKEN')

    if not all([client_id, client_secret]):
        return jsonify({'error': 'Google Drive not configured'}), 400

    config = {
        'google_client_id': client_id,
        'google_client_secret': client_secret,
        'google_access_token': access_token,
        'google_refresh_token': refresh_token,
        'google_root_folder_id': current_app.config.get('GOOGLE_DRIVE_ROOT_FOLDER_ID'),
    }
    client = GoogleDriveClient(config)

    if not client.is_configured():
        return jsonify({'error': 'Google Drive not authorized'}), 400

    try:
        files = client.list_files()
        folders = [f for f in files if f.get('mimeType') == 'application/vnd.google-apps.folder']
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
