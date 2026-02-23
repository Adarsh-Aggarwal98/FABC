"""
Company Enums
=============

Enumeration types used across the company module.
"""
import enum


class ContactType(enum.Enum):
    """Contact type classification for company contacts"""
    PRIMARY = "PRIMARY"
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    COMPLIANCE = "COMPLIANCE"
    OTHER = "OTHER"


class EmailProviderType(enum.Enum):
    """Email provider types for SMTP configuration"""
    GMAIL = "GMAIL"
    OUTLOOK = "OUTLOOK"
    ZOHO = "ZOHO"
    CUSTOM = "CUSTOM"


class StorageProviderType(enum.Enum):
    """Storage provider types for document storage"""
    AZURE_BLOB = "AZURE_BLOB"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    SHAREPOINT = "SHAREPOINT"
    ZOHO_DRIVE = "ZOHO_DRIVE"
