"""
Document Routes - API Endpoints for Document Management
========================================================

This module provides HTTP endpoints for document upload, download, and management.
Documents can be stored in multiple backends:
- Google Drive (OAuth or Apps Script)
- SharePoint / OneDrive
- Azure Blob Storage
- Zoho Drive
- Local filesystem (fallback)

Endpoints:
---------
CRUD Operations:
    POST   /documents               - Upload new document
    GET    /documents               - List documents (filtered by request or user)
    GET    /documents/<id>          - Get document details
    DELETE /documents/<id>          - Delete document (soft delete)

Download/View:
    GET    /documents/<id>/download - Get download URL (short expiry)
    GET    /documents/<id>/view     - Get view URL (long expiry for browser)
    GET    /documents/local/<file>  - Download local file (fallback)

Sharing:
    POST   /documents/<id>/share    - Create sharing link

Metadata:
    GET    /documents/categories    - List valid document categories

Security:
---------
- Users can only access their own documents or documents attached to their requests
- Admins and accountants can access all documents
- Document owners and admins can create sharing links

Author: CRM Development Team
"""

import os
import logging
import requests as http_requests
from io import BytesIO
from flask import request, jsonify, current_app, send_file, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.modules.documents import documents_bp
from app.modules.documents.services.document_service import DocumentService
from app.modules.documents.models.document import Document
from app.modules.documents.repositories.document_repository import DocumentRepository
from app.modules.user.models import User, Role
from app.modules.services.models import ServiceRequest

# Configure module-level logger
logger = logging.getLogger(__name__)


@documents_bp.route('', methods=['POST'])
@jwt_required()
def upload_document():
    """
    Upload a new document to the system.

    Documents are automatically stored in the configured storage backend
    (Google Drive, SharePoint, Azure Blob, or local filesystem).

    Form Data:
        file (required): The file to upload
        service_request_id: Link document to a service request
        category: Document category (supporting_document, id_proof, etc.)
        description: Optional description

    Returns:
        201: Document uploaded successfully
        400: No file provided or invalid file type
        403: User cannot upload to this request
        404: Service request not found
    """
    user_id = get_jwt_identity()
    logger.info(f"POST /documents - Upload request by user_id={user_id}")

    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400

    file = request.files['file']
    service_request_id = request.form.get('service_request_id')
    category = request.form.get('category', 'supporting_document')
    description = request.form.get('description')

    # Validate category
    if category not in Document.VALID_CATEGORIES:
        category = Document.CATEGORY_OTHER

    # If service_request_id provided, validate user has access
    if service_request_id:
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return jsonify({
                'success': False,
                'error': 'Service request not found'
            }), 404

        user = User.query.get(user_id)
        # Users can only upload to their own requests
        # Admins/Accountants can upload to any request
        if user.role.name == Role.USER and service_request.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'You can only upload documents to your own requests'
            }), 403

    result = DocumentService.upload_document(
        file=file,
        user_id=user_id,
        service_request_id=service_request_id,
        category=category,
        description=description
    )

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """List documents - filtered by service_request_id or user's documents"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    service_request_id = request.args.get('service_request_id')

    if service_request_id:
        # Get documents for a specific request
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return jsonify({
                'success': False,
                'error': 'Service request not found'
            }), 404

        # Check access - users can only see their own request documents
        if user.role.name == Role.USER and service_request.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        documents = DocumentService.get_documents_for_request(service_request_id)
    else:
        # Get user's documents
        if user.role.name in [Role.SUPER_ADMIN, Role.ADMIN]:
            # Admins can see all documents
            all_docs = DocumentRepository.get_all(limit=100)
            documents = [doc.to_dict() for doc in all_docs]
        else:
            documents = DocumentService.get_documents_for_user(user_id)

    return jsonify({
        'success': True,
        'documents': documents
    })


@documents_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get document details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = DocumentService.get_document(document_id)
    if not document:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404

    # Check access
    if user.role.name == Role.USER:
        if document.uploaded_by_id != user_id:
            # Check if document belongs to user's request
            if document.service_request_id:
                service_request = ServiceRequest.query.get(document.service_request_id)
                if not service_request or service_request.user_id != user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied'
                    }), 403
            else:
                return jsonify({
                    'success': False,
                    'error': 'Access denied'
                }), 403

    return jsonify({
        'success': True,
        'document': document.to_dict()
    })


@documents_bp.route('/<document_id>/download', methods=['GET'])
@jwt_required()
def get_download_url(document_id):
    """Get download URL for a document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = DocumentService.get_document(document_id)
    if not document:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404

    # Check access
    if user.role.name == Role.USER:
        if document.uploaded_by_id != user_id:
            if document.service_request_id:
                service_request = ServiceRequest.query.get(document.service_request_id)
                if not service_request or service_request.user_id != user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied'
                    }), 403
            else:
                return jsonify({
                    'success': False,
                    'error': 'Access denied'
                }), 403

    result = DocumentService.get_download_url(document_id)
    return jsonify(result)


