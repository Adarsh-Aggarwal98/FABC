"""
Document Repository
===================
Repository pattern implementation for Document data access.
Handles all database operations for documents.
"""
from typing import List, Optional
from app.extensions import db
from app.modules.documents.models.document import Document


class DocumentRepository:
    """Repository for Document database operations"""

    @staticmethod
    def get_by_id(document_id: str) -> Optional[Document]:
        """
        Get a document by ID.

        Args:
            document_id: The document ID

        Returns:
            Document or None if not found
        """
        return Document.query.get(document_id)

    @staticmethod
    def get_active_by_id(document_id: str) -> Optional[Document]:
        """
        Get an active document by ID.

        Args:
            document_id: The document ID

        Returns:
            Document or None if not found or inactive
        """
        document = Document.query.get(document_id)
        if document and document.is_active:
            return document
        return None

    @staticmethod
    def get_by_stored_filename(filename: str, active_only: bool = True) -> Optional[Document]:
        """
        Get a document by stored filename.

        Args:
            filename: The stored filename
            active_only: Whether to only return active documents

        Returns:
            Document or None if not found
        """
        query = Document.query.filter_by(stored_filename=filename)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.first()

    @staticmethod
    def get_for_service_request(service_request_id: str, active_only: bool = True) -> List[Document]:
        """
        Get all documents for a service request.

        Args:
            service_request_id: The service request ID
            active_only: Whether to only return active documents

        Returns:
            List of documents
        """
        query = Document.query.filter_by(service_request_id=service_request_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Document.created_at.desc()).all()

    @staticmethod
    def get_for_user(user_id: str, limit: int = 50, active_only: bool = True) -> List[Document]:
        """
        Get documents uploaded by a user.

        Args:
            user_id: The user ID
            limit: Maximum number of documents to return
            active_only: Whether to only return active documents

        Returns:
            List of documents
        """
        query = Document.query.filter_by(uploaded_by_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Document.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_by_client_folder(client_name: str, limit: int = 100, active_only: bool = True) -> List[Document]:
        """
        Get all documents for a specific client folder name.

        Args:
            client_name: The client name used for folder organization
            limit: Maximum number of documents to return
            active_only: Whether to only return active documents

        Returns:
            List of documents
        """
        query = Document.query.filter_by(client_folder_name=client_name)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Document.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all(limit: int = 100, active_only: bool = True) -> List[Document]:
        """
        Get all documents.

        Args:
            limit: Maximum number of documents to return
            active_only: Whether to only return active documents

        Returns:
            List of documents
        """
        query = Document.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Document.created_at.desc()).limit(limit).all()

    @staticmethod
    def create(document: Document) -> Document:
        """
        Create a new document.

        Args:
            document: The document to create

        Returns:
            The created document
        """
        db.session.add(document)
        db.session.commit()
        return document

    @staticmethod
    def save(document: Document) -> Document:
        """
        Save changes to a document.

        Args:
            document: The document to save

        Returns:
            The saved document
        """
        db.session.commit()
        return document

    @staticmethod
    def soft_delete(document: Document) -> Document:
        """
        Soft delete a document by marking it as inactive.

        Args:
            document: The document to delete

        Returns:
            The deleted document
        """
        document.is_active = False
        db.session.commit()
        return document

    @staticmethod
    def hard_delete(document: Document) -> None:
        """
        Permanently delete a document from the database.

        Args:
            document: The document to delete
        """
        db.session.delete(document)
        db.session.commit()

    @staticmethod
    def rollback() -> None:
        """Rollback the current transaction."""
        db.session.rollback()

    @staticmethod
    def flush() -> None:
        """Flush pending changes without committing."""
        db.session.flush()
