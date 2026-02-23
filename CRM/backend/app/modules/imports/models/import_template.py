"""
Import Template Model

Defines the structure for CSV import templates with column specifications
and sample data for each import type.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ImportTemplate:
    """
    Represents a CSV import template configuration.

    Attributes:
        data_type: The type of data this template is for (e.g., 'clients', 'services')
        columns: List of column names for the CSV header
        sample_rows: List of dictionaries containing sample data
        filename: The suggested filename for the downloaded template
    """
    data_type: str
    columns: List[str]
    sample_rows: List[Dict[str, Any]]
    filename: str


@dataclass
class ImportType:
    """
    Represents metadata about an available import type.

    Attributes:
        id: Unique identifier for the import type
        name: Human-readable name
        description: Description of what this import does
        required_columns: List of required CSV columns
        optional_columns: List of optional CSV columns
    """
    id: str
    name: str
    description: str
    required_columns: List[str] = field(default_factory=list)
    optional_columns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'required_columns': self.required_columns,
            'optional_columns': self.optional_columns
        }
