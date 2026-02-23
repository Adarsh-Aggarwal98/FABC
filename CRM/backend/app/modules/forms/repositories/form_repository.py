"""
Form Repository - Data Access Layer for Form entities
"""
from typing import Optional, List
from app.common.repository import BaseRepository
from app.modules.forms.models.form import Form


class FormRepository(BaseRepository[Form]):
    """Repository for Form data access"""
    model = Form

    def find_by_name(self, name: str) -> Optional[Form]:
        """Find form by name"""
        return Form.query.filter_by(name=name).first()

    def get_forms_paginated(self, form_type: str = None, active_only: bool = True,
                            page: int = 1, per_page: int = 20):
        """Get paginated list of forms"""
        query = Form.query

        if form_type:
            query = query.filter_by(form_type=form_type)
        if active_only:
            query = query.filter_by(is_active=True)

        query = query.order_by(Form.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_active_forms(self, form_type: str = None) -> List[Form]:
        """Get all active forms"""
        query = Form.query.filter_by(is_active=True)
        if form_type:
            query = query.filter_by(form_type=form_type)
        return query.order_by(Form.created_at.desc()).all()
