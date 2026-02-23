"""
Xero Contact Mapping Model

Maps CRM users/companies to Xero contacts.
"""

from datetime import datetime


def create_xero_contact_mapping_model(db):
    """
    Factory function to create XeroContactMapping model.

    Args:
        db: SQLAlchemy database instance

    Returns:
        XeroContactMapping model class
    """

    class XeroContactMapping(db.Model):
        """
        Maps CRM users/companies to Xero contacts.
        Allows bidirectional sync between systems.
        """
        __tablename__ = 'xero_contact_mappings'

        id = db.Column(db.Integer, primary_key=True)
        xero_connection_id = db.Column(db.String(36), db.ForeignKey('xero_connections.id', ondelete='CASCADE'), nullable=False)

        # CRM side - either a user or company
        crm_user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
        crm_company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

        # Xero side
        xero_contact_id = db.Column(db.String(100), nullable=False)
        xero_contact_name = db.Column(db.String(200))

        # Sync tracking
        last_synced_at = db.Column(db.DateTime)
        sync_direction = db.Column(db.String(20), default='bidirectional')  # crm_to_xero, xero_to_crm, bidirectional
        is_active = db.Column(db.Boolean, default=True)

        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        __table_args__ = (
            db.UniqueConstraint('xero_connection_id', 'xero_contact_id', name='unique_xero_contact'),
            db.UniqueConstraint('xero_connection_id', 'crm_user_id', name='unique_crm_user_contact'),
            db.UniqueConstraint('xero_connection_id', 'crm_company_id', name='unique_crm_company_contact'),
        )

        def to_dict(self):
            return {
                'id': self.id,
                'xero_connection_id': self.xero_connection_id,
                'crm_user_id': self.crm_user_id,
                'crm_company_id': self.crm_company_id,
                'xero_contact_id': self.xero_contact_id,
                'xero_contact_name': self.xero_contact_name,
                'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
                'sync_direction': self.sync_direction,
                'is_active': self.is_active
            }

        def __repr__(self):
            return f'<XeroContactMapping {self.xero_contact_name}>'

    return XeroContactMapping
