"""
Role Model - User role/permission definition
"""
from datetime import datetime
from app.extensions import db


class Role(db.Model):
    """Role model for user permissions"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='role', lazy='dynamic')

    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    SENIOR_ACCOUNTANT = 'senior_accountant'
    ACCOUNTANT = 'accountant'
    EXTERNAL_ACCOUNTANT = 'external_accountant'
    USER = 'user'

    @classmethod
    def get_or_create_default_roles(cls):
        """Create default roles if they don't exist"""
        default_roles = [
            {
                'name': cls.SUPER_ADMIN,
                'description': 'Full system access',
                'permissions': {'all': True}
            },
            {
                'name': cls.ADMIN,
                'description': 'Administrative access',
                'permissions': {'manage_users': True, 'manage_requests': True, 'view_reports': True, 'manage_invoices': True}
            },
            {
                'name': cls.SENIOR_ACCOUNTANT,
                'description': 'Senior accountant with admin privileges except invoicing',
                'permissions': {'manage_users': True, 'manage_requests': True, 'view_reports': True, 'manage_team': True}
            },
            {
                'name': cls.ACCOUNTANT,
                'description': 'Accountant access',
                'permissions': {'manage_assigned_requests': True, 'add_notes': True}
            },
            {
                'name': cls.USER,
                'description': 'Client user access',
                'permissions': {'view_own_requests': True, 'create_requests': True}
            }
        ]

        for role_data in default_roles:
            role = cls.query.filter_by(name=role_data['name']).first()
            if not role:
                role = cls(**role_data)
                db.session.add(role)

        db.session.commit()

    def __repr__(self):
        return f'<Role {self.name}>'
