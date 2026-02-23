"""
ClientEntity Repository
========================
Data access layer for ClientEntity.
"""

from typing import Optional, List, Tuple
from sqlalchemy import or_
from app.extensions import db
from ..models import ClientEntity


class ClientEntityRepository:
    """Repository for ClientEntity data access."""

    def get_by_id(self, entity_id: str) -> Optional[ClientEntity]:
        """Get entity by ID."""
        return ClientEntity.query.get(entity_id)

    def get_by_id_and_company(self, entity_id: str, company_id: str) -> Optional[ClientEntity]:
        """Get entity by ID, ensuring it belongs to the company."""
        return ClientEntity.query.filter_by(
            id=entity_id,
            company_id=company_id
        ).first()

    def list_by_company(
        self,
        company_id: str,
        entity_type: str = None,
        is_active: bool = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'name',
        sort_order: str = 'asc'
    ) -> Tuple[List[ClientEntity], int]:
        """List entities for a company with pagination."""
        query = ClientEntity.query.filter_by(company_id=company_id)

        # Apply filters
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        # Apply sorting
        sort_column = getattr(ClientEntity, sort_by, ClientEntity.name)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

        # Get total count
        total = query.count()

        # Apply pagination
        entities = query.offset((page - 1) * per_page).limit(per_page).all()

        return entities, total

    def search(
        self,
        company_id: str,
        query_str: str,
        entity_type: str = None,
        is_active: bool = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[ClientEntity], int]:
        """Search entities by name or ABN."""
        search_pattern = f"%{query_str}%"

        query = ClientEntity.query.filter_by(company_id=company_id).filter(
            or_(
                ClientEntity.name.ilike(search_pattern),
                ClientEntity.trading_name.ilike(search_pattern),
                ClientEntity.abn.ilike(search_pattern),
                ClientEntity.acn.ilike(search_pattern)
            )
        )

        # Apply filters
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        # Order by relevance (exact name match first, then alphabetical)
        query = query.order_by(
            ClientEntity.name.ilike(query_str).desc(),
            ClientEntity.name
        )

        # Get total count
        total = query.count()

        # Apply pagination
        entities = query.offset((page - 1) * per_page).limit(per_page).all()

        return entities, total

    def create(self, entity: ClientEntity) -> ClientEntity:
        """Create a new entity."""
        db.session.add(entity)
        db.session.flush()
        return entity

    def update(self, entity: ClientEntity, data: dict) -> ClientEntity:
        """Update an entity with the given data."""
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        db.session.flush()
        return entity

    def delete(self, entity: ClientEntity, soft: bool = True) -> None:
        """Delete an entity (soft delete by default)."""
        if soft:
            entity.is_active = False
            db.session.flush()
        else:
            db.session.delete(entity)
            db.session.flush()

    def get_by_name_and_company(self, name: str, company_id: str) -> Optional[ClientEntity]:
        """Get entity by name and company (for duplicate checking)."""
        return ClientEntity.query.filter_by(
            name=name,
            company_id=company_id
        ).first()

    def count_by_company(self, company_id: str, is_active: bool = None) -> int:
        """Count entities for a company."""
        query = ClientEntity.query.filter_by(company_id=company_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        return query.count()
