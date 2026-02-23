"""
Import Service Requests Use Case

Handles the business logic for importing service requests from CSV data.
"""
import csv
import io
import logging
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional

from app.modules.imports.models import ImportResult, ImportedServiceRequest
from app.modules.imports.repositories import UserImportRepository, ServiceImportRepository
from app.modules.imports.schemas import VALID_SERVICE_REQUEST_STATUSES, VALID_PRIORITIES

logger = logging.getLogger(__name__)


class ImportServiceRequestsUseCase:
    """Use case for importing service requests from CSV."""

    REQUIRED_COLUMNS = ['client_email', 'service_name']

    def __init__(
        self,
        user_repository: Optional[UserImportRepository] = None,
        service_repository: Optional[ServiceImportRepository] = None
    ):
        """
        Initialize the use case.

        Args:
            user_repository: Optional repository instance (for testing)
            service_repository: Optional repository instance (for testing)
        """
        self.user_repository = user_repository or UserImportRepository()
        self.service_repository = service_repository or ServiceImportRepository()

    def execute(
        self,
        csv_content: str,
        company_id: int
    ) -> Tuple[ImportResult, List[ImportedServiceRequest], Optional[str]]:
        """
        Import service requests from CSV content.

        Args:
            csv_content: The CSV file content as a string
            company_id: The company ID to filter users by

        Returns:
            Tuple of (ImportResult, list of ImportedServiceRequest, error_message)
            If validation fails, error_message contains the reason
        """
        # Parse CSV
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)
        except Exception as e:
            logger.error(f"Failed to parse CSV: {str(e)}")
            return ImportResult(), [], f'Failed to parse CSV: {str(e)}'

        if not rows:
            return ImportResult(), [], 'CSV file is empty'

        # Validate required columns
        if reader.fieldnames:
            missing = [col for col in self.REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                return ImportResult(), [], f'Missing required columns: {", ".join(missing)}'

        # Cache services by name
        services_cache = self.service_repository.get_active_services()

        # Cache users by email
        users_cache = self.user_repository.get_users_by_company(company_id)

        result = ImportResult(total=len(rows))
        imported_requests: List[ImportedServiceRequest] = []
        logger.info(f"Processing {len(rows)} service request records for import")

        for idx, row in enumerate(rows, start=2):
            try:
                self._process_row(
                    row, idx, services_cache, users_cache,
                    result, imported_requests
                )
            except Exception as e:
                result.add_error(idx, str(e))

        self.service_repository.commit()
        logger.info(f"Service request import completed: {result.imported} imported, {result.skipped} skipped")

        return result, imported_requests, None

    def _process_row(
        self,
        row: Dict[str, Any],
        idx: int,
        services_cache: Dict,
        users_cache: Dict,
        result: ImportResult,
        imported_requests: List[ImportedServiceRequest]
    ) -> None:
        """Process a single row from the CSV."""
        client_email = row.get('client_email', '').strip().lower()
        service_name = row.get('service_name', '').strip()

        if not client_email:
            result.add_error(idx, 'Client email is required')
            return

        if not service_name:
            result.add_error(idx, 'Service name is required')
            return

        # Find user
        user = users_cache.get(client_email)
        if not user:
            result.add_error(idx, 'Client not found', email=client_email)
            return

        # Find service
        service = services_cache.get(service_name.lower())
        if not service:
            result.add_error(idx, 'Service not found', service=service_name)
            return

        # Parse status
        status = row.get('status', 'pending').strip().lower()
        if status not in VALID_SERVICE_REQUEST_STATUSES:
            status = 'pending'

        # Parse priority
        priority = row.get('priority', 'normal').strip().lower()
        if priority not in VALID_PRIORITIES:
            priority = 'normal'

        # Parse dates
        deadline_date = None
        if row.get('deadline_date'):
            try:
                deadline_date = datetime.strptime(row['deadline_date'].strip(), '%Y-%m-%d').date()
            except ValueError:
                pass

        created_at = datetime.utcnow()
        if row.get('created_date'):
            try:
                created_at = datetime.strptime(row['created_date'].strip(), '%Y-%m-%d')
            except ValueError:
                pass

        # Parse invoice info
        invoice_amount = None
        if row.get('invoice_amount'):
            try:
                invoice_amount = float(row['invoice_amount'].strip().replace(',', ''))
            except ValueError:
                pass

        invoice_raised = row.get('invoice_raised', '').strip().lower() in ['yes', 'true', '1']
        invoice_paid = row.get('invoice_paid', '').strip().lower() in ['yes', 'true', '1']

        # Create service request
        service_request = self.service_repository.create_service_request(
            user_id=user.id,
            service_id=service.id,
            description=row.get('description', '').strip() or None,
            status=status,
            priority=priority,
            deadline_date=deadline_date,
            invoice_amount=invoice_amount,
            invoice_raised=invoice_raised,
            invoice_paid=invoice_paid,
            internal_reference=row.get('internal_reference', '').strip() or None,
            internal_notes=row.get('internal_notes', '').strip() or None,
            created_at=created_at
        )

        imported_requests.append(ImportedServiceRequest(
            request_number=service_request.request_number,
            client=client_email,
            service=service_name,
            status=status
        ))
        result.add_success()
