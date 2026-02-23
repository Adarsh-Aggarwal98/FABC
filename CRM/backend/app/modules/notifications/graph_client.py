"""
Backward compatibility layer - GraphAPIClient is now in clients/ folder

This file re-exports GraphAPIClient from the new location for backward compatibility.
New code should import from:
    from app.modules.notifications.clients import GraphAPIClient
"""
from app.modules.notifications.clients.graph_client import GraphAPIClient

__all__ = ['GraphAPIClient']
