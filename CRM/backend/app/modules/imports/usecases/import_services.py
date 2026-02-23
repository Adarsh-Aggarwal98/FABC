"""
Import Services Use Case

Handles the business logic for importing services catalog from CSV data.
"""
import csv
import io
import logging
from typing import Tuple, Dict, Any, Optional

from app.modules.imports.models import ImportResult
from app.modules.imports.repositories import ServiceImportRepository

logger = logging.getLogger(__name__)


class ImportServicesUseCase:
    """Use case for importing services catalog from CSV."""

    REQUIRED_COLUMNS = ['name']

    def __init__(self, service_repository: Optional[ServiceImportRepository] = None):
        """
        Initialize the use case.

        Args:
            service_repository: Optional repository instance (for testing)
        """
        self.service_repository = service_repository or ServiceImportRepository()

    def execute(self, csv_content: str) -> Tuple[ImportResult, Optional[str]]:
        """
        Import services from CSV content.

        Args:
            csv_content: The CSV file content as a string

        Returns:
            Tuple of (ImportResult, error_message)
            If validation fails, error_message contains the reason
        """
        # Parse CSV
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)
        except Exception as e:
            logger.error(f"Failed to parse CSV: {str(e)}")
            return ImportResult(), f'Failed to parse CSV: {str(e)}'

        if not rows:
            return ImportResult(), 'CSV file is empty'

        # Validate required columns
        if reader.fieldnames and 'name' not in reader.fieldnames:
            return ImportResult(), 'Missing required column: name'

        # Cache existing services
        existing_services = self.service_repository.get_all_services()

        result = ImportResult(total=len(rows))
        logger.info(f"Processing {len(rows)} service records for import")

        for idx, row in enumerate(rows, start=2):
            try:
                self._process_row(row, idx, existing_services, result)
            except Exception as e:
                result.add_error(idx, str(e))

        self.service_repository.commit()
        logger.info(
            f"Service import completed: {result.imported} new, "
            f"{result.updated} updated, {result.skipped} skipped"
        )

        return result, None

    def _process_row(
        self,
        row: Dict[str, Any],
        idx: int,
        existing_services: Dict,
        result: ImportResult
    ) -> None:
        """Process a single row from the CSV."""
        name = row.get('name', '').strip()
        if not name:
            result.add_error(idx, 'Service name is required')
            return

        # Parse numeric values
        base_price = None
        if row.get('base_price'):
            try:
                base_price = float(row['base_price'].strip().replace(',', ''))
            except ValueError:
                pass

        cost_percentage = 0
        if row.get('cost_percentage'):
            try:
                cost_percentage = float(row['cost_percentage'].strip())
            except ValueError:
                pass

        is_recurring = row.get('is_recurring', '').strip().lower() in ['yes', 'true', '1']

        renewal_period_months = 12
        if row.get('renewal_period_months'):
            try:
                renewal_period_months = int(row['renewal_period_months'].strip())
            except ValueError:
                pass

        # Check if service exists
        existing = existing_services.get(name.lower())

        if existing:
            # Update existing service
            self.service_repository.update_service(
                service=existing,
                description=row.get('description', '').strip() or None,
                category=row.get('category', '').strip() or None,
                base_price=base_price,
                is_recurring=is_recurring,
                renewal_period_months=renewal_period_months,
                cost_percentage=cost_percentage
            )
            result.add_update()
        else:
            # Create new service
            service = self.service_repository.create_service(
                name=name,
                description=row.get('description', '').strip() or None,
                category=row.get('category', '').strip() or None,
                base_price=base_price,
                is_recurring=is_recurring,
                renewal_period_months=renewal_period_months,
                cost_percentage=cost_percentage
            )
            existing_services[name.lower()] = service
            result.add_success()
