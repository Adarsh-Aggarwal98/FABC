"""Letters API Routes — Engagement & Representation letter generation for SMSF funds"""
import os
import io
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db
from ..models.letter import AuditLetter
from app.modules.client_entity.models import ClientEntity

letters_bp = Blueprint('letters', __name__, url_prefix='/api/letters')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'uploads', 'letters')


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            from app.modules.user.models import User
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            if user.role.name not in ['super_admin', 'admin', 'accountant']:
                return jsonify({'success': False, 'error': 'Access required'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Auth error: {str(e)}")
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return wrapper


def _ensure_upload_dir():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── LIST & CREATE ─────────────────────────────────────────────────────────

@letters_bp.route('', methods=['GET'])
@admin_required
def list_letters():
    """List all letters with optional filters."""
    try:
        query = AuditLetter.query

        entity_id = request.args.get('client_entity_id')
        if entity_id:
            query = query.filter_by(client_entity_id=entity_id)

        letter_type = request.args.get('letter_type')
        if letter_type in AuditLetter.VALID_LETTER_TYPES:
            query = query.filter_by(letter_type=letter_type)

        status = request.args.get('status')
        if status in AuditLetter.VALID_STATUSES:
            query = query.filter_by(status=status)

        financial_year = request.args.get('financial_year')
        if financial_year:
            query = query.filter_by(financial_year=financial_year)

        letters = query.order_by(AuditLetter.created_at.desc()).all()
        return jsonify({'success': True, 'letters': [l.to_dict() for l in letters]})
    except Exception as e:
        current_app.logger.error(f"Error listing letters: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch letters'}), 500


@letters_bp.route('', methods=['POST'])
@admin_required
def create_letter():
    """
    Create a new letter record.

    Required body fields:
      - client_entity_id  (must be an existing ClientEntity, typically SMSF type)
      - letter_type       ('engagement' or 'representation')
      - financial_year    (e.g. '2025' for FY ending 30 June 2025)

    Optional:
      - letter_date, auditor_name, auditor_registration, auditor_address
      - trustees (list of {name, company, role})
    """
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()

        # Validate required fields
        entity_id = data.get('client_entity_id')
        if not entity_id:
            return jsonify({'success': False, 'error': 'client_entity_id is required'}), 400

        # Verify the entity exists (this ties the letter to a real client)
        entity = ClientEntity.query.get(entity_id)
        if not entity:
            return jsonify({'success': False, 'error': 'Client entity not found'}), 404

        letter_type = data.get('letter_type', 'engagement')
        if letter_type not in AuditLetter.VALID_LETTER_TYPES:
            return jsonify({'success': False, 'error': 'Invalid letter_type'}), 400

        financial_year = str(data.get('financial_year', '')).strip()
        if not financial_year:
            return jsonify({'success': False, 'error': 'financial_year is required'}), 400

        # Build trustees list — seed from entity trustee_name if not provided
        trustees = data.get('trustees', [])
        if not trustees and entity.trustee_name:
            trustees = [{'name': entity.trustee_name, 'company': '', 'role': 'Trustee',
                         'signature_b64': None, 'signed_date': None}]

        letter = AuditLetter(
            client_entity_id=entity_id,
            letter_type=letter_type,
            financial_year=financial_year,
            letter_date=data.get('letter_date', datetime.utcnow().strftime('%d %B %Y')),
            status='draft',
            auditor_name=data.get('auditor_name', 'AusSuperSource'),
            auditor_registration=data.get('auditor_registration', ''),
            auditor_address=data.get('auditor_address', ''),
            trustees_data=trustees,
            created_by_id=current_user_id,
        )
        db.session.add(letter)
        db.session.commit()

        current_app.logger.info(
            f"Letter created: {letter.id} ({letter_type}) for entity {entity.name} FY{financial_year}"
        )
        return jsonify({'success': True, 'letter': letter.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating letter: {e}")
        return jsonify({'success': False, 'error': 'Failed to create letter'}), 500


# ─── GET / UPDATE / DELETE ─────────────────────────────────────────────────

@letters_bp.route('/<int:letter_id>', methods=['GET'])
@admin_required
def get_letter(letter_id):
    """Get a single letter record."""
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        return jsonify({'success': True, 'letter': letter.to_dict()})
    except Exception as e:
        current_app.logger.error(f"Error fetching letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch letter'}), 500


@letters_bp.route('/<int:letter_id>', methods=['PATCH'])
@admin_required
def update_letter(letter_id):
    """Update letter metadata (date, auditor, trustees, status)."""
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        data = request.get_json() or {}

        if 'letter_date' in data:
            letter.letter_date = str(data['letter_date'])[:50]
        if 'auditor_name' in data:
            letter.auditor_name = str(data['auditor_name'])[:200]
        if 'auditor_registration' in data:
            letter.auditor_registration = str(data['auditor_registration'])[:100]
        if 'auditor_address' in data:
            letter.auditor_address = str(data['auditor_address'])[:500]
        if 'financial_year' in data:
            letter.financial_year = str(data['financial_year'])[:20]
        if 'trustees' in data and isinstance(data['trustees'], list):
            letter.trustees_data = data['trustees']
        if 'status' in data and data['status'] in AuditLetter.VALID_STATUSES:
            letter.status = data['status']

        db.session.commit()
        return jsonify({'success': True, 'letter': letter.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to update letter'}), 500


@letters_bp.route('/<int:letter_id>', methods=['DELETE'])
@admin_required
def delete_letter(letter_id):
    """Delete a letter record and its PDF files."""
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        # Clean up PDF files
        for path in [letter.pdf_path, letter.signed_pdf_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        db.session.delete(letter)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Letter deleted'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete letter'}), 500


# ─── PDF GENERATION ────────────────────────────────────────────────────────

@letters_bp.route('/<int:letter_id>/pdf', methods=['GET'])
@admin_required
def get_pdf(letter_id):
    """
    Stream the generated PDF for this letter.
    Always regenerates from current data so edits are reflected immediately.
    Set ?download=1 to force browser download.
    """
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        entity = letter.client_entity

        from app.modules.letters.services.pdf_generator import LetterPDFGenerator
        context = LetterPDFGenerator.build_context(letter, entity)
        pdf_bytes = LetterPDFGenerator.generate_pdf_bytes(letter.letter_type, context)

        download = request.args.get('download', '0') == '1'
        filename = (
            f"{entity.name.replace(' ', '_')}_{letter.letter_type}_{letter.financial_year}.pdf"
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=download,
            download_name=filename,
        )
    except Exception as e:
        current_app.logger.error(f"Error generating PDF for letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': f'PDF generation failed: {str(e)}'}), 500


@letters_bp.route('/<int:letter_id>/preview-html', methods=['GET'])
@admin_required
def preview_html(letter_id):
    """Return rendered HTML for in-browser preview (no PDF conversion)."""
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        entity = letter.client_entity

        from app.modules.letters.services.pdf_generator import LetterPDFGenerator
        context = LetterPDFGenerator.build_context(letter, entity)
        html = LetterPDFGenerator.render_html(letter.letter_type, context)

        from flask import Response
        return Response(html, mimetype='text/html')
    except Exception as e:
        current_app.logger.error(f"Error previewing letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── SIGNATURE ─────────────────────────────────────────────────────────────

@letters_bp.route('/<int:letter_id>/sign', methods=['PATCH'])
@admin_required
def sign_letter(letter_id):
    """
    Add a trustee signature (base64 PNG from canvas) to the letter.

    Body:
      - trustee_index  (int, 0-based index in trustees_data array)
      - signature_b64  (base64-encoded PNG string from canvas pad)
      - signed_date    (optional display date string)
    """
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        data = request.get_json() or {}

        trustee_index = data.get('trustee_index', 0)
        signature_b64 = data.get('signature_b64', '')
        signed_date = data.get('signed_date', datetime.utcnow().strftime('%d/%m/%Y'))

        trustees = list(letter.trustees_data or [])

        # Extend if needed
        while len(trustees) <= trustee_index:
            trustees.append({'name': '', 'company': '', 'role': 'Trustee',
                              'signature_b64': None, 'signed_date': None})

        trustees[trustee_index]['signature_b64'] = signature_b64
        trustees[trustee_index]['signed_date'] = signed_date

        letter.trustees_data = trustees
        letter.status = 'signed'
        db.session.commit()

        current_app.logger.info(
            f"Trustee {trustee_index} signed letter {letter_id}"
        )
        return jsonify({'success': True, 'letter': letter.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error signing letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to save signature'}), 500


# ─── UPLOAD SIGNED PDF ─────────────────────────────────────────────────────

@letters_bp.route('/<int:letter_id>/upload-signed', methods=['POST'])
@admin_required
def upload_signed_pdf(letter_id):
    """
    Upload a manually signed PDF (after downloading, printing, signing, scanning).
    Accepts multipart/form-data with a 'file' field.
    """
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        entity = letter.client_entity

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files accepted'}), 400

        _ensure_upload_dir()
        filename = (
            f"signed_{entity.name.replace(' ', '_')}_{letter.letter_type}"
            f"_{letter.financial_year}_{letter_id}.pdf"
        )
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        letter.signed_pdf_path = file_path
        letter.status = 'signed'
        db.session.commit()

        current_app.logger.info(f"Signed PDF uploaded for letter {letter_id}: {filename}")
        return jsonify({'success': True, 'message': 'Signed PDF uploaded', 'letter': letter.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading signed PDF for letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Upload failed'}), 500


@letters_bp.route('/<int:letter_id>/signed-pdf', methods=['GET'])
@admin_required
def get_signed_pdf(letter_id):
    """Stream the uploaded signed PDF."""
    try:
        letter = AuditLetter.query.get_or_404(letter_id)
        if not letter.signed_pdf_path or not os.path.exists(letter.signed_pdf_path):
            return jsonify({'success': False, 'error': 'No signed PDF on record'}), 404

        entity = letter.client_entity
        download_name = (
            f"SIGNED_{entity.name.replace(' ', '_')}_{letter.letter_type}_{letter.financial_year}.pdf"
        )
        return send_file(letter.signed_pdf_path, mimetype='application/pdf',
                         as_attachment=False, download_name=download_name)
    except Exception as e:
        current_app.logger.error(f"Error streaming signed PDF for letter {letter_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to retrieve signed PDF'}), 500
