"""
Client Portal API Routes
========================
Admin:  POST /api/client-portal/invite        — invite client linked to a fund
Client: GET  /api/client-portal/my-portal     — dashboard data (request + entity)
Client: POST /api/client-portal/start-audit   — create request + submit data sheet
Client: GET  /api/client-portal/my-pdf        — stream generated data sheet PDF
Client: POST /api/client-portal/upload-signed — upload physically signed doc
"""
import io
import os
import random
import string
from datetime import datetime
from functools import wraps

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db

client_portal_bp = Blueprint('client_portal', __name__, url_prefix='/api/client-portal')

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', 'uploads', 'client_portal'
)


# ── auth decorators ────────────────────────────────────────────────────────

def _get_current_user():
    from app.modules.user.models import User
    return User.query.get(get_jwt_identity())


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            u = _get_current_user()
            if not u:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            if u.role.name not in ('super_admin', 'admin'):
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return wrapper


def client_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            u = _get_current_user()
            if not u:
                return jsonify({'success': False, 'error': 'User not found'}), 401
            if u.role.name != 'user':
                return jsonify({'success': False, 'error': 'Client access only'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return wrapper


# ── helpers ────────────────────────────────────────────────────────────────

def _temp_password(length=12):
    chars = string.ascii_letters + string.digits + '!@#$'
    return ''.join(random.choices(chars, k=length))


def _find_smsf_audit_service():
    """Find the SMSF Annual Audit service by name."""
    from app.modules.services.models import Service
    svc = Service.query.filter(
        Service.name.ilike('%SMSF%Audit%')
    ).first()
    if not svc:
        svc = Service.query.filter(
            Service.name.ilike('%SMSF%')
        ).first()
    return svc


def _time_elapsed(dt):
    """Human-readable time since dt."""
    if not dt:
        return 'Unknown'
    delta = datetime.utcnow() - dt
    days = delta.days
    hours = delta.seconds // 3600
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        mins = delta.seconds // 60
        return f"{mins} minute{'s' if mins != 1 else ''} ago"


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — Invite Client
# ══════════════════════════════════════════════════════════════════════════════

@client_portal_bp.route('/invite', methods=['POST'])
@admin_required
def invite_client():
    """
    Admin invites a client user tied to a ClientEntity (SMSF fund).
    Creates the user account, sends an invite email with temp password.

    Body:
      client_entity_id   (required)
      email              (required)
      first_name         (required)
      last_name          (required)
    """
    try:
        data = request.get_json() or {}
        admin = _get_current_user()

        entity_id  = data.get('client_entity_id')
        email      = (data.get('email') or '').strip().lower()
        first_name = (data.get('first_name') or '').strip()
        last_name  = (data.get('last_name') or '').strip()

        if not entity_id:
            return jsonify({'success': False, 'error': 'client_entity_id is required'}), 400
        if not email:
            return jsonify({'success': False, 'error': 'email is required'}), 400
        if not first_name:
            return jsonify({'success': False, 'error': 'first_name is required'}), 400

        from app.modules.client_entity.models import ClientEntity
        from app.modules.user.models import User, Role

        entity = ClientEntity.query.get(entity_id)
        if not entity:
            return jsonify({'success': False, 'error': 'Client entity not found'}), 404

        # Check if user already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': False, 'error': 'A user with this email already exists'}), 409

        client_role = Role.query.filter_by(name='user').first()
        if not client_role:
            return jsonify({'success': False, 'error': 'Client role not configured'}), 500

        temp_pw = _temp_password()
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=client_role.id,
            company_id=admin.company_id,
            client_entity_id=entity_id,
            invited_by_id=admin.id,
            is_active=True,
            is_verified=True,
            is_first_login=True,
            two_fa_enabled=False,
        )
        new_user.set_password(temp_pw)
        db.session.add(new_user)
        db.session.commit()

        # Send invite email
        try:
            from app.modules.notifications.services.email_service import EmailService
            portal_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            body = f"""
            <html><body style="font-family:Arial,sans-serif;color:#333;line-height:1.6;">
            <div style="max-width:600px;margin:0 auto;padding:20px;">
              <h2 style="color:#1B72BE;">Welcome to AusSuperSource Client Portal</h2>
              <p>Dear {first_name},</p>
              <p>You have been invited to access the AusSuperSource Client Portal for:</p>
              <p style="background:#f0f7ff;padding:12px;border-left:4px solid #1B72BE;border-radius:4px;">
                <strong>{entity.name}</strong>
              </p>
              <p>Use the following credentials to log in:</p>
              <table style="border-collapse:collapse;margin:12px 0;">
                <tr><td style="padding:6px 12px;background:#f5f7fa;font-weight:bold;">Email</td>
                    <td style="padding:6px 12px;">{email}</td></tr>
                <tr><td style="padding:6px 12px;background:#f5f7fa;font-weight:bold;">Temporary Password</td>
                    <td style="padding:6px 12px;font-family:monospace;">{temp_pw}</td></tr>
              </table>
              <p>
                <a href="{portal_url}/login"
                   style="display:inline-block;background:#1B72BE;color:white;padding:10px 24px;
                          border-radius:6px;text-decoration:none;font-weight:bold;">
                  Login to Portal
                </a>
              </p>
              <p style="color:#888;font-size:12px;">
                You will be asked to change your password on first login.<br>
                If you have any questions, contact us at info@aussupersource.com.au
              </p>
            </div>
            </body></html>
            """
            EmailService.send_email(email, 'Your AusSuperSource Client Portal Invitation', body)
        except Exception as email_err:
            current_app.logger.warning(f"Invite email failed: {email_err}")

        current_app.logger.info(
            f"Client invited: {email} linked to entity '{entity.name}' by admin {admin.email}"
        )
        return jsonify({
            'success': True,
            'message': f'Invitation sent to {email}',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': f'{first_name} {last_name}',
                'client_entity_id': entity_id,
                'temp_password': temp_pw,   # shown once in response for admin to note
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"invite_client: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ── List clients invited for an entity ──────────────────────────────────────

@client_portal_bp.route('/clients', methods=['GET'])
@admin_required
def list_clients():
    """List all client portal users, optionally filtered by entity."""
    try:
        from app.modules.user.models import User, Role
        q = User.query.join(Role).filter(Role.name == 'user')
        entity_id = request.args.get('client_entity_id')
        if entity_id:
            q = q.filter(User.client_entity_id == entity_id)
        users = q.order_by(User.created_at.desc()).all()
        return jsonify({'success': True, 'clients': [
            {
                'id': u.id, 'email': u.email,
                'name': u.full_name,
                'client_entity_id': u.client_entity_id,
                'is_active': u.is_active,
                'is_first_login': u.is_first_login,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]})
    except Exception as e:
        current_app.logger.error(f"list_clients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT — Portal Dashboard
# ══════════════════════════════════════════════════════════════════════════════

@client_portal_bp.route('/my-portal', methods=['GET'])
@client_required
def my_portal():
    """
    Client dashboard data:
    - Their linked entity (fund details)
    - Their active service request (status, stage, assignee, time, query)
    - Their data sheet (if submitted)
    """
    try:
        client = _get_current_user()

        # Entity
        entity = None
        if client.client_entity_id:
            from app.modules.client_entity.models import ClientEntity
            entity = ClientEntity.query.get(client.client_entity_id)

        # Latest service request
        from app.modules.services.models import ServiceRequest
        req = ServiceRequest.query.filter_by(
            user_id=client.id
        ).order_by(ServiceRequest.created_at.desc()).first()

        # Data sheet
        data_sheet = None
        if entity:
            from app.modules.smsf_data_sheet.models import SMSFDataSheet
            data_sheet = SMSFDataSheet.query.filter_by(
                client_entity_id=entity.id
            ).order_by(SMSFDataSheet.created_at.desc()).first()

        # Build response
        req_data = None
        if req:
            # Get assigned accountant name
            assigned_name = None
            if req.assigned_accountant_id:
                from app.modules.user.models import User
                acc = User.query.get(req.assigned_accountant_id)
                assigned_name = acc.full_name if acc else None

            # Get current stage name
            stage_name = None
            if req.current_step_id:
                from app.modules.services.models import WorkflowStep
                step = WorkflowStep.query.get(req.current_step_id)
                stage_name = step.name if step else None

            req_data = {
                'id':              req.id,
                'request_number':  req.request_number,
                'status':          req.status,
                'stage':           stage_name,
                'assigned_to':     assigned_name,
                'time_elapsed':    _time_elapsed(req.created_at),
                'created_at':      req.created_at.isoformat() if req.created_at else None,
                'query_raised':    req.status == 'query_raised',
                'internal_notes':  req.internal_notes if req.status == 'query_raised' else None,
                'invoice_raised':  req.invoice_raised,
                'invoice_paid':    req.invoice_paid,
                'invoice_amount':  float(req.invoice_amount) if req.invoice_amount else None,
                'priority':        req.priority,
            }

        return jsonify({
            'success': True,
            'client': {
                'id':         client.id,
                'name':       client.full_name,
                'email':      client.email,
                'is_first_login': client.is_first_login,
            },
            'entity': {
                'id':      entity.id,
                'name':    entity.name,
                'abn':     entity.abn,
                'tfn':     entity.tfn,
                'address': entity.full_address,
            } if entity else None,
            'request':    req_data,
            'data_sheet': {
                'id':             data_sheet.id,
                'financial_year': data_sheet.financial_year,
                'has_pdf':        True,
            } if data_sheet else None,
        })

    except Exception as e:
        current_app.logger.error(f"my_portal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# CLIENT — Start SMSF Audit (create request + submit data sheet)
# ══════════════════════════════════════════════════════════════════════════════

@client_portal_bp.route('/start-audit', methods=['POST'])
@client_required
def start_audit():
    """
    Client fills SMSF Basic Data Sheet.
    This endpoint:
      1. Creates ServiceRequest for SMSF Annual Audit
      2. Saves SMSFDataSheet with the submitted data
      3. Generates PDF
      4. Emails PDF to client
    """
    try:
        client   = _get_current_user()
        data     = request.get_json() or {}

        if not client.client_entity_id:
            return jsonify({'success': False, 'error': 'No fund linked to your account. Contact admin.'}), 400

        from app.modules.client_entity.models import ClientEntity
        entity = ClientEntity.query.get(client.client_entity_id)
        if not entity:
            return jsonify({'success': False, 'error': 'Fund not found'}), 404

        fy = str(data.get('financial_year', '')).strip()
        if not fy:
            return jsonify({'success': False, 'error': 'financial_year is required'}), 400

        # ── 1. Create ServiceRequest ──────────────────────────────────────
        svc = _find_smsf_audit_service()
        if not svc:
            return jsonify({'success': False, 'error': 'SMSF Annual Audit service not configured. Contact admin.'}), 404

        from app.modules.services.models import ServiceRequest
        # Check for existing pending/active request
        existing_req = ServiceRequest.query.filter(
            ServiceRequest.user_id == client.id,
            ServiceRequest.status.notin_(['completed', 'cancelled'])
        ).first()
        if existing_req:
            return jsonify({
                'success': False,
                'error': 'You already have an active SMSF Audit request.',
                'request_id': existing_req.id
            }), 409

        # Generate request number
        last_req = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).first()
        if last_req and last_req.request_number:
            try:
                last_num = int(last_req.request_number.replace('REQ-', ''))
                new_num = f"REQ-{last_num + 1:06d}"
            except (ValueError, AttributeError):
                new_num = f"REQ-{ServiceRequest.query.count() + 1:06d}"
        else:
            new_num = "REQ-000001"

        new_request = ServiceRequest(
            user_id=client.id,
            service_id=svc.id,
            client_entity_id=entity.id,
            request_number=new_num,
            description=f"SMSF Annual Audit — {entity.name} — FY{fy}",
            status='pending',
            priority='normal',
        )
        db.session.add(new_request)
        db.session.flush()  # get ID

        # ── 2. Save SMSFDataSheet ─────────────────────────────────────────
        from app.modules.smsf_data_sheet.models import SMSFDataSheet
        # Remove old draft if any
        old_sheet = SMSFDataSheet.query.filter_by(
            client_entity_id=entity.id, financial_year=fy
        ).first()
        if old_sheet:
            db.session.delete(old_sheet)
            db.session.flush()

        sheet = SMSFDataSheet(
            client_entity_id  = entity.id,
            financial_year    = fy,
            fund_name         = data.get('fund_name', entity.name),
            date_of_creation  = data.get('date_of_creation', ''),
            abn_of_smsf       = data.get('abn_of_smsf', entity.abn or ''),
            tfn_of_smsf       = data.get('tfn_of_smsf', entity.tfn or ''),
            members           = data.get('members', []),
            trustees          = data.get('trustees', []),
            bare_trustee      = data.get('bare_trustee', {}),
            nominations       = data.get('nominations', []),
            subsequent_events = data.get('subsequent_events', []),
            created_by_id     = client.id,
        )
        db.session.add(sheet)
        db.session.commit()

        # ── 3. Generate PDF ───────────────────────────────────────────────
        pdf_bytes = None
        try:
            from app.modules.smsf_data_sheet.services.pdf_generator import DataSheetPDFGenerator
            ctx       = DataSheetPDFGenerator.build_context(sheet)
            pdf_bytes = DataSheetPDFGenerator.generate_pdf_bytes(ctx)
        except Exception as pdf_err:
            current_app.logger.error(f"PDF generation failed: {pdf_err}")

        # ── 4. Email PDF to client ────────────────────────────────────────
        if pdf_bytes:
            try:
                from app.modules.notifications.services.email_service import EmailService
                subject = f"Your SMSF Basic Data Sheet — {entity.name} FY{fy}"
                body = f"""
                <html><body style="font-family:Arial,sans-serif;color:#333;line-height:1.6;">
                <div style="max-width:600px;margin:0 auto;padding:20px;">
                  <h2 style="color:#1B72BE;">SMSF Basic Data Sheet — FY{fy}</h2>
                  <p>Dear {client.full_name},</p>
                  <p>Thank you for submitting your SMSF Basic Data Sheet for
                     <strong>{entity.name}</strong> for the financial year ending 30/06/{fy}.</p>
                  <p>Please find your completed data sheet attached as a PDF.</p>
                  <p>Your audit request has been lodged (Reference: <strong>{new_request.request_number}</strong>).
                     Our team will be in touch shortly.</p>
                  <p style="color:#888;font-size:12px;">
                    Questions? Contact us at info@aussupersource.com.au
                  </p>
                </div>
                </body></html>
                """
                EmailService.send_email_with_attachment(
                    to_email=client.email,
                    subject=subject,
                    body=body,
                    attachment_bytes=pdf_bytes,
                    attachment_filename=f"SMSF_DataSheet_{entity.name.replace(' ','_')}_FY{fy}.pdf",
                    attachment_mime='application/pdf',
                )
            except Exception as mail_err:
                current_app.logger.warning(f"Email PDF failed: {mail_err}")

        current_app.logger.info(
            f"Client {client.email} started audit request {new_request.request_number} for {entity.name} FY{fy}"
        )
        return jsonify({
            'success': True,
            'message': 'Your SMSF Audit request has been submitted. A copy of your data sheet has been emailed to you.',
            'request_number': new_request.request_number,
            'data_sheet_id': sheet.id,
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"start_audit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ── GET PDF ──────────────────────────────────────────────────────────────────

@client_portal_bp.route('/my-pdf', methods=['GET'])
@client_required
def my_pdf():
    """Stream the client's latest SMSF data sheet PDF."""
    try:
        client = _get_current_user()
        if not client.client_entity_id:
            return jsonify({'success': False, 'error': 'No fund linked'}), 400

        from app.modules.smsf_data_sheet.models import SMSFDataSheet
        from app.modules.client_entity.models import ClientEntity
        entity = ClientEntity.query.get(client.client_entity_id)
        sheet  = SMSFDataSheet.query.filter_by(
            client_entity_id=client.client_entity_id
        ).order_by(SMSFDataSheet.created_at.desc()).first()

        if not sheet:
            return jsonify({'success': False, 'error': 'No data sheet found'}), 404

        from app.modules.smsf_data_sheet.services.pdf_generator import DataSheetPDFGenerator
        ctx   = DataSheetPDFGenerator.build_context(sheet)
        pdf   = DataSheetPDFGenerator.generate_pdf_bytes(ctx)
        fname = f"SMSF_DataSheet_{entity.name.replace(' ','_')}_FY{sheet.financial_year}.pdf"
        download = request.args.get('download', '0') == '1'
        return send_file(io.BytesIO(pdf), mimetype='application/pdf',
                         as_attachment=download, download_name=fname)
    except Exception as e:
        current_app.logger.error(f"my_pdf: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ── UPLOAD SIGNED DOCUMENT ───────────────────────────────────────────────────

@client_portal_bp.route('/upload-signed', methods=['POST'])
@client_required
def upload_signed():
    """Client uploads a signed document (engagement letter or data sheet)."""
    try:
        client = _get_current_user()
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        safe_name = f"signed_{client.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, safe_name)
        file.save(path)

        current_app.logger.info(f"Client {client.email} uploaded signed doc: {safe_name}")
        return jsonify({'success': True, 'message': 'Document uploaded successfully', 'filename': safe_name})
    except Exception as e:
        current_app.logger.error(f"upload_signed: {e}")
        return jsonify({'success': False, 'error': 'Upload failed'}), 500
