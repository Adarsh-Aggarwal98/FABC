"""
Xero Sync Service

Handles synchronization of data between CRM and Xero.
- Contacts: CRM users/companies <-> Xero contacts
- Invoices: CRM invoices <-> Xero invoices
- Payments: Payment status sync

This service is standalone and doesn't depend on existing CRM modules at import time.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class XeroSyncService:
    """
    Service for synchronizing data between CRM and Xero.

    Usage:
        # Initialize with database session and models
        sync_service = XeroSyncService(db, xero_connection)

        # Sync contacts
        result = sync_service.sync_contacts()

        # Sync invoices
        result = sync_service.sync_invoices()

        # Push single invoice to Xero
        xero_invoice = sync_service.push_invoice_to_xero(crm_invoice_id)
    """

    def __init__(self, db, xero_connection, models: Dict):
        """
        Initialize sync service.

        Args:
            db: SQLAlchemy database instance
            xero_connection: XeroConnection model instance
            models: Dict containing model classes:
                {
                    'XeroConnection': XeroConnection,
                    'XeroContactMapping': XeroContactMapping,
                    'XeroInvoiceMapping': XeroInvoiceMapping,
                    'XeroSyncLog': XeroSyncLog,
                    'User': User,
                    'Company': Company,
                    'Invoice': Invoice
                }
        """
        self.db = db
        self.connection = xero_connection
        self.models = models

        # Import API client
        from app.modules.integrations.xero.xero_client import XeroAPIClient, XeroAuthClient

        # Check and refresh token if needed
        if self.connection.is_token_expired():
            self._refresh_token()

        self.api_client = XeroAPIClient(
            access_token=self.connection.access_token,
            tenant_id=self.connection.xero_tenant_id
        )

    def _refresh_token(self) -> bool:
        """Refresh the access token if expired"""
        from app.modules.integrations.xero.xero_client import XeroAuthClient

        auth_client = XeroAuthClient()
        token_data = auth_client.refresh_access_token(self.connection.refresh_token)

        if token_data:
            self.connection.update_tokens(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token', self.connection.refresh_token),
                expires_in=token_data['expires_in']
            )
            self.db.session.commit()
            return True
        else:
            self.connection.is_active = False
            self.connection.last_error = "Failed to refresh access token"
            self.db.session.commit()
            return False

    def _create_sync_log(self, sync_type: str, direction: str, user_id: str = None, is_manual: bool = False):
        """Create a sync log entry"""
        XeroSyncLog = self.models['XeroSyncLog']
        log = XeroSyncLog(
            xero_connection_id=self.connection.id,
            sync_type=sync_type,
            direction=direction,
            status='started',
            triggered_by_id=user_id,
            is_manual=is_manual
        )
        self.db.session.add(log)
        self.db.session.flush()
        return log

    # ============== Contact Sync ==============

    def sync_contacts(self, user_id: str = None, is_manual: bool = False) -> Dict[str, Any]:
        """
        Sync contacts between CRM and Xero.

        Args:
            user_id: ID of user triggering the sync
            is_manual: Whether this is a manual sync

        Returns:
            Sync result with statistics
        """
        sync_log = self._create_sync_log('contacts', 'bidirectional', user_id, is_manual)

        try:
            # Push CRM contacts to Xero
            push_result = self._push_contacts_to_xero()

            # Pull Xero contacts to CRM (optional - for reference)
            # pull_result = self._pull_contacts_from_xero()

            sync_log.records_processed = push_result['processed']
            sync_log.records_created = push_result['created']
            sync_log.records_updated = push_result['updated']
            sync_log.records_failed = push_result['failed']
            sync_log.error_details = push_result.get('errors')
            sync_log.complete('completed')

            self.connection.last_sync_at = datetime.utcnow()
            self.connection.last_error = None
            self.db.session.commit()

            return {
                'success': True,
                'sync_log_id': sync_log.id,
                **push_result
            }

        except Exception as e:
            logger.error(f"Contact sync failed: {str(e)}")
            sync_log.complete('failed')
            sync_log.error_details = {'error': str(e)}
            self.connection.last_error = str(e)
            self.db.session.commit()

            return {
                'success': False,
                'error': str(e),
                'sync_log_id': sync_log.id
            }

    def _push_contacts_to_xero(self) -> Dict[str, Any]:
        """Push CRM users (clients) to Xero as contacts"""
        User = self.models['User']
        XeroContactMapping = self.models['XeroContactMapping']

        result = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        # Get all active client users in the company
        users = User.query.filter(
            User.company_id == self.connection.company_id,
            User.is_active == True
        ).all()

        for user in users:
            result['processed'] += 1

            try:
                # Check if mapping exists
                mapping = XeroContactMapping.query.filter_by(
                    xero_connection_id=self.connection.id,
                    crm_user_id=user.id
                ).first()

                contact_data = self._build_contact_data_from_user(user)

                if mapping:
                    # Update existing contact
                    response = self.api_client.update_contact(mapping.xero_contact_id, contact_data)
                    if response:
                        mapping.last_synced_at = datetime.utcnow()
                        result['updated'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to update contact for user {user.id}")
                else:
                    # Create new contact
                    response = self.api_client.create_contact(contact_data)
                    if response and 'Contacts' in response:
                        xero_contact = response['Contacts'][0]
                        mapping = XeroContactMapping(
                            xero_connection_id=self.connection.id,
                            crm_user_id=user.id,
                            xero_contact_id=xero_contact['ContactID'],
                            xero_contact_name=xero_contact.get('Name'),
                            last_synced_at=datetime.utcnow()
                        )
                        self.db.session.add(mapping)
                        result['created'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to create contact for user {user.id}")

            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error syncing user {user.id}: {str(e)}")

        return result

    def _build_contact_data_from_user(self, user) -> Dict[str, Any]:
        """Build Xero contact data from CRM user"""
        contact = {
            'Name': user.full_name or user.email,
            'EmailAddress': user.email
        }

        if user.first_name:
            contact['FirstName'] = user.first_name
        if user.last_name:
            contact['LastName'] = user.last_name

        # Add phone if available
        if user.phone:
            contact['Phones'] = [{
                'PhoneType': 'DEFAULT',
                'PhoneNumber': user.phone
            }]

        # Add address if available
        if user.address:
            contact['Addresses'] = [{
                'AddressType': 'STREET',
                'AddressLine1': user.address
            }]

        return contact

    def push_single_contact_to_xero(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Push a single user to Xero as a contact.

        Args:
            user_id: CRM user ID

        Returns:
            Xero contact data or None on error
        """
        User = self.models['User']
        XeroContactMapping = self.models['XeroContactMapping']

        user = User.query.get(user_id)
        if not user:
            return None

        contact_data = self._build_contact_data_from_user(user)

        # Check existing mapping
        mapping = XeroContactMapping.query.filter_by(
            xero_connection_id=self.connection.id,
            crm_user_id=user.id
        ).first()

        if mapping:
            response = self.api_client.update_contact(mapping.xero_contact_id, contact_data)
        else:
            response = self.api_client.create_contact(contact_data)
            if response and 'Contacts' in response:
                xero_contact = response['Contacts'][0]
                mapping = XeroContactMapping(
                    xero_connection_id=self.connection.id,
                    crm_user_id=user.id,
                    xero_contact_id=xero_contact['ContactID'],
                    xero_contact_name=xero_contact.get('Name'),
                    last_synced_at=datetime.utcnow()
                )
                self.db.session.add(mapping)
                self.db.session.commit()

        return response

    # ============== Invoice Sync ==============

    def sync_invoices(self, user_id: str = None, is_manual: bool = False) -> Dict[str, Any]:
        """
        Sync invoices between CRM and Xero.

        Args:
            user_id: ID of user triggering the sync
            is_manual: Whether this is a manual sync

        Returns:
            Sync result with statistics
        """
        sync_log = self._create_sync_log('invoices', 'push', user_id, is_manual)

        try:
            result = self._push_invoices_to_xero()

            sync_log.records_processed = result['processed']
            sync_log.records_created = result['created']
            sync_log.records_updated = result['updated']
            sync_log.records_failed = result['failed']
            sync_log.error_details = result.get('errors')
            sync_log.complete('completed')

            self.connection.last_sync_at = datetime.utcnow()
            self.connection.last_error = None
            self.db.session.commit()

            return {
                'success': True,
                'sync_log_id': sync_log.id,
                **result
            }

        except Exception as e:
            logger.error(f"Invoice sync failed: {str(e)}")
            sync_log.complete('failed')
            sync_log.error_details = {'error': str(e)}
            self.connection.last_error = str(e)
            self.db.session.commit()

            return {
                'success': False,
                'error': str(e),
                'sync_log_id': sync_log.id
            }

    def _push_invoices_to_xero(self) -> Dict[str, Any]:
        """Push CRM invoices to Xero"""
        Invoice = self.models.get('Invoice')
        XeroInvoiceMapping = self.models['XeroInvoiceMapping']
        XeroContactMapping = self.models['XeroContactMapping']

        result = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        if not Invoice:
            result['errors'].append("Invoice model not available")
            return result

        # Get invoices that need syncing (not yet synced or updated since last sync)
        invoices = Invoice.query.filter(
            Invoice.company_id == self.connection.company_id
        ).all()

        for invoice in invoices:
            result['processed'] += 1

            try:
                # Check if mapping exists
                mapping = XeroInvoiceMapping.query.filter_by(
                    xero_connection_id=self.connection.id,
                    crm_invoice_id=invoice.id
                ).first()

                # Get Xero contact ID for the client
                contact_mapping = XeroContactMapping.query.filter_by(
                    xero_connection_id=self.connection.id,
                    crm_user_id=invoice.client_id
                ).first()

                if not contact_mapping:
                    # Try to create contact first
                    contact_result = self.push_single_contact_to_xero(invoice.client_id)
                    if contact_result:
                        contact_mapping = XeroContactMapping.query.filter_by(
                            xero_connection_id=self.connection.id,
                            crm_user_id=invoice.client_id
                        ).first()

                if not contact_mapping:
                    result['failed'] += 1
                    result['errors'].append(f"No Xero contact for invoice {invoice.id}")
                    continue

                invoice_data = self._build_invoice_data(invoice, contact_mapping.xero_contact_id)

                if mapping:
                    # Update existing invoice (if not paid/voided)
                    if mapping.xero_invoice_status not in ['PAID', 'VOIDED']:
                        response = self.api_client.update_invoice(mapping.xero_invoice_id, invoice_data)
                        if response:
                            mapping.last_synced_at = datetime.utcnow()
                            mapping.sync_status = 'synced'
                            result['updated'] += 1
                        else:
                            mapping.sync_status = 'error'
                            result['failed'] += 1
                else:
                    # Create new invoice
                    response = self.api_client.create_invoice(invoice_data)
                    if response and 'Invoices' in response:
                        xero_invoice = response['Invoices'][0]
                        mapping = XeroInvoiceMapping(
                            xero_connection_id=self.connection.id,
                            crm_invoice_id=invoice.id,
                            xero_invoice_id=xero_invoice['InvoiceID'],
                            xero_invoice_number=xero_invoice.get('InvoiceNumber'),
                            xero_invoice_status=xero_invoice.get('Status'),
                            last_synced_at=datetime.utcnow(),
                            sync_status='synced'
                        )
                        self.db.session.add(mapping)
                        result['created'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to create invoice {invoice.id}")

            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error syncing invoice {invoice.id}: {str(e)}")

        return result

    def _build_invoice_data(self, invoice, xero_contact_id: str) -> Dict[str, Any]:
        """Build Xero invoice data from CRM invoice"""
        # Build line items
        line_items = []
        for item in invoice.line_items:
            line_items.append({
                'Description': item.description,
                'Quantity': float(item.quantity) if item.quantity else 1.0,
                'UnitAmount': float(item.unit_price) if item.unit_price else 0.0,
                'AccountCode': self.connection.default_sales_account_id or '200',  # Default sales account
                'TaxType': 'OUTPUT' if not item.is_tax_exempt else 'NONE'
            })

        invoice_data = {
            'Type': 'ACCREC',  # Accounts Receivable (sales invoice)
            'Contact': {'ContactID': xero_contact_id},
            'LineItems': line_items,
            'Date': invoice.issue_date.strftime('%Y-%m-%d') if invoice.issue_date else datetime.utcnow().strftime('%Y-%m-%d'),
            'DueDate': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
            'Reference': invoice.reference or invoice.invoice_number,
            'InvoiceNumber': invoice.invoice_number,
            'Status': self._map_invoice_status(invoice.status),
            'CurrencyCode': invoice.currency or 'AUD'
        }

        # Add notes if present
        if invoice.notes:
            invoice_data['LineAmountTypes'] = 'Exclusive'

        return invoice_data

    def _map_invoice_status(self, crm_status: str) -> str:
        """Map CRM invoice status to Xero status"""
        status_map = {
            'draft': 'DRAFT',
            'sent': 'AUTHORISED',
            'viewed': 'AUTHORISED',
            'paid': 'AUTHORISED',  # Xero marks as PAID when payments are applied
            'overdue': 'AUTHORISED',
            'cancelled': 'VOIDED'
        }
        return status_map.get(crm_status, 'DRAFT')

    def push_single_invoice_to_xero(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Push a single invoice to Xero.

        Args:
            invoice_id: CRM invoice ID

        Returns:
            Xero invoice data or None on error
        """
        Invoice = self.models.get('Invoice')
        XeroInvoiceMapping = self.models['XeroInvoiceMapping']
        XeroContactMapping = self.models['XeroContactMapping']

        if not Invoice:
            return None

        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return None

        # Get or create contact mapping
        contact_mapping = XeroContactMapping.query.filter_by(
            xero_connection_id=self.connection.id,
            crm_user_id=invoice.client_id
        ).first()

        if not contact_mapping:
            self.push_single_contact_to_xero(invoice.client_id)
            contact_mapping = XeroContactMapping.query.filter_by(
                xero_connection_id=self.connection.id,
                crm_user_id=invoice.client_id
            ).first()

        if not contact_mapping:
            return {'error': 'Could not create Xero contact for client'}

        invoice_data = self._build_invoice_data(invoice, contact_mapping.xero_contact_id)

        # Check existing mapping
        mapping = XeroInvoiceMapping.query.filter_by(
            xero_connection_id=self.connection.id,
            crm_invoice_id=invoice.id
        ).first()

        if mapping:
            response = self.api_client.update_invoice(mapping.xero_invoice_id, invoice_data)
            if response:
                mapping.last_synced_at = datetime.utcnow()
                mapping.sync_status = 'synced'
                self.db.session.commit()
        else:
            response = self.api_client.create_invoice(invoice_data)
            if response and 'Invoices' in response:
                xero_invoice = response['Invoices'][0]
                mapping = XeroInvoiceMapping(
                    xero_connection_id=self.connection.id,
                    crm_invoice_id=invoice.id,
                    xero_invoice_id=xero_invoice['InvoiceID'],
                    xero_invoice_number=xero_invoice.get('InvoiceNumber'),
                    xero_invoice_status=xero_invoice.get('Status'),
                    last_synced_at=datetime.utcnow(),
                    sync_status='synced'
                )
                self.db.session.add(mapping)
                self.db.session.commit()

        return response

    # ============== Payment Sync ==============

    def sync_payment_status(self, invoice_id: str = None) -> Dict[str, Any]:
        """
        Pull payment status from Xero for synced invoices.

        Args:
            invoice_id: Optional specific invoice to check

        Returns:
            Sync result
        """
        XeroInvoiceMapping = self.models['XeroInvoiceMapping']
        Invoice = self.models.get('Invoice')

        result = {
            'processed': 0,
            'updated': 0,
            'errors': []
        }

        query = XeroInvoiceMapping.query.filter_by(
            xero_connection_id=self.connection.id
        )

        if invoice_id:
            query = query.filter_by(crm_invoice_id=invoice_id)

        mappings = query.all()

        for mapping in mappings:
            result['processed'] += 1

            try:
                response = self.api_client.get_invoice(mapping.xero_invoice_id)

                if response and 'Invoices' in response:
                    xero_invoice = response['Invoices'][0]
                    new_status = xero_invoice.get('Status')

                    if new_status != mapping.xero_invoice_status:
                        mapping.xero_invoice_status = new_status
                        mapping.last_synced_at = datetime.utcnow()

                        # Update CRM invoice status if paid
                        if Invoice and new_status == 'PAID':
                            crm_invoice = Invoice.query.get(mapping.crm_invoice_id)
                            if crm_invoice and crm_invoice.status != 'paid':
                                crm_invoice.status = 'paid'
                                result['updated'] += 1

            except Exception as e:
                result['errors'].append(f"Error checking invoice {mapping.crm_invoice_id}: {str(e)}")

        self.db.session.commit()
        return result

    # ============== Utility Methods ==============

    def get_xero_organisation(self) -> Optional[Dict]:
        """Get connected Xero organisation details"""
        return self.api_client.get_organisation()

    def get_xero_accounts(self) -> Optional[Dict]:
        """Get Xero chart of accounts"""
        return self.api_client.get_accounts()

    def get_xero_bank_accounts(self) -> Optional[Dict]:
        """Get Xero bank accounts"""
        return self.api_client.get_bank_accounts()

    def get_xero_tax_rates(self) -> Optional[Dict]:
        """Get Xero tax rates"""
        return self.api_client.get_tax_rates()

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Xero connection.

        Returns:
            Connection status and org info
        """
        try:
            org = self.get_xero_organisation()

            if org and 'Organisations' in org:
                org_data = org['Organisations'][0]
                return {
                    'success': True,
                    'organisation': {
                        'name': org_data.get('Name'),
                        'legal_name': org_data.get('LegalName'),
                        'country': org_data.get('CountryCode'),
                        'base_currency': org_data.get('BaseCurrency'),
                        'organisation_type': org_data.get('OrganisationType')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not retrieve organisation details'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
