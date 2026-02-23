"""Leads Module - Capture website form submissions"""
from .models.lead import Lead
from .routes import leads_bp

__all__ = ['Lead', 'leads_bp']
