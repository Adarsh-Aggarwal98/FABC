import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/accountant_crm'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_QUERY_STRING_NAME = 'token'

    # Microsoft Graph API
    GRAPH_CLIENT_ID = os.getenv('GRAPH_CLIENT_ID', '')
    GRAPH_CLIENT_SECRET = os.getenv('GRAPH_CLIENT_SECRET', '')
    GRAPH_TENANT_ID = os.getenv('GRAPH_TENANT_ID', '')
    GRAPH_SENDER_EMAIL = os.getenv('GRAPH_SENDER_EMAIL', '')

    # SMTP2GO Email Configuration (Primary - reliable delivery)
    SMTP2GO_API_KEY = os.getenv('SMTP2GO_API_KEY', '')
    SMTP2GO_SENDER_EMAIL = os.getenv('SMTP2GO_SENDER_EMAIL', '')
    SMTP2GO_SENDER_NAME = os.getenv('SMTP2GO_SENDER_NAME', 'Accountant CRM')

    # MailerSend Email Configuration (Recommended for Docker/Cloud)
    MAILERSEND_API_KEY = os.getenv('MAILERSEND_API_KEY', '')
    MAILERSEND_SENDER_EMAIL = os.getenv('MAILERSEND_SENDER_EMAIL', '')
    MAILERSEND_SENDER_NAME = os.getenv('MAILERSEND_SENDER_NAME', 'Accountant CRM')

    # System SMTP Email Configuration (Alternative to Graph API)
    SYSTEM_SMTP_ENABLED = os.getenv('SYSTEM_SMTP_ENABLED', 'false').lower() == 'true'
    SYSTEM_SMTP_HOST = os.getenv('SYSTEM_SMTP_HOST', 'smtp.gmail.com')
    SYSTEM_SMTP_PORT = int(os.getenv('SYSTEM_SMTP_PORT', '587'))
    SYSTEM_SMTP_USERNAME = os.getenv('SYSTEM_SMTP_USERNAME', '')
    SYSTEM_SMTP_PASSWORD = os.getenv('SYSTEM_SMTP_PASSWORD', '')
    SYSTEM_SMTP_USE_TLS = os.getenv('SYSTEM_SMTP_USE_TLS', 'true').lower() == 'true'
    SYSTEM_SMTP_USE_SSL = os.getenv('SYSTEM_SMTP_USE_SSL', 'false').lower() == 'true'
    SYSTEM_SMTP_SENDER_EMAIL = os.getenv('SYSTEM_SMTP_SENDER_EMAIL', '')
    SYSTEM_SMTP_SENDER_NAME = os.getenv('SYSTEM_SMTP_SENDER_NAME', 'Accountant CRM')

    # Azure Blob Storage Settings (Legacy - kept for backwards compatibility)
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
    AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER', 'crm-documents')
    AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', '')
    AZURE_STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')

    # SharePoint Storage Settings (Primary document storage)
    # Set SHAREPOINT_ENABLED=true to use SharePoint instead of Azure Blob Storage
    SHAREPOINT_ENABLED = os.getenv('SHAREPOINT_ENABLED', 'false').lower() == 'true'
    SHAREPOINT_SITE_ID = os.getenv('SHAREPOINT_SITE_ID', '')  # SharePoint site ID
    SHAREPOINT_DRIVE_ID = os.getenv('SHAREPOINT_DRIVE_ID', '')  # Document library drive ID
    SHAREPOINT_ROOT_FOLDER = os.getenv('SHAREPOINT_ROOT_FOLDER', 'CRM_Documents')  # Root folder in document library

    # Stripe Payment Gateway
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

    # Xero Integration
    XERO_CLIENT_ID = os.getenv('XERO_CLIENT_ID', '')
    XERO_CLIENT_SECRET = os.getenv('XERO_CLIENT_SECRET', '')
    XERO_REDIRECT_URI = os.getenv('XERO_REDIRECT_URI', 'http://localhost:5001/api/integrations/xero/callback')

    # MYOB Integration
    MYOB_CLIENT_ID = os.getenv('MYOB_CLIENT_ID', '')
    MYOB_CLIENT_SECRET = os.getenv('MYOB_CLIENT_SECRET', '')
    MYOB_REDIRECT_URI = os.getenv('MYOB_REDIRECT_URI', 'http://localhost:5001/api/integrations/myob/callback')

    # QuickBooks Integration
    QUICKBOOKS_CLIENT_ID = os.getenv('QUICKBOOKS_CLIENT_ID', '')
    QUICKBOOKS_CLIENT_SECRET = os.getenv('QUICKBOOKS_CLIENT_SECRET', '')
    QUICKBOOKS_REDIRECT_URI = os.getenv('QUICKBOOKS_REDIRECT_URI', 'http://localhost:5001/api/integrations/quickbooks/callback')
    QUICKBOOKS_ENVIRONMENT = os.getenv('QUICKBOOKS_ENVIRONMENT', 'sandbox')  # sandbox or production

    # Google Drive Integration (OAuth - requires tokens)
    GOOGLE_DRIVE_CLIENT_ID = os.getenv('GOOGLE_DRIVE_CLIENT_ID', '')
    GOOGLE_DRIVE_CLIENT_SECRET = os.getenv('GOOGLE_DRIVE_CLIENT_SECRET', '')
    GOOGLE_DRIVE_REDIRECT_URI = os.getenv('GOOGLE_DRIVE_REDIRECT_URI', 'http://localhost:5001/api/integrations/google-drive/callback')
    GOOGLE_DRIVE_ACCESS_TOKEN = os.getenv('GOOGLE_DRIVE_ACCESS_TOKEN', '')
    GOOGLE_DRIVE_REFRESH_TOKEN = os.getenv('GOOGLE_DRIVE_REFRESH_TOKEN', '')
    GOOGLE_DRIVE_ROOT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID', '')

    # Google Apps Script Web App (simpler - no OAuth needed)
    GOOGLE_APPS_SCRIPT_URL = os.getenv('GOOGLE_APPS_SCRIPT_URL', '')
    GOOGLE_APPS_SCRIPT_FOLDER_ID = os.getenv('GOOGLE_APPS_SCRIPT_FOLDER_ID', '')

    # OTP Settings
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6

    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt'}

    # Frontend URL (for email links)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # CORS Allowed Origins (comma-separated list)
    # Development: http://localhost:5173,http://localhost:3000
    # Production: https://pointersconsulting.com.au,https://crm.pointersconsulting.com.au
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://localhost:3001,http://127.0.0.1:5173,http://127.0.0.1:3000,http://127.0.0.1:3001').split(',')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
