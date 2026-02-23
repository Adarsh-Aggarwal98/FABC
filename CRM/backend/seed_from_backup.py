"""
Seed script to import system data from backup
Excludes: companies, users, and company-specific data
Includes: services, forms, workflows, email templates (system), currencies, tax_types
"""
import os
import sys
import bcrypt

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

app = create_app()

def seed_data():
    with app.app_context():
        from app.modules.user.models import Role, User
        from app.modules.company.models import Company

        # 1. Check/Create Roles
        print("Checking roles...")
        roles_data = [
            (1, 'super_admin', 'Full system access', '{"all": true}'),
            (2, 'admin', 'Administrative access', '{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_invoices": true}'),
            (3, 'senior_accountant', 'Senior accountant with admin privileges', '{"manage_users": true, "manage_requests": true, "view_reports": true, "manage_team": true}'),
            (4, 'accountant', 'Accountant access', '{"manage_assigned_requests": true, "add_notes": true}'),
            (5, 'external_accountant', 'External accountant access', '{"manage_assigned_requests": true, "add_notes": true, "external": true}'),
            (6, 'user', 'Client user access', '{"view_own_requests": true, "create_requests": true}'),
        ]

        for role_id, name, desc, perms in roles_data:
            existing = Role.query.filter_by(name=name).first()
            if not existing:
                role = Role(id=role_id, name=name, description=desc)
                role.permissions = perms
                db.session.add(role)
                print(f"  Created role: {name}")

        db.session.commit()

        # 2. Create Company
        print("Creating Pointers Consulting company...")
        company = Company.query.filter_by(name='Pointers Consulting').first()
        if not company:
            company = Company(
                name='Pointers Consulting',
                trading_name='Pointers Consulting Pty Ltd',
                email='sam@pointersconsulting.com.au',
                phone='+61 426 784 982',
                address_line1='Sydney',
                city='Sydney',
                state='NSW',
                postcode='2000',
                country='Australia',
                plan_type='enterprise',
                max_users=100,
                max_clients=10000,
                primary_color='#2D8C3C',
                secondary_color='#1F7A2E',
                tertiary_color='#3BA34D',
                logo_url='/assets/pointers-logo.png',
                sidebar_bg_color='#0f172a',
                sidebar_text_color='#ffffff',
                sidebar_hover_bg_color='#334155'
            )
            db.session.add(company)
            db.session.flush()
            print(f"  Created company: {company.name}")

        # 3. Create Admin User
        print("Creating admin user...")
        admin = User.query.filter_by(email='aggarwal.adarsh98@gmail.com').first()
        super_admin_role = Role.query.filter_by(name='super_admin').first()

        if not admin:
            password_hash = bcrypt.hashpw('Big@200650078296'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                email='aggarwal.adarsh98@gmail.com',
                password_hash=password_hash,
                role_id=super_admin_role.id,
                company_id=company.id,
                first_name='Adarsh',
                last_name='Aggarwal',
                is_active=True,
                is_verified=True,
                is_first_login=False,
                two_fa_enabled=False
            )
            db.session.add(admin)
            print(f"  Created admin: {admin.email}")
        else:
            # Update password
            admin.password_hash = bcrypt.hashpw('Big@200650078296'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(f"  Updated admin password: {admin.email}")

        db.session.commit()
        print("\nSeed complete!")
        print(f"  Admin email: aggarwal.adarsh98@gmail.com")
        print(f"  Admin password: Big@200650078296")

if __name__ == '__main__':
    seed_data()
