"""
Import Result Model

Defines the structure for import operation results including
success counts, errors, and imported records.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ImportError:
    """
    Represents an error encountered during import.

    Attributes:
        row: The row number where the error occurred (1-indexed, header is row 1)
        error: Description of the error
        email: Optional email associated with the error
        service: Optional service name associated with the error
        company: Optional company name associated with the error
    """
    row: int
    error: str
    email: Optional[str] = None
    service: Optional[str] = None
    company: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {'row': self.row, 'error': self.error}
        if self.email:
            result['email'] = self.email
        if self.service:
            result['service'] = self.service
        if self.company:
            result['company'] = self.company
        return result


@dataclass
class ImportResult:
    """
    Represents the result of an import operation.

    Attributes:
        total: Total number of rows in the CSV (excluding header)
        imported: Number of successfully imported records
        updated: Number of updated records (for services import)
        skipped: Number of skipped records
        errors: List of ImportError objects
    """
    total: int = 0
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[ImportError] = field(default_factory=list)

    def add_error(self, row: int, error: str, **kwargs) -> None:
        """Add an error to the results."""
        self.errors.append(ImportError(row=row, error=error, **kwargs))
        self.skipped += 1

    def add_success(self) -> None:
        """Increment the imported count."""
        self.imported += 1

    def add_update(self) -> None:
        """Increment the updated count."""
        self.updated += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total': self.total,
            'imported': self.imported,
            'updated': self.updated,
            'skipped': self.skipped,
            'errors': [e.to_dict() for e in self.errors]
        }


@dataclass
class ImportedUser:
    """Represents an imported user with temporary credentials."""
    email: str
    name: str
    temp_password: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'name': self.name,
            'temp_password': self.temp_password
        }


@dataclass
class ImportedServiceRequest:
    """Represents an imported service request."""
    request_number: str
    client: str
    service: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_number': self.request_number,
            'client': self.client,
            'service': self.service,
            'status': self.status
        }


@dataclass
class ImportedCompany:
    """Represents an imported company with admin credentials."""
    company: str
    admin_email: str
    temp_password: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'company': self.company,
            'admin_email': self.admin_email,
            'temp_password': self.temp_password
        }
