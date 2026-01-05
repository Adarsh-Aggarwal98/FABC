"""
SMSF Website - Flask Backend
Complete API including Auth, Documents, Admin, Blogs, ATO Alerts
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from functools import wraps
import os
import secrets
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

from models import db, User, TwoFactorCode, Invitation, Document, Blog, AtoAlert, AuditLog
from zoho_service import zoho_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
# Check if static folder exists (for production deployment with frontend)
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if os.path.exists(static_folder):
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
else:
    app = Flask(__name__)

# App configuration
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev-secret-change-in-production')

# Database: Use DATABASE_URL env var for PostgreSQL, defaults to SQLite
db_url = os.getenv('DATABASE_URL')
if not db_url:
    # Use SQLite - determine path based on environment
    if os.path.exists('/app'):
        # Docker environment - use /app/data for persistence
        db_dir = '/app/data'
        os.makedirs(db_dir, exist_ok=True)
        db_url = f'sqlite:///{db_dir}/smsf.db'
    else:
        # Local development
        db_url = 'sqlite:///smsf.db'
    logger.info(f"Using SQLite database: {db_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration - use filesystem for simplicity with SQLite
session_dir = '/app/data/sessions' if os.path.exists('/app') else os.path.join(os.path.dirname(__file__), 'sessions')
os.makedirs(session_dir, exist_ok=True)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = session_dir
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('NODE_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.zoho.com.au')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL', 'admin@aussupersource.com.au')

# Initialize extensions
db.init_app(app)
Session(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('FRONTEND_URL', 'http://localhost:5173').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ============================================
# DECORATORS
# ============================================
def require_role(*roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_approved(f):
    """Decorator to require approved user status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if current_user.status != 'approved':
            return jsonify({'error': 'Account not approved'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# DATABASE INITIALIZATION
# ============================================
def init_database():
    """Initialize database and create default data"""
    with app.app_context():
        db.create_all()

        # Create default admin if none exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            logger.info("Creating default test users...")
            password_hash = bcrypt.generate_password_hash('Test@123').decode('utf-8')

            # Admin
            admin = User(
                email='admin@aussupersource.com.au',
                password_hash=password_hash,
                first_name='Admin',
                last_name='User',
                role='admin',
                status='approved',
                approved_at=datetime.utcnow()
            )
            db.session.add(admin)

            # Accountant
            accountant = User(
                email='accountant@aussupersource.com.au',
                password_hash=password_hash,
                first_name='Test',
                last_name='Accountant',
                role='accountant',
                status='approved',
                approved_at=datetime.utcnow()
            )
            db.session.add(accountant)

            # Regular User
            user = User(
                email='user@aussupersource.com.au',
                password_hash=password_hash,
                first_name='Test',
                last_name='User',
                phone='0400000000',
                role='user',
                status='approved',
                approved_at=datetime.utcnow()
            )
            db.session.add(user)

            db.session.commit()

            print("\n" + "="*60)
            print("  TEST CREDENTIALS CREATED")
            print("="*60)
            print("\n  ADMIN:")
            print("    Email:    admin@aussupersource.com.au")
            print("    Password: Test@123")
            print("\n  ACCOUNTANT:")
            print("    Email:    accountant@aussupersource.com.au")
            print("    Password: Test@123")
            print("\n  USER:")
            print("    Email:    user@aussupersource.com.au")
            print("    Password: Test@123")
            print("\n" + "="*60 + "\n")

        # Seed blogs if empty
        if Blog.query.count() == 0:
            logger.info("Seeding initial blogs...")
            blogs = [
                Blog(
                    title="2024 SMSF Compliance Changes: What Accountants Need to Know",
                    slug="2024-smsf-compliance-changes",
                    excerpt="Stay ahead of the latest regulatory updates affecting SMSF audits.",
                    category="Compliance",
                    author="Yateender Gupta",
                    read_time="5 min read",
                    image="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=600&h=400&fit=crop",
                    featured=True
                ),
                Blog(
                    title="White-Label Auditing: How to Scale Your SMSF Practice",
                    slug="white-label-auditing-scale-practice",
                    excerpt="Discover how partnering with a white-label audit provider can help you.",
                    category="Practice Growth",
                    author="Sharat Sharma",
                    read_time="4 min read",
                    image="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop",
                ),
            ]
            for blog in blogs:
                db.session.add(blog)
            db.session.commit()

        # Seed ATO alerts if empty
        if AtoAlert.query.count() == 0:
            logger.info("Seeding initial ATO alerts...")
            alerts = [
                AtoAlert(
                    title="SMSF annual return deadline extended to 28 February 2025",
                    type="update",
                    link="https://www.ato.gov.au/super/self-managed-super-funds/",
                    priority=1
                ),
                AtoAlert(
                    title="New contribution caps for 2024-25: Concessional $30,000",
                    type="alert",
                    link="https://www.ato.gov.au/super/self-managed-super-funds/contributions-and-rollovers/",
                    priority=2
                ),
            ]
            for alert in alerts:
                db.session.add(alert)
            db.session.commit()


# ============================================
# HELPER FUNCTIONS
# ============================================
def generate_2fa_code():
    """Generate 6-digit 2FA code"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def send_2fa_email(email, code, user_name):
    """Send 2FA verification email"""
    # ==========================================
    # DEV MODE: Log OTP to console for testing
    # ==========================================
    logger.info(f"")
    logger.info(f"========================================")
    logger.info(f"  OTP CODE FOR {email}: {code}")
    logger.info(f"========================================")
    logger.info(f"")

    # Try to send email, but don't fail if it doesn't work
    try:
        msg = Message(
            subject="Your Australian Super Source Login Code",
            recipients=[email]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; text-align: center;">
                <h1>Australian Super Source</h1>
            </div>
            <div style="padding: 30px; background: white; text-align: center;">
                <h2>Your Verification Code</h2>
                <p>Hi {user_name},</p>
                <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 20px; background: #f0f9ff; border-radius: 8px; color: #1e40af; margin: 20px 0;">
                    {code}
                </div>
                <p style="color: #6b7280;">This code expires in 5 minutes.</p>
            </div>
        </div>
        """
        mail.send(msg)
        logger.info(f"2FA email sent to {email}")
    except Exception as e:
        logger.warning(f"Email not sent (dev mode OK): {e}")

    # Always return True so login continues
    return True


def log_action(user_id, action, details=None):
    """Log user action for audit trail"""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log action: {e}")


# ============================================
# HEALTH CHECK
# ============================================
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


# ============================================
# AUTH ROUTES
# ============================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Self-registration (pending approval)"""
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    phone = data.get('phone', '').strip()

    if not all([email, password, first_name, last_name]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role='user',
        status='pending'
    )

    db.session.add(user)
    db.session.commit()

    log_action(user.id, 'register', {'email': email})

    return jsonify({'message': 'Registration successful. Awaiting admin approval.'}), 201


@app.route('/api/auth/register/<token>', methods=['POST'])
def register_with_invitation(token):
    """Register via invitation link"""
    invitation = Invitation.query.filter_by(token=token, used_at=None).first()

    if not invitation:
        return jsonify({'error': 'Invalid or expired invitation'}), 400

    if invitation.expires_at < datetime.utcnow():
        return jsonify({'error': 'Invitation has expired'}), 400

    data = request.get_json()
    password = data.get('password', '')
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    phone = data.get('phone', '').strip()

    if not all([password, first_name, last_name]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(email=invitation.email).first():
        return jsonify({'error': 'Email already registered'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(
        email=invitation.email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=invitation.role,
        status='approved',
        invited_by=invitation.invited_by,
        approved_at=datetime.utcnow()
    )

    invitation.used_at = datetime.utcnow()

    db.session.add(user)
    db.session.commit()

    log_action(user.id, 'register_via_invitation', {'email': invitation.email})

    return jsonify({'message': 'Registration successful. You can now log in.'}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Step 1: Validate credentials and send 2FA code (or bypass for test accounts)"""
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.status != 'approved':
        status_messages = {
            'pending': 'Your account is pending approval',
            'rejected': 'Your account has been rejected',
            'suspended': 'Your account has been suspended'
        }
        return jsonify({'error': status_messages.get(user.status, 'Account not accessible')}), 403

    # ==========================================
    # DEV MODE: Skip 2FA for test accounts
    # ==========================================
    test_emails = [
        'admin@aussupersource.com.au',
        'accountant@aussupersource.com.au',
        'user@aussupersource.com.au'
    ]

    if email in test_emails:
        # Direct login - skip 2FA
        login_user(user)
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        log_action(user.id, 'login_no_2fa', {'email': email})
        logger.info(f"Test account login (2FA skipped): {email}")
        return jsonify({
            'message': 'Login successful',
            'requires2FA': False,
            'user': user.to_dict()
        }), 200

    # Generate and save 2FA code for regular users
    code = generate_2fa_code()
    two_factor = TwoFactorCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.session.add(two_factor)
    db.session.commit()

    # Send 2FA email
    if send_2fa_email(user.email, code, user.first_name):
        session['pending_user_id'] = user.id
        return jsonify({
            'message': '2FA code sent to your email',
            'requires2FA': True
        }), 200
    else:
        return jsonify({'error': 'Failed to send verification code'}), 500


@app.route('/api/auth/verify-2fa', methods=['POST'])
def verify_2fa():
    """Step 2: Verify 2FA code and complete login"""
    data = request.get_json()
    code = data.get('code', '')

    pending_user_id = session.get('pending_user_id')
    if not pending_user_id:
        return jsonify({'error': 'No pending login session'}), 400

    user = User.query.get(pending_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Find valid 2FA code
    two_factor = TwoFactorCode.query.filter_by(
        user_id=user.id,
        code=code,
        used=False
    ).filter(TwoFactorCode.expires_at > datetime.utcnow()).first()

    if not two_factor:
        return jsonify({'error': 'Invalid or expired code'}), 401

    # Mark code as used
    two_factor.used = True
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Complete login
    login_user(user)
    session.pop('pending_user_id', None)

    log_action(user.id, 'login', {'method': '2fa'})

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@app.route('/api/auth/resend-2fa', methods=['POST'])
def resend_2fa():
    """Resend 2FA code"""
    pending_user_id = session.get('pending_user_id')
    if not pending_user_id:
        return jsonify({'error': 'No pending login session'}), 400

    user = User.query.get(pending_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Generate new code
    code = generate_2fa_code()
    two_factor = TwoFactorCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.session.add(two_factor)
    db.session.commit()

    if send_2fa_email(user.email, code, user.first_name):
        return jsonify({'message': '2FA code resent'}), 200
    else:
        return jsonify({'error': 'Failed to send verification code'}), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    log_action(current_user.id, 'logout')
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me')
def get_current_user():
    """Get current authenticated user"""
    if current_user.is_authenticated:
        return jsonify({'user': current_user.to_dict()}), 200
    return jsonify({'user': None}), 200


# ============================================
# ADMIN ROUTES
# ============================================
@app.route('/api/admin/users')
@login_required
@require_role('admin')
def get_all_users():
    """Get all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route('/api/admin/users/pending')
@login_required
@require_role('admin')
def get_pending_users():
    """Get pending users"""
    users = User.query.filter_by(status='pending').order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route('/api/admin/users/<user_id>/approve', methods=['POST'])
@login_required
@require_role('admin')
def approve_user(user_id):
    """Approve a pending user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.status != 'pending':
        return jsonify({'error': 'User is not pending approval'}), 400

    # Create Zoho folder
    zoho_folder_id = None
    if zoho_service.is_configured():
        try:
            zoho_folder_id = zoho_service.create_user_folder(user.id, user.email)
        except Exception as e:
            logger.error(f"Failed to create Zoho folder: {e}")

    user.status = 'approved'
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    user.zoho_folder_id = zoho_folder_id
    db.session.commit()

    log_action(current_user.id, 'approve_user', {'approved_user_id': user_id})

    return jsonify({'message': 'User approved', 'user': user.to_dict()}), 200


@app.route('/api/admin/users/<user_id>/reject', methods=['POST'])
@login_required
@require_role('admin')
def reject_user(user_id):
    """Reject a pending user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.status = 'rejected'
    db.session.commit()

    log_action(current_user.id, 'reject_user', {'rejected_user_id': user_id})

    return jsonify({'message': 'User rejected'}), 200


@app.route('/api/admin/users/<user_id>/suspend', methods=['POST'])
@login_required
@require_role('admin')
def suspend_user(user_id):
    """Suspend a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.status = 'suspended'
    db.session.commit()

    log_action(current_user.id, 'suspend_user', {'suspended_user_id': user_id})

    return jsonify({'message': 'User suspended'}), 200


@app.route('/api/admin/users/<user_id>/reactivate', methods=['POST'])
@login_required
@require_role('admin')
def reactivate_user(user_id):
    """Reactivate a suspended user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.status = 'approved'
    db.session.commit()

    log_action(current_user.id, 'reactivate_user', {'reactivated_user_id': user_id})

    return jsonify({'message': 'User reactivated'}), 200


@app.route('/api/admin/invite', methods=['POST'])
@login_required
@require_role('admin')
def invite_user():
    """Send invitation to new user"""
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    role = data.get('role', 'user')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    if role not in ['user', 'accountant']:
        return jsonify({'error': 'Invalid role'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Generate invitation token
    token = secrets.token_urlsafe(32)

    invitation = Invitation(
        email=email,
        role=role,
        token=token,
        invited_by=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.session.add(invitation)
    db.session.commit()

    # Send invitation email
    try:
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        register_link = f"{frontend_url}/register/{token}"

        msg = Message(
            subject="You're Invited to Australian Super Source",
            recipients=[email]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; text-align: center;">
                <h1>Australian Super Source</h1>
            </div>
            <div style="padding: 30px; background: white; text-align: center;">
                <h2>You're Invited!</h2>
                <p>You've been invited to join as a <strong>{'User' if role == 'user' else 'Accountant'}</strong>.</p>
                <a href="{register_link}" style="display: inline-block; background: #1e40af; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0;">
                    Create Your Account
                </a>
                <p style="color: #6b7280; font-size: 14px;">This invitation expires in 7 days.</p>
            </div>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        logger.error(f"Failed to send invitation email: {e}")

    log_action(current_user.id, 'send_invitation', {'email': email, 'role': role})

    return jsonify({'message': 'Invitation sent'}), 201


@app.route('/api/admin/invitations')
@login_required
@require_role('admin')
def get_invitations():
    """Get all pending invitations"""
    invitations = Invitation.query.filter_by(used_at=None).filter(
        Invitation.expires_at > datetime.utcnow()
    ).order_by(Invitation.created_at.desc()).all()

    return jsonify([inv.to_dict() for inv in invitations]), 200


@app.route('/api/admin/invitations/<invitation_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def cancel_invitation(invitation_id):
    """Cancel an invitation"""
    invitation = Invitation.query.get(invitation_id)
    if not invitation:
        return jsonify({'error': 'Invitation not found'}), 404

    db.session.delete(invitation)
    db.session.commit()

    return jsonify({'message': 'Invitation cancelled'}), 200


# ============================================
# DOCUMENT ROUTES
# ============================================
@app.route('/api/documents')
@login_required
@require_approved
def get_documents():
    """Get current user's documents"""
    docs = Document.query.filter_by(user_id=current_user.id).order_by(Document.uploaded_at.desc()).all()
    return jsonify([d.to_dict() for d in docs]), 200


@app.route('/api/documents/user/<user_id>')
@login_required
@require_role('accountant', 'admin')
def get_user_documents(user_id):
    """Get documents for a specific user (accountant/admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    docs = Document.query.filter_by(user_id=user_id).order_by(Document.uploaded_at.desc()).all()

    return jsonify({
        'user': {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email
        },
        'documents': [d.to_dict() for d in docs]
    }), 200


@app.route('/api/documents/all-users')
@login_required
@require_role('accountant', 'admin')
def get_all_users_documents():
    """Get all users with document counts"""
    users = User.query.filter_by(status='approved').order_by(User.first_name).all()

    result = []
    for user in users:
        doc_count = Document.query.filter_by(user_id=user.id).count()
        result.append({
            **user.to_dict(),
            'documentCount': doc_count
        })

    return jsonify(result), 200


@app.route('/api/documents/upload', methods=['POST'])
@login_required
@require_approved
def upload_document():
    """Upload a document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    description = request.form.get('description', '')
    target_user_id = request.form.get('targetUserId', current_user.id)

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Determine target user
    target_user = current_user
    if target_user_id != current_user.id:
        if current_user.role not in ['accountant', 'admin']:
            return jsonify({'error': 'You can only upload to your own folder'}), 403
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({'error': 'Target user not found'}), 404

    # Create Zoho folder if needed
    if not target_user.zoho_folder_id and zoho_service.is_configured():
        try:
            folder_id = zoho_service.create_user_folder(target_user.id, target_user.email)
            target_user.zoho_folder_id = folder_id
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to create Zoho folder: {e}")
            return jsonify({'error': 'Document storage not available'}), 500

    # Upload to Zoho
    if not zoho_service.is_configured():
        return jsonify({'error': 'Document storage not configured'}), 500

    try:
        result = zoho_service.upload_file(
            target_user.zoho_folder_id,
            file.read(),
            file.filename,
            file.mimetype
        )
    except Exception as e:
        logger.error(f"Zoho upload failed: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500

    # Save document record
    doc = Document(
        user_id=target_user.id,
        file_name=file.filename,
        file_type=file.mimetype,
        file_size=file.content_length or 0,
        zoho_file_id=result['file_id'],
        zoho_download_url=result['download_url'],
        description=description
    )

    db.session.add(doc)
    db.session.commit()

    log_action(current_user.id, 'document_upload', {
        'document_id': doc.id,
        'file_name': doc.file_name,
        'target_user_id': target_user.id
    })

    return jsonify({'message': 'Document uploaded', 'document': doc.to_dict()}), 201


@app.route('/api/documents/<doc_id>/download')
@login_required
@require_approved
def download_document(doc_id):
    """Get document download URL"""
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    # Check access
    has_access = (
        doc.user_id == current_user.id or
        current_user.role in ['accountant', 'admin']
    )

    if not has_access:
        return jsonify({'error': 'Access denied'}), 403

    try:
        download_url = zoho_service.get_download_url(doc.zoho_file_id)
    except:
        download_url = doc.zoho_download_url

    log_action(current_user.id, 'document_download', {
        'document_id': doc_id,
        'file_name': doc.file_name
    })

    return jsonify({
        'downloadUrl': download_url,
        'fileName': doc.file_name,
        'fileType': doc.file_type
    }), 200


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@login_required
@require_approved
def delete_document(doc_id):
    """Delete a document"""
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    # Check access - owner, accountant, or admin can delete
    can_delete = (
        doc.user_id == current_user.id or
        current_user.role in ['accountant', 'admin']
    )

    if not can_delete:
        return jsonify({'error': 'Access denied'}), 403

    # Delete from Zoho
    try:
        zoho_service.delete_file(doc.zoho_file_id)
    except Exception as e:
        logger.error(f"Failed to delete from Zoho: {e}")

    db.session.delete(doc)
    db.session.commit()

    log_action(current_user.id, 'document_delete', {
        'document_id': doc_id,
        'file_name': doc.file_name
    })

    return jsonify({'message': 'Document deleted'}), 200


# ============================================
# BLOG ROUTES
# ============================================
@app.route('/api/blogs')
def get_blogs():
    """Get published blogs"""
    blogs = Blog.query.filter_by(published=True).order_by(Blog.created_at.desc()).all()
    return jsonify([b.to_dict() for b in blogs]), 200


@app.route('/api/blogs/slug/<slug>')
def get_blog_by_slug(slug):
    """Get single blog by slug"""
    blog = Blog.query.filter_by(slug=slug, published=True).first()
    if not blog:
        return jsonify({'error': 'Blog not found'}), 404
    return jsonify(blog.to_dict()), 200


@app.route('/api/admin/blogs')
@login_required
@require_role('admin')
def get_all_blogs():
    """Get all blogs (admin)"""
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return jsonify([b.to_dict() for b in blogs]), 200


@app.route('/api/admin/blogs', methods=['POST'])
@login_required
@require_role('admin')
def create_blog():
    """Create blog"""
    data = request.get_json()

    required = ['title', 'slug', 'excerpt', 'category', 'author']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'Missing required fields'}), 400

    if Blog.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Slug already exists'}), 400

    blog = Blog(
        title=data['title'],
        slug=data['slug'],
        excerpt=data['excerpt'],
        content=data.get('content'),
        category=data['category'],
        author=data['author'],
        read_time=data.get('readTime', '5 min read'),
        image=data.get('image'),
        featured=data.get('featured', False),
        published=data.get('published', True)
    )

    db.session.add(blog)
    db.session.commit()

    return jsonify(blog.to_dict()), 201


@app.route('/api/admin/blogs/<blog_id>', methods=['PUT'])
@login_required
@require_role('admin')
def update_blog(blog_id):
    """Update blog"""
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'error': 'Blog not found'}), 404

    data = request.get_json()

    # Check slug uniqueness if changed
    if data.get('slug') and data['slug'] != blog.slug:
        if Blog.query.filter_by(slug=data['slug']).first():
            return jsonify({'error': 'Slug already exists'}), 400

    for field in ['title', 'slug', 'excerpt', 'content', 'category', 'author', 'image']:
        if field in data:
            setattr(blog, field, data[field])

    if 'readTime' in data:
        blog.read_time = data['readTime']
    if 'featured' in data:
        blog.featured = data['featured']
    if 'published' in data:
        blog.published = data['published']

    db.session.commit()

    return jsonify(blog.to_dict()), 200


@app.route('/api/admin/blogs/<blog_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_blog(blog_id):
    """Delete blog"""
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'error': 'Blog not found'}), 404

    db.session.delete(blog)
    db.session.commit()

    return jsonify({'message': 'Blog deleted'}), 200


# ============================================
# ATO ALERTS ROUTES
# ============================================
@app.route('/api/ato-alerts')
def get_ato_alerts():
    """Get active ATO alerts"""
    now = datetime.utcnow()
    alerts = AtoAlert.query.filter_by(active=True).filter(
        (AtoAlert.expires_at == None) | (AtoAlert.expires_at > now)
    ).order_by(AtoAlert.priority).all()

    return jsonify([a.to_dict() for a in alerts]), 200


@app.route('/api/admin/ato-alerts')
@login_required
@require_role('admin')
def get_all_ato_alerts():
    """Get all ATO alerts (admin)"""
    alerts = AtoAlert.query.order_by(AtoAlert.priority).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@app.route('/api/admin/ato-alerts', methods=['POST'])
@login_required
@require_role('admin')
def create_ato_alert():
    """Create ATO alert"""
    data = request.get_json()

    if not all([data.get('title'), data.get('type'), data.get('link')]):
        return jsonify({'error': 'Title, type, and link are required'}), 400

    if data['type'] not in ['update', 'alert', 'reminder']:
        return jsonify({'error': 'Invalid type'}), 400

    alert = AtoAlert(
        title=data['title'],
        type=data['type'],
        link=data['link'],
        active=data.get('active', True),
        priority=data.get('priority', 0)
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify(alert.to_dict()), 201


@app.route('/api/admin/ato-alerts/<alert_id>', methods=['PUT'])
@login_required
@require_role('admin')
def update_ato_alert(alert_id):
    """Update ATO alert"""
    alert = AtoAlert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    data = request.get_json()

    for field in ['title', 'type', 'link']:
        if field in data:
            setattr(alert, field, data[field])

    if 'active' in data:
        alert.active = data['active']
    if 'priority' in data:
        alert.priority = data['priority']

    db.session.commit()

    return jsonify(alert.to_dict()), 200


@app.route('/api/admin/ato-alerts/<alert_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_ato_alert(alert_id):
    """Delete ATO alert"""
    alert = AtoAlert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    db.session.delete(alert)
    db.session.commit()

    return jsonify({'message': 'Alert deleted'}), 200


# ============================================
# CONTACT FORM (existing)
# ============================================
@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', 'Contact Form Submission').strip()
    message = data.get('message', '').strip()

    if not all([name, email, message]):
        return jsonify({'status': 'error', 'message': 'Name, email, and message are required'}), 400

    try:
        msg = Message(
            subject=f"[Contact Form] {subject}",
            recipients=[app.config['ADMIN_EMAIL']],
            reply_to=email
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px;">
                <h2>New Contact Form Submission</h2>
            </div>
            <div style="padding: 20px; background: #f9fafb; border: 1px solid #e5e7eb;">
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                <p><strong>Phone:</strong> {phone or 'Not provided'}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Message:</strong></p>
                <div style="background: white; padding: 15px; border-left: 4px solid #3b82f6;">{message}</div>
            </div>
        </div>
        """
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'Message sent successfully'}), 200

    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to send message'}), 500


# ============================================
# STATIC FILE SERVING (Frontend SPA)
# ============================================
@app.route('/')
def serve_index():
    """Serve the frontend index.html"""
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return app.send_static_file('index.html')
    return jsonify({'message': 'SMSF API is running', 'docs': '/api/health'}), 200


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files or fallback to index.html for SPA routing"""
    if app.static_folder:
        static_file = os.path.join(app.static_folder, path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return app.send_static_file(path)
        # Fallback to index.html for SPA routing
        if os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return app.send_static_file('index.html')
    return jsonify({'error': 'Not found'}), 404


# ============================================
# ERROR HANDLERS
# ============================================
@app.errorhandler(404)
def not_found(error):
    # For API routes, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    # For other routes, serve index.html if available (SPA routing)
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return app.send_static_file('index.html')
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================
# INITIALIZE DATABASE ON STARTUP
# ============================================
# This runs when gunicorn imports the app
try:
    with app.app_context():
        init_database()
        logger.info("App initialized successfully!")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    # Don't crash - let the app start anyway


# ============================================
# MAIN (for local development only)
# ============================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'

    logger.info(f"Starting Flask app on port {port}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
