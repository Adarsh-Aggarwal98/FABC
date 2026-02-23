"""
ATO Alerts API Routes
=====================
Public:  GET  /api/ato-alerts              — active alerts (no auth required)
Admin:   GET  /api/admin/ato-alerts        — all alerts
Admin:   POST /api/admin/ato-alerts        — create alert
Admin:   PUT  /api/admin/ato-alerts/:id    — update alert
Admin:   DELETE /api/admin/ato-alerts/:id  — delete alert
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.extensions import db

ato_alerts_bp = Blueprint('ato_alerts', __name__)


def _admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            from app.modules.user.models import User
            user = User.query.get(get_jwt_identity())
            if not user or user.role.name not in ('super_admin', 'admin'):
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
        except Exception:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return fn(*args, **kwargs)
    return wrapper


# ── Public ────────────────────────────────────────────────────────────────────

@ato_alerts_bp.route('/api/ato-alerts', methods=['GET'])
def list_ato_alerts():
    """Return active, non-expired ATO alerts sorted by priority."""
    from app.modules.ato_alerts.models import AtoAlert
    now = datetime.utcnow()
    alerts = (
        AtoAlert.query
        .filter_by(active=True)
        .filter((AtoAlert.expires_at == None) | (AtoAlert.expires_at > now))
        .order_by(AtoAlert.priority)
        .all()
    )
    return jsonify({'success': True, 'alerts': [a.to_dict() for a in alerts]})


# ── Admin ─────────────────────────────────────────────────────────────────────

@ato_alerts_bp.route('/api/admin/ato-alerts', methods=['GET'])
@_admin_required
def admin_list_alerts():
    from app.modules.ato_alerts.models import AtoAlert
    alerts = AtoAlert.query.order_by(AtoAlert.priority).all()
    return jsonify({'success': True, 'alerts': [a.to_dict() for a in alerts]})


@ato_alerts_bp.route('/api/admin/ato-alerts', methods=['POST'])
@_admin_required
def create_alert():
    from app.modules.ato_alerts.models import AtoAlert
    data = request.get_json() or {}
    if not all([data.get('title'), data.get('type'), data.get('link')]):
        return jsonify({'success': False, 'error': 'title, type, and link are required'}), 400
    if data['type'] not in ('update', 'alert', 'reminder'):
        return jsonify({'success': False, 'error': 'type must be update, alert, or reminder'}), 400

    expires_at = None
    if data.get('expiresAt'):
        try:
            expires_at = datetime.fromisoformat(data['expiresAt'].replace('Z', '+00:00'))
        except ValueError:
            pass

    alert = AtoAlert(
        title=data['title'],
        type=data['type'],
        link=data['link'],
        active=data.get('active', True),
        priority=data.get('priority', 0),
        expires_at=expires_at,
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'success': True, 'alert': alert.to_dict()}), 201


@ato_alerts_bp.route('/api/admin/ato-alerts/<alert_id>', methods=['PUT', 'PATCH'])
@_admin_required
def update_alert(alert_id):
    from app.modules.ato_alerts.models import AtoAlert
    alert = AtoAlert.query.get(alert_id)
    if not alert:
        return jsonify({'success': False, 'error': 'Alert not found'}), 404
    data = request.get_json() or {}
    for field in ['title', 'type', 'link']:
        if field in data:
            setattr(alert, field, data[field])
    if 'active' in data:
        alert.active = data['active']
    if 'priority' in data:
        alert.priority = data['priority']
    if 'expiresAt' in data:
        try:
            alert.expires_at = datetime.fromisoformat(data['expiresAt'].replace('Z', '+00:00')) if data['expiresAt'] else None
        except ValueError:
            pass
    db.session.commit()
    return jsonify({'success': True, 'alert': alert.to_dict()})


@ato_alerts_bp.route('/api/admin/ato-alerts/<alert_id>', methods=['DELETE'])
@_admin_required
def delete_alert(alert_id):
    from app.modules.ato_alerts.models import AtoAlert
    alert = AtoAlert.query.get(alert_id)
    if not alert:
        return jsonify({'success': False, 'error': 'Alert not found'}), 404
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Alert deleted'})
