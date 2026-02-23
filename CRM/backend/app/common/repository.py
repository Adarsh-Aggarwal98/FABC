"""
Base Repository Pattern
========================

Repositories handle data access and persistence operations.
They abstract the database layer from the business logic.

Architecture Benefits:
    - Single Responsibility: Repositories only handle data access
    - Testability: Easy to mock for unit tests
    - Flexibility: Can switch databases without changing business logic
    - Reusability: Generic Repository works with any model

Usage Examples:

    # Option 1: Use Repository directly (RECOMMENDED for simple CRUD)
    # No subclass needed - just pass the model class!

    from app.common.repository import Repository
    from app.modules.company.models import Company

    repo = Repository(Company)

    # Create
    company = Company(name="Acme Corp")
    repo.create(company)
    repo.save()  # Commits the transaction

    # Read
    company = repo.get_by_id("123")
    companies = repo.find_all_by(is_active=True)
    exists = repo.exists(name="Acme Corp")

    # Search with pagination
    results = repo.search(
        search_term="acme",
        search_fields=["name", "email"],
        filters={"is_active": True},
        page=1,
        per_page=20
    )

    # Update
    company.name = "New Name"
    repo.save()

    # Delete
    repo.delete(company)
    repo.save()

    # Option 2: Create custom repository ONLY if you need custom queries

    class CompanyRepository(BaseRepository[Company]):
        model = Company

        def find_by_abn(self, abn: str) -> Optional[Company]:
            '''Custom query that can't be done with generic methods'''
            self.logger.debug(f"Finding company by ABN: {abn}")
            return self.model.query.filter_by(abn=abn).first()

        def search_with_joins(self, term: str) -> List[Company]:
            '''Complex query with joins'''
            return self.model.query.join(...).filter(...).all()

Author: Refactored for DRY principle
"""
import logging
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

# Type variable for generic repository
T = TypeVar('T')

