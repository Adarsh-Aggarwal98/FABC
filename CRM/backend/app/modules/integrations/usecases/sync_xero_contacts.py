"""
Sync Xero Contacts Use Case

Handles synchronization of contacts between CRM and Xero.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SyncXeroContactsUseCase:
    """
    Use case for synchronizing contacts between CRM and Xero.
    """

    def __init__(self, repository, api_client, user_model):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            api_client: XeroAPIClient instance
            user_model: User model class
        """
        self.repository = repository
        self.api_client = api_client
        self.User = user_model

    def execute(
        self,
        connection_id: str,
        company_id: str,
        user_id: str = None,
        is_manual: bool = False
    ) -> Dict[str, Any]:
        """
        Sync contacts to Xero.

        Args:
            connection_id: Xero connection ID
            company_id: CRM company ID
            user_id: User triggering the sync
            is_manual: Whether this is a manual sync

        Returns:
            Sync result with statistics
        """
        # Create sync log
        sync_log = self.repository.create_sync_log(
            connection_id=connection_id,
            sync_type='contacts',
            direction='bidirectional',
            user_id=user_id,
            is_manual=is_manual
        )

        result = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        try:
            result = self._push_contacts_to_xero(connection_id, company_id, result)

            # Update sync log
            sync_log.records_processed = result['processed']
            sync_log.records_created = result['created']
            sync_log.records_updated = result['updated']
            sync_log.records_failed = result['failed']
            sync_log.error_details = result['errors'] if result['errors'] else None
            sync_log.complete('completed')

            self.repository.commit()

            return {
                'success': True,
                'sync_log_id': sync_log.id,
                **result
            }

        except Exception as e:
            logger.error(f"Contact sync failed: {str(e)}")
            sync_log.complete('failed')
            sync_log.error_details = {'error': str(e)}
            self.repository.commit()

            return {
                'success': False,
                'error': str(e),
                'sync_log_id': sync_log.id
            }

    def _push_contacts_to_xero(
        self,
        connection_id: str,
        company_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push CRM users to Xero as contacts."""

        # Get all active users in the company
        users = self.User.query.filter(
            self.User.company_id == company_id,
            self.User.is_active == True
        ).all()

        for user in users:
            result['processed'] += 1

            try:
                # Check if mapping exists
                mapping = self.repository.get_contact_mapping_by_user(
                    connection_id, user.id
                )

                contact_data = self._build_contact_data(user)

                if mapping:
                    # Update existing contact
                    response = self.api_client.update_contact(
                        mapping.xero_contact_id,
                        contact_data
                    )
                    if response:
                        self.repository.update_contact_mapping(
                            mapping,
                            last_synced_at=datetime.utcnow()
                        )
                        result['updated'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to update contact for user {user.id}")
                else:
                    # Create new contact
                    response = self.api_client.create_contact(contact_data)
                    if response and 'Contacts' in response:
                        xero_contact = response['Contacts'][0]
                        self.repository.create_contact_mapping(
                            xero_connection_id=connection_id,
                            crm_user_id=user.id,
                            xero_contact_id=xero_contact['ContactID'],
                            xero_contact_name=xero_contact.get('Name'),
                            last_synced_at=datetime.utcnow()
                        )
                        result['created'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to create contact for user {user.id}")

            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error syncing user {user.id}: {str(e)}")

        return result

    def _build_contact_data(self, user) -> Dict[str, Any]:
        """Build Xero contact data from CRM user."""
        contact = {
            'Name': user.full_name or user.email,
            'EmailAddress': user.email
        }

        if user.first_name:
            contact['FirstName'] = user.first_name
        if user.last_name:
            contact['LastName'] = user.last_name

        if hasattr(user, 'phone') and user.phone:
            contact['Phones'] = [{
                'PhoneType': 'DEFAULT',
                'PhoneNumber': user.phone
            }]

        if hasattr(user, 'address') and user.address:
            contact['Addresses'] = [{
                'AddressType': 'STREET',
                'AddressLine1': user.address
            }]

        return contact


class PushSingleContactToXeroUseCase:
    """
    Use case for pushing a single contact to Xero.
    """

    def __init__(self, repository, api_client, user_model):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            api_client: XeroAPIClient instance
            user_model: User model class
        """
        self.repository = repository
        self.api_client = api_client
        self.User = user_model

    def execute(self, connection_id: str, user_id: str) -> Dict[str, Any]:
        """
        Push a single user to Xero as a contact.

        Args:
            connection_id: Xero connection ID
            user_id: CRM user ID

        Returns:
            Result dict
        """
        try:
            user = self.User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}

            contact_data = {
                'Name': user.full_name or user.email,
                'EmailAddress': user.email
            }

            if user.first_name:
                contact_data['FirstName'] = user.first_name
            if user.last_name:
                contact_data['LastName'] = user.last_name

            # Check existing mapping
            mapping = self.repository.get_contact_mapping_by_user(connection_id, user.id)

            if mapping:
                response = self.api_client.update_contact(
                    mapping.xero_contact_id,
                    contact_data
                )
                if response:
                    self.repository.update_contact_mapping(
                        mapping,
                        last_synced_at=datetime.utcnow()
                    )
            else:
                response = self.api_client.create_contact(contact_data)
                if response and 'Contacts' in response:
                    xero_contact = response['Contacts'][0]
                    self.repository.create_contact_mapping(
                        xero_connection_id=connection_id,
                        crm_user_id=user.id,
                        xero_contact_id=xero_contact['ContactID'],
                        xero_contact_name=xero_contact.get('Name'),
                        last_synced_at=datetime.utcnow()
                    )

            self.repository.commit()

            return {
                'success': True,
                'data': response
            }

        except Exception as e:
            logger.error(f"Error pushing contact to Xero: {str(e)}")
            self.repository.rollback()
            return {
                'success': False,
                'error': str(e)
            }
