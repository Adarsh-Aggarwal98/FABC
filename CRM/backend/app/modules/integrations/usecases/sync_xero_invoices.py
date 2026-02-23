"""
Sync Xero Invoices Use Case

Handles synchronization of invoices between CRM and Xero.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SyncXeroInvoicesUseCase:
    """
    Use case for synchronizing invoices between CRM and Xero.
    """

    def __init__(self, repository, api_client, invoice_model, connection):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            api_client: XeroAPIClient instance
            invoice_model: Invoice model class
            connection: XeroConnection instance
        """
        self.repository = repository
        self.api_client = api_client
        self.Invoice = invoice_model
        self.connection = connection

    def execute(
        self,
        company_id: str,
        user_id: str = None,
        is_manual: bool = False
    ) -> Dict[str, Any]:
        """
        Sync invoices to Xero.

        Args:
            company_id: CRM company ID
            user_id: User triggering the sync
            is_manual: Whether this is a manual sync

        Returns:
            Sync result with statistics
        """
        # Create sync log
        sync_log = self.repository.create_sync_log(
            connection_id=self.connection.id,
            sync_type='invoices',
            direction='push',
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
            result = self._push_invoices_to_xero(company_id, result)

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
            logger.error(f"Invoice sync failed: {str(e)}")
            sync_log.complete('failed')
            sync_log.error_details = {'error': str(e)}
            self.repository.commit()

            return {
                'success': False,
                'error': str(e),
                'sync_log_id': sync_log.id
            }

    def _push_invoices_to_xero(
        self,
        company_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push CRM invoices to Xero."""

        if not self.Invoice:
            result['errors'].append("Invoice model not available")
            return result

        # Get invoices that need syncing
        invoices = self.Invoice.query.filter(
            self.Invoice.company_id == company_id
        ).all()

        for invoice in invoices:
            result['processed'] += 1

            try:
                # Check if mapping exists
                mapping = self.repository.get_invoice_mapping_by_crm_id(
                    self.connection.id,
                    invoice.id
                )

                # Get Xero contact ID for the client
                contact_mapping = self.repository.get_contact_mapping_by_user(
                    self.connection.id,
                    invoice.client_id
                )

                if not contact_mapping:
                    result['failed'] += 1
                    result['errors'].append(f"No Xero contact for invoice {invoice.id}")
                    continue

                invoice_data = self._build_invoice_data(invoice, contact_mapping.xero_contact_id)

                if mapping:
                    # Update existing invoice (if not paid/voided)
                    if mapping.xero_invoice_status not in ['PAID', 'VOIDED']:
                        response = self.api_client.update_invoice(
                            mapping.xero_invoice_id,
                            invoice_data
                        )
                        if response:
                            self.repository.update_invoice_mapping(
                                mapping,
                                last_synced_at=datetime.utcnow(),
                                sync_status='synced'
                            )
                            result['updated'] += 1
                        else:
                            self.repository.update_invoice_mapping(
                                mapping,
                                sync_status='error'
                            )
                            result['failed'] += 1
                else:
                    # Create new invoice
                    response = self.api_client.create_invoice(invoice_data)
                    if response and 'Invoices' in response:
                        xero_invoice = response['Invoices'][0]
                        self.repository.create_invoice_mapping(
                            xero_connection_id=self.connection.id,
                            crm_invoice_id=invoice.id,
                            xero_invoice_id=xero_invoice['InvoiceID'],
                            xero_invoice_number=xero_invoice.get('InvoiceNumber'),
                            xero_invoice_status=xero_invoice.get('Status'),
                            last_synced_at=datetime.utcnow(),
                            sync_status='synced'
                        )
                        result['created'] += 1
                    else:
                        result['failed'] += 1
                        result['errors'].append(f"Failed to create invoice {invoice.id}")

            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error syncing invoice {invoice.id}: {str(e)}")

        return result

    def _build_invoice_data(self, invoice, xero_contact_id: str) -> Dict[str, Any]:
        """Build Xero invoice data from CRM invoice."""
        # Build line items
        line_items = []

        if hasattr(invoice, 'line_items'):
            for item in invoice.line_items:
                line_items.append({
                    'Description': item.description,
                    'Quantity': float(item.quantity) if item.quantity else 1.0,
                    'UnitAmount': float(item.unit_price) if item.unit_price else 0.0,
                    'AccountCode': self.connection.default_sales_account_id or '200',
                    'TaxType': 'OUTPUT' if not getattr(item, 'is_tax_exempt', False) else 'NONE'
                })

        invoice_data = {
            'Type': 'ACCREC',  # Accounts Receivable (sales invoice)
            'Contact': {'ContactID': xero_contact_id},
            'LineItems': line_items,
            'Date': invoice.issue_date.strftime('%Y-%m-%d') if invoice.issue_date else datetime.utcnow().strftime('%Y-%m-%d'),
            'DueDate': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
            'Reference': getattr(invoice, 'reference', None) or invoice.invoice_number,
            'InvoiceNumber': invoice.invoice_number,
            'Status': self._map_invoice_status(invoice.status),
            'CurrencyCode': getattr(invoice, 'currency', 'AUD') or 'AUD'
        }

        return invoice_data

    def _map_invoice_status(self, crm_status: str) -> str:
        """Map CRM invoice status to Xero status."""
        status_map = {
            'draft': 'DRAFT',
            'sent': 'AUTHORISED',
            'viewed': 'AUTHORISED',
            'paid': 'AUTHORISED',
            'overdue': 'AUTHORISED',
            'cancelled': 'VOIDED'
        }
        return status_map.get(crm_status, 'DRAFT')


class PushSingleInvoiceToXeroUseCase:
    """
    Use case for pushing a single invoice to Xero.
    """

    def __init__(self, repository, api_client, invoice_model, connection):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            api_client: XeroAPIClient instance
            invoice_model: Invoice model class
            connection: XeroConnection instance
        """
        self.repository = repository
        self.api_client = api_client
        self.Invoice = invoice_model
        self.connection = connection

    def execute(self, invoice_id: str) -> Dict[str, Any]:
        """
        Push a single invoice to Xero.

        Args:
            invoice_id: CRM invoice ID

        Returns:
            Result dict
        """
        try:
            if not self.Invoice:
                return {'success': False, 'error': 'Invoice model not available'}

            invoice = self.Invoice.query.get(invoice_id)
            if not invoice:
                return {'success': False, 'error': 'Invoice not found'}

            # Get or create contact mapping
            contact_mapping = self.repository.get_contact_mapping_by_user(
                self.connection.id,
                invoice.client_id
            )

            if not contact_mapping:
                return {'success': False, 'error': 'No Xero contact for client'}

            invoice_data = self._build_invoice_data(invoice, contact_mapping.xero_contact_id)

            # Check existing mapping
            mapping = self.repository.get_invoice_mapping_by_crm_id(
                self.connection.id,
                invoice.id
            )

            if mapping:
                response = self.api_client.update_invoice(
                    mapping.xero_invoice_id,
                    invoice_data
                )
                if response:
                    self.repository.update_invoice_mapping(
                        mapping,
                        last_synced_at=datetime.utcnow(),
                        sync_status='synced'
                    )
            else:
                response = self.api_client.create_invoice(invoice_data)
                if response and 'Invoices' in response:
                    xero_invoice = response['Invoices'][0]
                    self.repository.create_invoice_mapping(
                        xero_connection_id=self.connection.id,
                        crm_invoice_id=invoice.id,
                        xero_invoice_id=xero_invoice['InvoiceID'],
                        xero_invoice_number=xero_invoice.get('InvoiceNumber'),
                        xero_invoice_status=xero_invoice.get('Status'),
                        last_synced_at=datetime.utcnow(),
                        sync_status='synced'
                    )

            self.repository.commit()

            return {
                'success': True,
                'data': response
            }

        except Exception as e:
            logger.error(f"Error pushing invoice to Xero: {str(e)}")
            self.repository.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def _build_invoice_data(self, invoice, xero_contact_id: str) -> Dict[str, Any]:
        """Build Xero invoice data from CRM invoice."""
        line_items = []

        if hasattr(invoice, 'line_items'):
            for item in invoice.line_items:
                line_items.append({
                    'Description': item.description,
                    'Quantity': float(item.quantity) if item.quantity else 1.0,
                    'UnitAmount': float(item.unit_price) if item.unit_price else 0.0,
                    'AccountCode': self.connection.default_sales_account_id or '200',
                    'TaxType': 'OUTPUT' if not getattr(item, 'is_tax_exempt', False) else 'NONE'
                })

        return {
            'Type': 'ACCREC',
            'Contact': {'ContactID': xero_contact_id},
            'LineItems': line_items,
            'Date': invoice.issue_date.strftime('%Y-%m-%d') if invoice.issue_date else datetime.utcnow().strftime('%Y-%m-%d'),
            'DueDate': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else None,
            'Reference': getattr(invoice, 'reference', None) or invoice.invoice_number,
            'InvoiceNumber': invoice.invoice_number,
            'Status': 'DRAFT',
            'CurrencyCode': getattr(invoice, 'currency', 'AUD') or 'AUD'
        }


class SyncXeroPaymentStatusUseCase:
    """
    Use case for syncing payment status from Xero.
    """

    def __init__(self, repository, api_client, invoice_model):
        """
        Initialize use case.

        Args:
            repository: XeroRepository instance
            api_client: XeroAPIClient instance
            invoice_model: Invoice model class
        """
        self.repository = repository
        self.api_client = api_client
        self.Invoice = invoice_model

    def execute(self, connection_id: str, invoice_id: str = None) -> Dict[str, Any]:
        """
        Pull payment status from Xero for synced invoices.

        Args:
            connection_id: Xero connection ID
            invoice_id: Optional specific invoice to check

        Returns:
            Sync result
        """
        result = {
            'processed': 0,
            'updated': 0,
            'errors': []
        }

        try:
            mappings = self.repository.get_all_invoice_mappings(connection_id)

            if invoice_id:
                mappings = [m for m in mappings if m.crm_invoice_id == invoice_id]

            for mapping in mappings:
                result['processed'] += 1

                try:
                    response = self.api_client.get_invoice(mapping.xero_invoice_id)

                    if response and 'Invoices' in response:
                        xero_invoice = response['Invoices'][0]
                        new_status = xero_invoice.get('Status')

                        if new_status != mapping.xero_invoice_status:
                            self.repository.update_invoice_mapping(
                                mapping,
                                xero_invoice_status=new_status,
                                last_synced_at=datetime.utcnow()
                            )

                            # Update CRM invoice status if paid
                            if self.Invoice and new_status == 'PAID':
                                crm_invoice = self.Invoice.query.get(mapping.crm_invoice_id)
                                if crm_invoice and crm_invoice.status != 'paid':
                                    crm_invoice.status = 'paid'
                                    result['updated'] += 1

                except Exception as e:
                    result['errors'].append(f"Error checking invoice {mapping.crm_invoice_id}: {str(e)}")

            self.repository.commit()
            return {
                'success': True,
                **result
            }

        except Exception as e:
            logger.error(f"Error syncing payment status: {str(e)}")
            self.repository.rollback()
            return {
                'success': False,
                'error': str(e)
            }
