"""
Import Clients Use Case

Handles the business logic for importing clients from CSV data.
"""
import csv
import io
import logging
import secrets
import string
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional

from app.modules.imports.models import ImportResult, ImportedUser
from app.modules.imports.repositories import UserImportRepository

logger = logging.getLogger(__name__)


def generate_temp_password(length: int = 12) -> str:
    """Generate a random temporary password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class ImportClientsUseCase:
    """Use case for importing clients from CSV."""

    REQUIRED_COLUMNS = ['email', 'first_name', 'last_name']

    def __init__(self, user_repository: Optional[UserImportRepository] = None):
        """
        Initialize the use case.

        Args:
            user_repository: Optional repository instance (for testing)
        """
        self.user_repository = user_repository or UserImportRepository()

    def execute(
        self,
        csv_content: str,
        company_id: int
    ) -> Tuple[ImportResult, List[ImportedUser], Optional[str]]:
        """
        Import clients from CSV content.

        Args:
            csv_content: The CSV file content as a string
            company_id: The company ID to associate clients with

        Returns:
            Tuple of (ImportResult, list of ImportedUser, error_message)
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

        # Get client role
        client_role = self.user_repository.get_client_role()
        if not client_role:
            return ImportResult(), [], 'Client role not found'

        result = ImportResult(total=len(rows))
        imported_users: List[ImportedUser] = []
        logger.info(f"Processing {len(rows)} client records for import")

        for idx, row in enumerate(rows, start=2):
            try:
                self._process_row(row, idx, company_id, client_role, result, imported_users)
            except Exception as e:
                result.add_error(idx, str(e), email=row.get('email', ''))

        self.user_repository.commit()
        logger.info(f"Client import completed: {result.imported} imported, {result.skipped} skipped")

        return result, imported_users, None

    def _process_row(
        self,
        row: Dict[str, Any],
        idx: int,
        company_id: int,
        client_role,
        result: ImportResult,
        imported_users: List[ImportedUser]
    ) -> None:
        """Process a single row from the CSV."""
        email = row.get('email', '').strip().lower()
        if not email:
            result.add_error(idx, 'Email is required')
            return

        # Check if user exists
        if self.user_repository.email_exists(email):
            result.add_error(idx, 'Email already exists', email=email)
            return

        # Generate temp password
        temp_password = generate_temp_password()

        # Parse date_of_birth
        dob = None
        if row.get('date_of_birth'):
            try:
                dob = datetime.strptime(row['date_of_birth'].strip(), '%Y-%m-%d').date()
            except ValueError:
                pass

        # Create user
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()

        self.user_repository.create_user(
            email=email,
            password=temp_password,
            first_name=first_name,
            last_name=last_name,
            role=client_role,
            company_id=company_id,
            phone=row.get('phone', '').strip() or None,
            address=row.get('address', '').strip() or None,
            date_of_birth=dob,
            occupation=row.get('occupation', '').strip() or None,
            company_name=row.get('company_name', '').strip() or None,
            abn=row.get('abn', '').strip() or None,
            tfn=row.get('tfn', '').strip() or None,
            personal_email=row.get('personal_email', '').strip() or None,
            bsb=row.get('bsb', '').strip() or None,
            bank_account_number=row.get('bank_account_number', '').strip() or None,
            bank_account_holder_name=row.get('bank_account_holder_name', '').strip() or None
        )

        imported_users.append(ImportedUser(
            email=email,
            name=f"{first_name} {last_name}".strip(),
            temp_password=temp_password
        ))
        result.add_success()
