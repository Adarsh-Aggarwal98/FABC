"""
External Integrations Module (Clean Architecture)

Contains integrations with accounting software and other third-party services.

Folder Structure:
    integrations/
    ├── models/                 # Database models (one per file)
    │   ├── __init__.py
    │   ├── xero_connection.py
    │   ├── xero_contact_mapping.py
    │   └── ...
    ├── repositories/           # Data access layer
    │   ├── __init__.py
    │   ├── xero_repository.py
    │   └── ...
    ├── usecases/               # Business logic
    │   ├── __init__.py
    │   ├── connect_xero.py
    │   ├── sync_xero_contacts.py
    │   └── ...
    ├── services/               # External API clients
    │   ├── __init__.py
    │   ├── xero_service.py
    │   └── google_drive_service.py
    ├── schemas/                # Data validation
    │   ├── __init__.py
    │   └── xero_schemas.py
    └── routes/                 # Thin controllers
        ├── __init__.py
        ├── xero_routes.py
        └── google_drive_routes.py

Supported Integrations:
- Xero (Australian accounting software)
- Google Drive (Document storage)

Usage (Backward Compatible):
    # Xero Integration
    from app.modules.integrations.xero import init_xero_routes, XeroConfig
    if XeroConfig.is_configured():
        xero_bp = init_xero_routes(db, jwt_required, get_jwt_identity)
        app.register_blueprint(xero_bp)

    # Or using clean architecture imports:
    from app.modules.integrations.services import XeroConfig, XeroAuthClient
    from app.modules.integrations.models import create_xero_models
    from app.modules.integrations.repositories import XeroRepository
    from app.modules.integrations.usecases import ConnectXeroUseCase

Environment Variables Required:
    Xero:
        - XERO_CLIENT_ID
        - XERO_CLIENT_SECRET
        - XERO_REDIRECT_URI (optional)

    Google Drive:
        - GOOGLE_DRIVE_CLIENT_ID
        - GOOGLE_DRIVE_CLIENT_SECRET
        - GOOGLE_DRIVE_REDIRECT_URI (optional)
        - GOOGLE_DRIVE_ACCESS_TOKEN (after authorization)
        - GOOGLE_DRIVE_REFRESH_TOKEN (after authorization)
"""

# Re-export models for backward compatibility
from .models import (
    create_xero_models,
    create_xero_connection_model,
    create_xero_contact_mapping_model,
    create_xero_invoice_mapping_model,
    create_xero_sync_log_model,
)

# Re-export services (API clients)
from .services import (
    XeroConfig,
    XeroAuthClient,
    XeroAPIClient,
    GoogleDriveConfig,
    GoogleDriveAuthClient,
    GoogleDriveAPIClient,
)

# Re-export repositories
from .repositories import (
    XeroRepository,
)

# Re-export use cases
from .usecases import (
    ConnectXeroUseCase,
    DisconnectXeroUseCase,
    GetXeroStatusUseCase,
    SyncXeroContactsUseCase,
    PushSingleContactToXeroUseCase,
    SyncXeroInvoicesUseCase,
    PushSingleInvoiceToXeroUseCase,
    SyncXeroPaymentStatusUseCase,
)

# Re-export routes
from .routes import (
    xero_bp,
    init_xero_routes,
    google_drive_bp,
    init_google_drive_routes,
)


# Lazy imports for backward compatibility with sub-modules
def get_xero_module():
    """Lazy load Xero module for backward compatibility"""
    from . import xero
    return xero


def get_google_drive_module():
    """Lazy load Google Drive module for backward compatibility"""
    from . import google_drive
    return google_drive


__all__ = [
    # Model factories
    'create_xero_models',
    'create_xero_connection_model',
    'create_xero_contact_mapping_model',
    'create_xero_invoice_mapping_model',
    'create_xero_sync_log_model',

    # Xero services
    'XeroConfig',
    'XeroAuthClient',
    'XeroAPIClient',

    # Google Drive services
    'GoogleDriveConfig',
    'GoogleDriveAuthClient',
    'GoogleDriveAPIClient',

    # Repositories
    'XeroRepository',

    # Use cases
    'ConnectXeroUseCase',
    'DisconnectXeroUseCase',
    'GetXeroStatusUseCase',
    'SyncXeroContactsUseCase',
    'PushSingleContactToXeroUseCase',
    'SyncXeroInvoicesUseCase',
    'PushSingleInvoiceToXeroUseCase',
    'SyncXeroPaymentStatusUseCase',

    # Routes
    'xero_bp',
    'init_xero_routes',
    'google_drive_bp',
    'init_google_drive_routes',

    # Lazy loaders
    'get_xero_module',
    'get_google_drive_module',
]
