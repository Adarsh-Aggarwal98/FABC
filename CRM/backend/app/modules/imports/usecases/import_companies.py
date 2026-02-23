"""
Import Companies Use Case

Handles the business logic for importing companies from CSV data.
"""
import csv
import io
import logging
import secrets
import string
from typing import Tuple, List, Dict, Any, Optional

from app.modules.imports.models import ImportResult, ImportedCompany
from app.modules.imports.repositories import UserImportRepository, CompanyImportRepository

logger = logging.getLogger(__name__)


def generate_temp_password(length: int = 12) -> str:
    """Generate a random temporary password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class ImportCompaniesUseCase:
    """Use case for importing companies from CSV."""

    REQUIRED_COLUMNS = ['name', 'admin_email']

    def __init__(
        self,
        user_repository: Optional[UserImportRepository] = None,
        company_repository: Optional[CompanyImportRepository] = None
    ):
        """
        Initialize the use case.

        Args:
            user_repository: Optional repository instance (for testing)
            company_repository: Optional repository instance (for testing)
        """
        self.user_repository = user_repository or UserImportRepository()
        self.company_repository = company_repository or CompanyImportRepository()

    def execute(
        self,
        csv_content: str
    ) -> Tuple[ImportResult, List[ImportedCompany], Optional[str]]:
        """
        Import companies from CSV content.

        Args:
            csv_content: The CSV file content as a string

        Returns:
            Tuple of (ImportResult, list of ImportedCompany, error_message)
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

        # Get admin role
        admin_role = self.user_repository.get_admin_role()
        if not admin_role:
            return ImportResult(), [], 'Admin role not found'

        result = ImportResult(total=len(rows))
        imported_companies: List[ImportedCompany] = []
        logger.info(f"Processing {len(rows)} company records for import")

        for idx, row in enumerate(rows, start=2):
            try:
                self._process_row(row, idx, admin_role, result, imported_companies)
            except Exception as e:
                result.add_error(idx, str(e))

        self.company_repository.commit()
        logger.info(f"Company import completed: {result.imported} imported, {result.skipped} skipped")

        return result, imported_companies, None

    def _process_row(
        self,
        row: Dict[str, Any],
        idx: int,
        admin_role,
        result: ImportResult,
        imported_companies: List[ImportedCompany]
    ) -> None:
        """Process a single row from the CSV."""
        name = row.get('name', '').strip()
        admin_email = row.get('admin_email', '').strip().lower()

        if not name:
            result.add_error(idx, 'Company name is required')
            return

        if not admin_email:
            result.add_error(idx, 'Admin email is required')
            return

        # Check if company exists
        if self.company_repository.company_exists(name):
            result.add_error(idx, 'Company already exists', company=name)
            return

        # Check if admin email exists
        if self.user_repository.email_exists(admin_email):
            result.add_error(idx, 'Admin email already exists', email=admin_email)
            return

        # Create company
        company = self.company_repository.create_company(
            name=name,
            trading_name=row.get('trading_name', '').strip() or None,
            abn=row.get('abn', '').strip() or None,
            acn=row.get('acn', '').strip() or None,
            email=row.get('email', '').strip() or None,
            phone=row.get('phone', '').strip() or None,
            address=row.get('address', '').strip() or None,
            website=row.get('website', '').strip() or None,
            tax_agent_number=row.get('tax_agent_number', '').strip() or None
        )

        # Create admin user
        temp_password = generate_temp_password()
        self.user_repository.create_user(
            email=admin_email,
            password=temp_password,
            first_name=row.get('admin_first_name', '').strip() or 'Admin',
            last_name=row.get('admin_last_name', '').strip() or name,
            role=admin_role,
            company_id=company.id
        )

        imported_companies.append(ImportedCompany(
            company=name,
            admin_email=admin_email,
            temp_password=temp_password
        ))
        result.add_success()
