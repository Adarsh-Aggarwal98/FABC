"""SMSF Basic Data Sheet — API Routes"""
import io
from functools import wraps
from flask import Blueprint, request, jsonify, send_file, current_app, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db
from ..models.data_sheet import SMSFDataSheet
from app.modules.client_entity.models import ClientEntity

data_sheet_bp = Blueprint('smsf_data_sheet', __name__, url_prefix='/api/smsf-data-sheets')


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            from app.modules.user.models import User
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            if user.role.name not in ['super_admin', 'admin', 'accountant', 'senior_accountant']:
                return jsonify({'success': False, 'error': 'Access required'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Auth error: {e}")
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return wrapper


# ── LIST ────────────────────────────────────────────────────────────────────

@data_sheet_bp.route('', methods=['GET'])
@auth_required
def list_sheets():
    try:
        q = SMSFDataSheet.query
        entity_id = request.args.get('client_entity_id')
        if entity_id:
            q = q.filter_by(client_entity_id=entity_id)
        fy = request.args.get('financial_year')
        if fy:
            q = q.filter_by(financial_year=fy)
        sheets = q.order_by(SMSFDataSheet.created_at.desc()).all()
        return jsonify({'success': True, 'data_sheets': [s.to_dict() for s in sheets]})
    except Exception as e:
        current_app.logger.error(f"list_sheets: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch data sheets'}), 500


# ── CREATE ───────────────────────────────────────────────────────────────────

@data_sheet_bp.route('', methods=['POST'])
@auth_required
def create_sheet():
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()

        entity_id = data.get('client_entity_id')
        if not entity_id:
            return jsonify({'success': False, 'error': 'client_entity_id is required'}), 400
        entity = ClientEntity.query.get(entity_id)
        if not entity:
            return jsonify({'success': False, 'error': 'Client entity not found'}), 404

        fy = str(data.get('financial_year', '')).strip()
        if not fy:
            return jsonify({'success': False, 'error': 'financial_year is required'}), 400

        # Prevent duplicates: one sheet per entity per FY
        existing = SMSFDataSheet.query.filter_by(
            client_entity_id=entity_id, financial_year=fy
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'error': f'A data sheet already exists for FY{fy}. Update it instead.',
                'existing_id': existing.id
            }), 409

        sheet = SMSFDataSheet(
            client_entity_id = entity_id,
            financial_year   = fy,
            fund_name        = data.get('fund_name', entity.name),
            date_of_creation = data.get('date_of_creation', ''),
            abn_of_smsf      = data.get('abn_of_smsf', entity.abn or ''),
            tfn_of_smsf      = data.get('tfn_of_smsf', entity.tfn or ''),
            members          = data.get('members', []),
            trustees         = data.get('trustees', []),
            bare_trustee     = data.get('bare_trustee', {}),
            nominations      = data.get('nominations', []),
            subsequent_events= data.get('subsequent_events', []),
            created_by_id    = user_id,
        )
        db.session.add(sheet)
        db.session.commit()
        current_app.logger.info(f"Data sheet created: id={sheet.id} FY{fy} entity={entity.name}")
        return jsonify({'success': True, 'data_sheet': sheet.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"create_sheet: {e}")
        return jsonify({'success': False, 'error': 'Failed to create data sheet'}), 500


# ── GET ──────────────────────────────────────────────────────────────────────

@data_sheet_bp.route('/<int:sheet_id>', methods=['GET'])
@auth_required
def get_sheet(sheet_id):
    try:
        sheet = SMSFDataSheet.query.get_or_404(sheet_id)
        return jsonify({'success': True, 'data_sheet': sheet.to_dict()})
    except Exception as e:
        current_app.logger.error(f"get_sheet: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch'}), 500


# ── UPDATE (full replace of all sections) ───────────────────────────────────

@data_sheet_bp.route('/<int:sheet_id>', methods=['PUT', 'PATCH'])
@auth_required
def update_sheet(sheet_id):
    try:
        sheet = SMSFDataSheet.query.get_or_404(sheet_id)
        data  = request.get_json() or {}

        for field in ('fund_name', 'date_of_creation', 'abn_of_smsf', 'tfn_of_smsf'):
            if field in data:
                setattr(sheet, field, str(data[field]))
        for field in ('members', 'trustees', 'subsequent_events', 'nominations'):
            if field in data and isinstance(data[field], list):
                setattr(sheet, field, data[field])
        if 'bare_trustee' in data and isinstance(data['bare_trustee'], dict):
            sheet.bare_trustee = data['bare_trustee']

        db.session.commit()
        return jsonify({'success': True, 'data_sheet': sheet.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"update_sheet: {e}")
        return jsonify({'success': False, 'error': 'Failed to update'}), 500


# ── DELETE ───────────────────────────────────────────────────────────────────

@data_sheet_bp.route('/<int:sheet_id>', methods=['DELETE'])
@auth_required
def delete_sheet(sheet_id):
    try:
        sheet = SMSFDataSheet.query.get_or_404(sheet_id)
        db.session.delete(sheet)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Data sheet deleted'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"delete_sheet: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete'}), 500


# ── PDF ───────────────────────────────────────────────────────────────────────

@data_sheet_bp.route('/<int:sheet_id>/pdf', methods=['GET'])
@auth_required
def get_pdf(sheet_id):
    try:
        sheet = SMSFDataSheet.query.get_or_404(sheet_id)
        from app.modules.smsf_data_sheet.services.pdf_generator import DataSheetPDFGenerator
        ctx   = DataSheetPDFGenerator.build_context(sheet)
        pdf   = DataSheetPDFGenerator.generate_pdf_bytes(ctx)
        fname = f"SMSF_DataSheet_{sheet.client_entity.name.replace(' ','_')}_FY{sheet.financial_year}.pdf"
        download = request.args.get('download', '0') == '1'
        return send_file(io.BytesIO(pdf), mimetype='application/pdf',
                         as_attachment=download, download_name=fname)
    except Exception as e:
        current_app.logger.error(f"get_pdf: {e}")
        return jsonify({'success': False, 'error': f'PDF generation failed: {e}'}), 500


@data_sheet_bp.route('/<int:sheet_id>/preview-html', methods=['GET'])
@auth_required
def preview_html(sheet_id):
    try:
        sheet = SMSFDataSheet.query.get_or_404(sheet_id)
        from app.modules.smsf_data_sheet.services.pdf_generator import DataSheetPDFGenerator
        ctx  = DataSheetPDFGenerator.build_context(sheet)
        html = DataSheetPDFGenerator.render_html(ctx)
        return Response(html, mimetype='text/html')
    except Exception as e:
        current_app.logger.error(f"preview_html: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