@documents_bp.route('/<document_id>/share', methods=['POST'])
@jwt_required()
def create_sharing_link(document_id):
    """Create a sharing link for a document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Only admins and document owners can create sharing links
    document = DocumentService.get_document(document_id)
    if not document:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404

    if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN] and document.uploaded_by_id != user_id:
        return jsonify({
            'success': False,
            'error': 'Permission denied'
        }), 403

    result = DocumentService.create_sharing_link(document_id)
    return jsonify(result)


@documents_bp.route('/<document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    is_admin = user.role.name in [Role.SUPER_ADMIN, Role.ADMIN]

    result = DocumentService.delete_document(
        document_id=document_id,
        user_id=user_id,
        is_admin=is_admin
    )

    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400 if 'Permission' in result.get('error', '') else 404


@documents_bp.route('/<document_id>/view', methods=['GET'])
@jwt_required()
def get_view_url(document_id):
    """Get view URL for a document (longer expiry for viewing in browser)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = DocumentService.get_document(document_id)
    if not document:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404

    # Check access
    if user.role.name == Role.USER:
        if document.uploaded_by_id != user_id:
            if document.service_request_id:
                service_request = ServiceRequest.query.get(document.service_request_id)
                if not service_request or service_request.user_id != user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied'
                    }), 403
            else:
                return jsonify({
                    'success': False,
                    'error': 'Access denied'
                }), 403

    result = DocumentService.get_view_url(document_id)
    return jsonify(result)


@documents_bp.route('/<document_id>/proxy', methods=['GET'])
@jwt_required(locations=['headers', 'query_string'])
def proxy_document(document_id):
    """Proxy document content through the server to avoid CORS/auth issues with external storage"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    document = DocumentService.get_document(document_id)
    if not document:
        return jsonify({'success': False, 'error': 'Document not found'}), 404

    # Check access
    if user.role.name == Role.USER:
        if document.uploaded_by_id != user_id:
            if document.service_request_id:
                service_request = ServiceRequest.query.get(document.service_request_id)
                if not service_request or service_request.user_id != user_id:
                    return jsonify({'success': False, 'error': 'Access denied'}), 403
            else:
                return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Get download URL from storage provider
    result = DocumentService.get_download_url(document_id)
    if not result.get('success') or not result.get('download_url'):
        return jsonify({'success': False, 'error': 'Could not get download URL'}), 500

    try:
        # Fetch file content from storage provider
        resp = http_requests.get(result['download_url'], timeout=30, stream=True)
        if resp.status_code != 200:
            return jsonify({'success': False, 'error': f'Storage returned {resp.status_code}'}), 502

        # Determine content type
        content_type = document.mime_type or resp.headers.get('Content-Type', 'application/octet-stream')

        return Response(
            resp.content,
            status=200,
            content_type=content_type,
            headers={
                'Cache-Control': 'private, max-age=3600',
                'Content-Disposition': f'inline; filename="{document.original_filename}"',
            }
        )
    except Exception as e:
        logger.error(f'Proxy error for document {document_id}: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch document'}), 502


@documents_bp.route('/local/<filename>', methods=['GET'])
@jwt_required()
def download_local_file(filename):
    """Download a locally stored file (fallback when blob storage not configured)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Find document by stored filename
    document = DocumentRepository.get_by_stored_filename(filename)
    if not document:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404

    # Check access
    if user.role.name == Role.USER:
        if document.uploaded_by_id != user_id:
            if document.service_request_id:
                service_request = ServiceRequest.query.get(document.service_request_id)
                if not service_request or service_request.user_id != user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied'
                    }), 403
            else:
                return jsonify({
                    'success': False,
                    'error': 'Access denied'
                }), 403

    # Build file path
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if document.service_request_id:
        file_path = os.path.join(
            upload_dir, 'requests', document.service_request_id,
            document.document_category or 'other', document.stored_filename
        )
    else:
        file_path = os.path.join(
            upload_dir, 'general',
            document.document_category or 'other', document.stored_filename
        )

    if not os.path.exists(file_path):
        return jsonify({
            'success': False,
            'error': 'File not found on server'
        }), 404

    return send_file(
        file_path,
        download_name=document.original_filename,
        as_attachment=True
    )


@documents_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get list of valid document categories"""
    categories = [
        {'value': Document.CATEGORY_SUPPORTING, 'label': 'Supporting Document'},
        {'value': Document.CATEGORY_ID_PROOF, 'label': 'ID Proof'},
        {'value': Document.CATEGORY_TAX_DOCUMENT, 'label': 'Tax Document'},
        {'value': Document.CATEGORY_FINANCIAL_STATEMENT, 'label': 'Financial Statement'},
        {'value': Document.CATEGORY_INVOICE, 'label': 'Invoice'},
        {'value': Document.CATEGORY_OTHER, 'label': 'Other'},
    ]

    return jsonify({
        'success': True,
        'categories': categories
    })


@documents_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_documents(user_id):
    """
    Get documents for a specific user.

    Only admins/accountants can access documents for other users.
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 401

    # Check permission - only admins can view other users' documents
    if current_user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
        if current_user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

    # Get documents for the user
    documents = DocumentRepository.get_for_user(user_id, limit=100)

    return jsonify({
        'success': True,
        'documents': [doc.to_dict() for doc in documents]
    })
