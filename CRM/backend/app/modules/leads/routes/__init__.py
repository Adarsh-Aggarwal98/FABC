"""Leads API Routes"""
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db
from ..models.lead import Lead

leads_bp = Blueprint('leads', __name__, url_prefix='/api/leads')


# ============== VALIDATION HELPERS ==============

def validate_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def sanitize_string(value, max_length=200):
    if not value:
        return None
    sanitized = str(value).strip()[:max_length]
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    return sanitized


# ============== ADMIN AUTH DECORATOR ==============

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
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Auth error: {str(e)}")
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return wrapper


# ============== RATE LIMITING ==============

_rate_limit_store = {}

def check_rate_limit(ip_address, limit=5, window=60):
    now = datetime.utcnow()
    key = f"lead_submission_{ip_address}"
    if key in _rate_limit_store:
        requests_count, window_start = _rate_limit_store[key]
        if (now - window_start).total_seconds() > window:
            _rate_limit_store[key] = (1, now)
            return True
        if requests_count >= limit:
            return False
        _rate_limit_store[key] = (requests_count + 1, window_start)
    else:
        _rate_limit_store[key] = (1, now)
    return True


# ============== PUBLIC ROUTE ==============

@leads_bp.route('', methods=['POST'])
def create_lead():
    """Save a new lead from website form submission"""
    try:
        # Rate limiting
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if isinstance(ip_address, str) and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()

        if not check_rate_limit(ip_address):
            return jsonify({
                'success': False,
                'error': 'Too many submissions. Please wait a minute before trying again.'
            }), 429

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Validate required fields
        errors = []

        first_name = sanitize_string(data.get('first_name'), 100)
        if not first_name or len(first_name) < 1:
            errors.append('First name is required')

        last_name = sanitize_string(data.get('last_name'), 100)
        if not last_name or len(last_name) < 1:
            errors.append('Last name is required')

        email = sanitize_string(data.get('email'), 200)
        if not validate_email(email):
            errors.append('Valid email address is required')

        phone = sanitize_string(data.get('phone'), 50)
        message = sanitize_string(data.get('message'), 2000)

        form_type = data.get('form_type', 'contact')
        if form_type not in ('contact', 'appointment'):
            form_type = 'contact'

        # Appointment-specific fields
        appointment_date = sanitize_string(data.get('appointment_date'), 50)
        appointment_time = sanitize_string(data.get('appointment_time'), 50)
        service = sanitize_string(data.get('service'), 200)
        hear_about_us = sanitize_string(data.get('hear_about_us'), 200)

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Create lead
        lead = Lead(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            phone=phone,
            message=message,
            form_type=form_type,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service=service,
            hear_about_us=hear_about_us,
            status='new',
            ip_address=ip_address[:50] if ip_address else None,
            user_agent=sanitize_string(request.headers.get('User-Agent', ''), 500),
        )

        db.session.add(lead)
        db.session.commit()

        current_app.logger.info(f"New lead from {email} - type: {form_type}")

        # Send email notification
        try:
            from app.modules.notifications.services.email_service import EmailService

            type_label = 'Appointment Request' if form_type == 'appointment' else 'Contact Form'
            service_line = f"<p><strong>Service:</strong> {service}</p>" if service else ""
            appt_line = ""
            if appointment_date:
                appt_line = f"<p><strong>Preferred Date:</strong> {appointment_date}</p>"
            if appointment_time:
                appt_line += f"<p><strong>Preferred Time:</strong> {appointment_time}</p>"

            body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2D8C3C;">New {type_label} Submission</h2>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Name:</strong> {first_name} {last_name}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Phone:</strong> {phone or 'Not provided'}</p>
                            {service_line}
                            {appt_line}
                            <p><strong>Message:</strong> {message or 'No message'}</p>
                        </div>
                        <p style="color: #6b7280; font-size: 12px;">This lead has been saved to the CRM. <a href="https://crm.aussupersource.com.au/leads">View in CRM</a></p>
                    </div>
                </body>
                </html>
            """

            EmailService.send_email(
                'info@aussupersource.com.au',
                f'New {type_label}: {first_name} {last_name}',
                body
            )
        except Exception as email_err:
            current_app.logger.error(f"Failed to send lead notification email: {str(email_err)}")

        return jsonify({
            'success': True,
            'message': 'Thank you! Your submission has been received. We will get back to you shortly.'
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating lead: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to save submission. Please try again.'}), 500


# ============== ADMIN ROUTES ==============

@leads_bp.route('/admin/leads', methods=['GET'])
@admin_required
def admin_get_leads():
    """Get all leads with optional filtering"""
    try:
        query = Lead.query

        # Filter by status
        status = request.args.get('status')
        if status and status in ('new', 'contacted', 'converted', 'closed'):
            query = query.filter_by(status=status)

        # Filter by form_type
        form_type = request.args.get('form_type')
        if form_type and form_type in ('contact', 'appointment'):
            query = query.filter_by(form_type=form_type)

        # Search
        search = request.args.get('search', '').strip()
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Lead.first_name.ilike(search_term),
                    Lead.last_name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.phone.ilike(search_term),
                )
            )

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)

        total = query.count()
        leads = query.order_by(Lead.submitted_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'success': True,
            'leads': [l.to_dict() for l in leads],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching leads: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch leads'}), 500


@leads_bp.route('/admin/leads/<int:lead_id>', methods=['GET'])
@admin_required
def admin_get_lead(lead_id):
    """Get a single lead"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        return jsonify({'success': True, 'lead': lead.to_dict()})
    except Exception as e:
        current_app.logger.error(f"Error fetching lead: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch lead'}), 500


@leads_bp.route('/admin/leads/<int:lead_id>', methods=['PATCH'])
@admin_required
def admin_update_lead(lead_id):
    """Update lead status/notes"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        data = request.get_json()

        if 'status' in data:
            if data['status'] in ('new', 'contacted', 'converted', 'closed'):
                lead.status = data['status']

        if 'notes' in data:
            lead.notes = sanitize_string(data['notes'], 5000)

        db.session.commit()
        current_app.logger.info(f"Admin updated lead {lead_id}")

        return jsonify({'success': True, 'lead': lead.to_dict()})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lead: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update lead'}), 500


@leads_bp.route('/admin/leads/<int:lead_id>', methods=['DELETE'])
@admin_required
def admin_delete_lead(lead_id):
    """Delete a lead"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        db.session.delete(lead)
        db.session.commit()
        current_app.logger.info(f"Admin deleted lead {lead_id}")
        return jsonify({'success': True, 'message': 'Lead deleted'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting lead: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete lead'}), 500


@leads_bp.route('/admin/leads/export', methods=['GET'])
@admin_required
def admin_export_leads():
    """Export all leads"""
    try:
        leads = Lead.query.order_by(Lead.submitted_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(leads),
            'leads': [l.to_export_dict() for l in leads]
        })
    except Exception as e:
        current_app.logger.error(f"Error exporting leads: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to export leads'}), 500


@leads_bp.route('/admin/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    """Get lead statistics"""
    try:
        total = Lead.query.count()
        new_count = Lead.query.filter_by(status='new').count()

        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week = Lead.query.filter(Lead.submitted_at >= week_ago).count()

        contact_count = Lead.query.filter_by(form_type='contact').count()
        appointment_count = Lead.query.filter_by(form_type='appointment').count()

        by_status = {
            'new': new_count,
            'contacted': Lead.query.filter_by(status='contacted').count(),
            'converted': Lead.query.filter_by(status='converted').count(),
            'closed': Lead.query.filter_by(status='closed').count(),
        }

        return jsonify({
            'total': total,
            'new': new_count,
            'thisWeek': this_week,
            'contactCount': contact_count,
            'appointmentCount': appointment_count,
            'byStatus': by_status,
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching lead stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch stats'}), 500
