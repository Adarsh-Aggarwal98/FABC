"""
Get Template Use Case

Handles generation of CSV templates for import operations.
"""
import csv
import io
import logging
from typing import Tuple, Optional

from app.modules.imports.models import ImportTemplate
from app.modules.imports.schemas import get_template, get_available_template_types

logger = logging.getLogger(__name__)


class GetTemplateUseCase:
    """Use case for generating CSV import templates."""

    @staticmethod
    def execute(data_type: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Generate a CSV template for the specified data type.

        Args:
            data_type: The type of data template to generate

        Returns:
            Tuple of (csv_content, filename, error_message)
            If successful, error_message is None
            If failed, csv_content and filename are None
        """
        logger.info(f"Generating template for data type: {data_type}")

        try:
            template = get_template(data_type)
        except ValueError as e:
            valid_types = get_available_template_types()
            logger.warning(f"Invalid template type requested: {data_type}")
            return None, None, f'Unknown data type: {data_type}. Valid types: {", ".join(valid_types)}'

        logger.debug(f"Generating template for {data_type} with {len(template.columns)} columns")

        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=template.columns)
        writer.writeheader()
        for row in template.sample_rows:
            writer.writerow(row)

        return output.getvalue(), template.filename, None