# Configure module logger
logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations.

    This class implements the Repository Pattern, providing a clean abstraction
    over the database layer. All data access should go through repositories.

    Attributes:
        model: The SQLAlchemy model class this repository manages
        logger: Logger instance for this repository

    Example:
        class UserRepository(BaseRepository[User]):
            model = User

            def find_active_admins(self):
                return self.model.query.filter_by(is_active=True, role='admin').all()
    """

    model: Type[T] = None

    def __init__(self):
        """
        Initialize the repository.

        Raises:
            NotImplementedError: If model class attribute is not defined
        """
        if self.model is None:
            raise NotImplementedError(
                f"Repository {self.__class__.__name__} must define a 'model' class attribute. "
                f"Example: model = User"
            )
        # Create logger with repository name for better tracing
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initialized repository for model: {self.model.__name__}")

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get a single entity by its primary key.

        Args:
            id: The primary key value (can be int, str, uuid, etc.)

        Returns:
            The entity if found, None otherwise

        Example:
            user = repo.get_by_id(123)
            company = repo.get_by_id("uuid-string")
        """
        self.logger.debug(f"Getting {self.model.__name__} by ID: {id}")
        try:
            entity = self.model.query.get(id)
            if entity:
                self.logger.debug(f"Found {self.model.__name__} with ID: {id}")
            else:
                self.logger.debug(f"No {self.model.__name__} found with ID: {id}")
            return entity
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting {self.model.__name__} by ID {id}: {e}")
            raise

    def get_all(self) -> List[T]:
        """
        Get all entities of this type.

        Warning: Use with caution on large tables. Consider using get_paginated instead.

        Returns:
            List of all entities
        """
        self.logger.debug(f"Getting all {self.model.__name__} entities")
        try:
            entities = self.model.query.all()
            self.logger.debug(f"Found {len(entities)} {self.model.__name__} entities")
            return entities
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting all {self.model.__name__}: {e}")
            raise

    def get_paginated(self, page: int = 1, per_page: int = 20, filters: Dict = None) -> Any:
        """
        Get paginated results with optional filters.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            filters: Dictionary of field=value filters

        Returns:
            Flask-SQLAlchemy Pagination object with:
                - items: List of entities for current page
                - total: Total number of matching entities
                - pages: Total number of pages
                - page: Current page number
                - has_next/has_prev: Boolean flags

        Example:
            # Get page 2 of active users, 10 per page
            result = repo.get_paginated(page=2, per_page=10, filters={'is_active': True})
            for user in result.items:
                print(user.name)
        """
        self.logger.debug(
            f"Getting paginated {self.model.__name__} - page: {page}, "
            f"per_page: {per_page}, filters: {filters}"
        )
        try:
            query = self.model.query

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.filter(getattr(self.model, key) == value)
                        self.logger.debug(f"Applied filter: {key}={value}")

            result = query.paginate(page=page, per_page=per_page, error_out=False)
            self.logger.debug(
                f"Pagination result: {len(result.items)} items, "
                f"page {result.page}/{result.pages}, total: {result.total}"
            )
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in paginated query: {e}")
            raise

    def find_by(self, **kwargs) -> Optional[T]:
        """
        Find a single entity by attributes.

        Args:
            **kwargs: Field=value pairs to filter by

        Returns:
            First matching entity or None

        Example:
            user = repo.find_by(email="john@example.com")
            company = repo.find_by(abn="12345678901", is_active=True)
        """
        self.logger.debug(f"Finding {self.model.__name__} by: {kwargs}")
        try:
            entity = self.model.query.filter_by(**kwargs).first()
            if entity:
                self.logger.debug(f"Found {self.model.__name__} matching criteria")
            else:
                self.logger.debug(f"No {self.model.__name__} found matching criteria")
            return entity
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_by: {e}")
            raise

    def find_all_by(self, **kwargs) -> List[T]:
        """
        Find all entities matching attributes.

        Args:
            **kwargs: Field=value pairs to filter by

        Returns:
            List of matching entities (empty list if none found)

        Example:
            active_admins = repo.find_all_by(is_active=True, role='admin')
        """
        self.logger.debug(f"Finding all {self.model.__name__} by: {kwargs}")
        try:
            entities = self.model.query.filter_by(**kwargs).all()
            self.logger.debug(f"Found {len(entities)} {self.model.__name__} matching criteria")
            return entities
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in find_all_by: {e}")
            raise

    def find_one_or_none(self, **kwargs) -> Optional[T]:
        """
        Find exactly one entity or None.

        Unlike find_by, this raises an error if multiple matches exist.

        Args:
            **kwargs: Field=value pairs to filter by

        Returns:
            The single matching entity or None

        Raises:
            MultipleResultsFound: If more than one entity matches
        """
        self.logger.debug(f"Finding one {self.model.__name__} by: {kwargs}")
        return self.model.query.filter_by(**kwargs).one_or_none()

    def exists(self, **kwargs) -> bool:
        """
        Check if an entity exists with given attributes.

        More efficient than find_by when you only need to check existence.

        Args:
            **kwargs: Field=value pairs to check

        Returns:
            True if entity exists, False otherwise

        Example:
            if repo.exists(email="john@example.com"):
                raise ValidationError("Email already in use")
        """
        self.logger.debug(f"Checking if {self.model.__name__} exists with: {kwargs}")
        result = self.model.query.filter_by(**kwargs).first() is not None
        self.logger.debug(f"Exists check result: {result}")
        return result

    def count(self, **kwargs) -> int:
        """
        Count entities matching attributes.

        Args:
            **kwargs: Field=value pairs to filter by (optional)

        Returns:
            Number of matching entities

        Example:
            total_users = repo.count()
            active_users = repo.count(is_active=True)
        """
        self.logger.debug(f"Counting {self.model.__name__} with filters: {kwargs}")
        try:
            if kwargs:
                count = self.model.query.filter_by(**kwargs).count()
            else:
                count = self.model.query.count()
            self.logger.debug(f"Count result: {count}")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in count: {e}")
            raise

    def search(self, search_term: str, search_fields: List[str], page: int = 1,
               per_page: int = 20, filters: Dict = None, order_by: str = None,
               order_desc: bool = True) -> Any:
        """
        Search entities with text search across multiple fields.

        Performs case-insensitive LIKE search across specified fields.

        Args:
            search_term: The text to search for (will be wrapped with %)
            search_fields: List of field names to search in
            page: Page number for pagination
            per_page: Items per page
            filters: Additional exact-match filter criteria
            order_by: Field name to order results by
            order_desc: If True, order descending; else ascending

        Returns:
            Pagination object with matching entities

        Example:
            # Search users by name or email
            results = repo.search(
                search_term="john",
                search_fields=["first_name", "last_name", "email"],
                filters={"is_active": True},
                order_by="created_at",
                order_desc=True
            )
        """
        self.logger.info(
            f"Searching {self.model.__name__} - term: '{search_term}', "
            f"fields: {search_fields}, filters: {filters}"
        )
        try:
            query = self.model.query

            # Apply exact-match filters first
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.filter(getattr(self.model, key) == value)

            # Apply text search with OR across all specified fields
            if search_term and search_fields:
                search_pattern = f'%{search_term}%'
                conditions = []
                for field in search_fields:
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field).ilike(search_pattern))
                    else:
                        self.logger.warning(
                            f"Search field '{field}' does not exist on {self.model.__name__}"
                        )
                if conditions:
                    query = query.filter(or_(*conditions))

            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_col = getattr(self.model, order_by)
                query = query.order_by(desc(order_col) if order_desc else asc(order_col))

            result = query.paginate(page=page, per_page=per_page, error_out=False)
            self.logger.info(f"Search found {result.total} results")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in search: {e}")
            raise

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    def create(self, entity: T) -> T:
        """
        Create a new entity (add to session).

        Note: Call save() to commit the transaction.

        Args:
            entity: The entity instance to create

        Returns:
            The created entity (with ID populated after flush)

        Example:
            user = User(name="John", email="john@example.com")
            repo.create(user)
            repo.save()  # Commit transaction
            print(user.id)  # ID is now available
        """
        self.logger.info(f"Creating new {self.model.__name__}")
        try:
            db.session.add(entity)
            db.session.flush()  # Flush to get ID without committing
            self.logger.info(f"Created {self.model.__name__} with ID: {getattr(entity, 'id', 'N/A')}")
            return entity
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating {self.model.__name__}: {e}")
            raise

    def update(self, entity: T) -> T:
        """
        Update an existing entity.

        The entity should already be modified. This method just flushes changes.

        Args:
            entity: The modified entity

        Returns:
            The updated entity

        Example:
            user = repo.get_by_id(123)
            user.name = "New Name"
            repo.update(user)
            repo.save()
        """
        self.logger.info(f"Updating {self.model.__name__} with ID: {getattr(entity, 'id', 'N/A')}")
        try:
            db.session.flush()
            self.logger.debug(f"Update flushed for {self.model.__name__}")
            return entity
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating {self.model.__name__}: {e}")
            raise

    def delete(self, entity: T) -> bool:
        """
        Delete an entity (hard delete).

        Note: Call save() to commit the transaction.

        Args:
            entity: The entity to delete

        Returns:
            True if successful

        Example:
            user = repo.get_by_id(123)
            repo.delete(user)
            repo.save()
        """
        entity_id = getattr(entity, 'id', 'N/A')
        self.logger.info(f"Deleting {self.model.__name__} with ID: {entity_id}")
        try:
            db.session.delete(entity)
            self.logger.info(f"Deleted {self.model.__name__} with ID: {entity_id}")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"Database error deleting {self.model.__name__}: {e}")
            raise

    def soft_delete(self, entity: T, field: str = 'is_active') -> T:
        """
        Soft delete by setting a boolean field to False.

        Args:
            entity: The entity to soft delete
            field: The boolean field to set to False (default: 'is_active')

        Returns:
            The updated entity

        Example:
            user = repo.get_by_id(123)
            repo.soft_delete(user)  # Sets is_active = False
            repo.save()
        """
        entity_id = getattr(entity, 'id', 'N/A')
        self.logger.info(f"Soft deleting {self.model.__name__} with ID: {entity_id}")
        if hasattr(entity, field):
            setattr(entity, field, False)
            db.session.flush()
            self.logger.info(f"Soft deleted {self.model.__name__} (set {field}=False)")
        else:
            self.logger.warning(
                f"Cannot soft delete {self.model.__name__}: field '{field}' does not exist"
            )
        return entity

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    def bulk_create(self, entities: List[T]) -> List[T]:
        """
        Create multiple entities at once.

        More efficient than calling create() multiple times.

        Args:
            entities: List of entities to create

        Returns:
            List of created entities

        Example:
            users = [User(name="A"), User(name="B"), User(name="C")]
            repo.bulk_create(users)
            repo.save()
        """
        self.logger.info(f"Bulk creating {len(entities)} {self.model.__name__} entities")
        try:
            db.session.add_all(entities)
            db.session.flush()
            self.logger.info(f"Bulk created {len(entities)} {self.model.__name__} entities")
            return entities
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in bulk create: {e}")
            raise

    def bulk_update(self, filters: Dict, updates: Dict) -> int:
        """
        Update multiple entities matching filters.

        Args:
            filters: Dictionary of conditions to match
            updates: Dictionary of fields to update

        Returns:
            Number of entities updated

        Example:
            # Deactivate all users from a company
            count = repo.bulk_update(
                filters={'company_id': '123'},
                updates={'is_active': False}
            )
        """
        self.logger.info(
            f"Bulk updating {self.model.__name__} - filters: {filters}, updates: {updates}"
        )
        try:
            count = self.model.query.filter_by(**filters).update(updates)
            self.logger.info(f"Bulk updated {count} {self.model.__name__} entities")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in bulk update: {e}")
            raise

    # =========================================================================
    # TRANSACTION CONTROL
    # =========================================================================

    def save(self) -> None:
        """
        Commit the current transaction.

        Call this after create/update/delete operations to persist changes.

        Example:
            repo.create(user)
            repo.save()  # Changes are now permanent
        """
        self.logger.debug("Committing transaction")
        try:
            db.session.commit()
            self.logger.debug("Transaction committed successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"Database error committing transaction: {e}")
            db.session.rollback()
            raise

    def rollback(self) -> None:
        """
        Rollback the current transaction.

        Call this to undo any pending changes.

        Example:
            try:
                repo.create(user)
                repo.save()
            except Exception:
                repo.rollback()
                raise
        """
        self.logger.warning("Rolling back transaction")
        db.session.rollback()


class Repository(BaseRepository[T]):
    """
    Generic repository that can be used directly without subclassing.

    This is the RECOMMENDED way to use repositories for simple CRUD operations.
    No need to create a custom repository class for each model!

    Usage:
        from app.common.repository import Repository
        from app.modules.company.models import Company

        # Create repository instance
        repo = Repository(Company)

        # Use all BaseRepository methods
        company = repo.get_by_id("123")
        companies = repo.find_all_by(is_active=True)

        new_company = Company(name="Acme")
        repo.create(new_company)
        repo.save()
    """

    def __init__(self, model_class: Type[T]):
        """
        Initialize the generic repository with a model class.

        Args:
            model_class: The SQLAlchemy model class to use

        Example:
            repo = Repository(User)
            repo = Repository(Company)
        """
        self.model = model_class
        self.logger = logging.getLogger(f"{__name__}.Repository[{model_class.__name__}]")
        self.logger.debug(f"Initialized generic repository for: {model_class.__name__}")


def get_repository(model_class: Type[T]) -> Repository[T]:
    """
    Factory function to get a repository for any model.

    Convenience function that's slightly more readable than Repository(Model).

    Args:
        model_class: The SQLAlchemy model class

    Returns:
        A Repository instance for that model

    Example:
        repo = get_repository(Company)
        company = repo.get_by_id("123")
    """
    return Repository(model_class)
