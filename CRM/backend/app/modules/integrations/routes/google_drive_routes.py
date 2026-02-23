"""
Google Drive Routes

API endpoints for Google Drive document storage integration.
"""

import logging
from flask import Blueprint, request, redirect, jsonify, current_app

logger = logging.getLogger(__name__)

google_drive_bp = Blueprint('google_drive', __name__, url_prefix='/api/integrations/google-drive')


def init_google_drive_routes(jwt_required, get_jwt_identity):
    """
    Initialize Google Drive routes with dependencies.

    Args:
        jwt_required: JWT decorator
        get_jwt_identity: Function to get current user ID

    Returns:
        Configured blueprint
    """
    from ..services import GoogleDriveConfig, GoogleDriveAuthClient, GoogleDriveAPIClient

    @google_drive_bp.route('/auth-url', methods=['GET'])
    @jwt_required()
    def get_auth_url():
        """Get Google OAuth2 authorization URL"""
        logger.info("GET /integrations/google-drive/auth-url - Requesting OAuth URL")

        client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
        redirect_uri = current_app.config.get('GOOGLE_DRIVE_REDIRECT_URI')

        if not client_id:
            logger.warning("Google Drive not configured - missing client ID")
            return jsonify({'error': 'Google Drive not configured'}), 400

        user_id = get_jwt_identity()
        state = f"user_{user_id}"

        auth_url = GoogleDriveAuthClient.get_authorization_url(
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
        """Handle OAuth2 callback from Google"""
        logger.info("GET /integrations/google-drive/callback - Processing OAuth callback")

        code = request.args.get('code')
        error = request.args.get('error')

        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

        if error:
            logger.error(f"Google OAuth error: {error}")
            return redirect(f'{frontend_url}/settings/email-storage?error={error}')

        if not code:
            return jsonify({'error': 'No authorization code provided'}), 400

        try:
            client_id = current_app.config.get('GOOGLE_DRIVE_CLIENT_ID')
            client_secret = current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET')
            redirect_uri = current_app.config.get('GOOGLE_DRIVE_REDIRECT_URI')

            tokens = GoogleDriveAuthClient.exchange_code_for_tokens(
                client_id=client_id,
                client_secret=client_secret,
                code=code,
                redirect_uri=redirect_uri
            )

            access_token = tokens['access_token']
            refresh_token = tokens.get('refresh_token', '')

            logger.info('Google Drive authorized successfully')

            # Print tokens for manual .env update
            print("\n" + "=" * 60)
            print("GOOGLE DRIVE AUTHORIZATION SUCCESSFUL!")
            print("=" * 60)
            print("\nAdd these to your .env file:\n")
            print(f"GOOGLE_DRIVE_ACCESS_TOKEN={access_token}")
            if refresh_token:
                print(f"GOOGLE_DRIVE_REFRESH_TOKEN={refresh_token}")
            print("\n" + "=" * 60 + "\n")

            return redirect(
                f'{frontend_url}/settings/email-storage?google_drive=connected'
                f'&refresh_token={refresh_token}&access_token={access_token}'
            )

        except Exception as e:
            logger.error(f'Google Drive OAuth error: {str(e)}')
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

        config = {
            'google_client_id': client_id,
            'google_client_secret': current_app.config.get('GOOGLE_DRIVE_CLIENT_SECRET'),
            'google_access_token': access_token,
            'google_refresh_token': refresh_token,
            'google_root_folder_id': current_app.config.get('GOOGLE_DRIVE_ROOT_FOLDER_ID'),
        }
        client = GoogleDriveAPIClient(config)
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
        client = GoogleDriveAPIClient(config)
        result = client.test_connection()

        return jsonify(result)

    @google_drive_bp.route('/disconnect', methods=['POST'])
    @jwt_required()
    def disconnect():
        """Disconnect Google Drive"""
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
        client = GoogleDriveAPIClient(config)

        if not client.is_configured():
            return jsonify({'error': 'Google Drive not authorized'}), 400

        try:
            files = client.list_files()
            folders = [f for f in files if f.get('mimeType') == 'application/vnd.google-apps.folder']
            return jsonify({'folders': folders})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return google_drive_bp
