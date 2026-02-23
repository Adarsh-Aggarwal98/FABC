"""
Seed script to create test data for demo/development
Creates: Company, All user types, Client entities, Services, Requests in various statuses
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.modules.user.models.user import User
from app.modules.user.models.role import Role
from app.modules.company.models.company import Company
from app.modules.client_entity.models.client_entity import ClientEntity
from app.modules.services.models.service import Service
from app.modules.services.models.service_request import ServiceRequest
from app.modules.services.models.query import Query
from app.modules.services.models.job_note import JobNote
from app.modules.services.models.workflow_models import ServiceWorkflow, WorkflowStep
import bcrypt
from datetime import datetime, timedelta
import uuid
import random

def hash_password(password):
    """Hash password using bcrypt (same as User model)"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

app = create_app()

def generate_uuid():
    return str(uuid.uuid4())

def seed_data():
    with app.app_context():
        print("Starting seed data creation...")

        # Get roles
        roles = {r.name: r for r in Role.query.all()}
        print(f"Found roles: {list(roles.keys())}")

        # Check if test company exists
        test_company = Company.query.filter_by(name="Demo Accounting Firm").first()
        if not test_company:
            print("Creating test company...")
            test_company = Company(
                id=generate_uuid(),
                name="Demo Accounting Firm",
                trading_name="Demo Accountants",
                abn="12 345 678 901",
                email="admin@demoaccounting.com.au",
                phone="+61 2 1234 5678",
                address_line1="123 Demo Street",
                city="Sydney",
                state="NSW",
                postcode="2000",
                country="Australia",
                currency="AUD",
                currency_symbol="$",
                tax_type="GST",
                tax_label="GST",
                default_tax_rate=10.0,
                is_active=True
            )
            db.session.add(test_company)
            db.session.flush()

        company_id = test_company.id
        print(f"Company ID: {company_id}")

        # Create users of all types
        users_data = [
            {
                "email": "superadmin@demo.com",
                "first_name": "Super",
                "last_name": "Admin",
                "role": "super_admin",
                "password": "Demo@123"
            },
            {
                "email": "admin@demo.com",
                "first_name": "John",
                "last_name": "Admin",
                "role": "admin",
                "password": "Demo@123"
            },
            {
                "email": "senior@demo.com",
                "first_name": "Sarah",
                "last_name": "Senior",
                "role": "senior_accountant",
                "password": "Demo@123"
            },
            {
                "email": "accountant1@demo.com",
                "first_name": "Mike",
                "last_name": "Accountant",
                "role": "accountant",
                "password": "Demo@123"
            },
            {
                "email": "accountant2@demo.com",
                "first_name": "Lisa",
                "last_name": "Numbers",
                "role": "accountant",
                "password": "Demo@123"
            },
            {
                "email": "external@demo.com",
                "first_name": "External",
                "last_name": "Partner",
                "role": "external_accountant",
                "password": "Demo@123"
            },
            {
                "email": "client1@demo.com",
                "first_name": "Bob",
                "last_name": "BusinessOwner",
                "role": "user",
                "password": "Demo@123"
            },
            {
                "email": "client2@demo.com",
                "first_name": "Alice",
                "last_name": "Entrepreneur",
                "role": "user",
                "password": "Demo@123"
            },
            {
                "email": "client3@demo.com",
                "first_name": "Charlie",
                "last_name": "Contractor",
                "role": "user",
                "password": "Demo@123"
            },
        ]

        created_users = {}
        for user_data in users_data:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                created_users[user_data["role"]] = existing
                print(f"User {user_data['email']} already exists")
                continue

            role = roles.get(user_data["role"])
            if not role:
                print(f"Role {user_data['role']} not found, skipping user")
                continue

            user = User(
                id=generate_uuid(),
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password_hash=hash_password(user_data["password"]),
                role_id=role.id,
                company_id=company_id,
                is_active=True,
                is_verified=True,
                two_fa_enabled=False
            )
            db.session.add(user)
            created_users[user_data["role"]] = user
            print(f"Created user: {user_data['email']} ({user_data['role']})")

        db.session.flush()

        # Set supervisor for accountants
        senior = created_users.get("senior_accountant")
        if senior:
            for user in User.query.filter(User.role_id == roles["accountant"].id).all():
                if user.supervisor_id is None:
                    user.supervisor_id = senior.id
                    print(f"Set {senior.email} as supervisor for {user.email}")

        # Get client users
        client_users = User.query.filter(User.role_id == roles["user"].id, User.company_id == company_id).all()

        # Create client entities
        entities_data = [
            {"name": "Bob's Construction Pty Ltd", "abn": "11 222 333 444", "entity_type": "company", "user_idx": 0},
            {"name": "Bob Smith Family Trust", "abn": "11 222 333 445", "entity_type": "trust", "user_idx": 0},
            {"name": "Alice Tech Solutions", "abn": "22 333 444 555", "entity_type": "sole_trader", "user_idx": 1},
            {"name": "Alice & Co Holdings", "abn": "22 333 444 556", "entity_type": "company", "user_idx": 1},
            {"name": "Charlie Consulting", "abn": "33 444 555 666", "entity_type": "sole_trader", "user_idx": 2},
            {"name": "Smith Family SMSF", "abn": "44 555 666 777", "entity_type": "smsf", "user_idx": 0},
        ]

        created_entities = []
        for ent_data in entities_data:
            existing = ClientEntity.query.filter_by(abn=ent_data["abn"]).first()
            if existing:
                created_entities.append(existing)
                print(f"Entity {ent_data['name']} already exists")
                continue

            user_idx = ent_data["user_idx"]
            owner = client_users[user_idx] if user_idx < len(client_users) else client_users[0]

            entity = ClientEntity(
                id=generate_uuid(),
                company_id=company_id,
                created_by_id=owner.id,
                name=ent_data["name"],
                abn=ent_data["abn"],
                entity_type=ent_data["entity_type"],
                email=owner.email,
                phone="+61 4 1234 5678",
                is_active=True
            )
            entity._owner_id = owner.id  # Store for later use
            db.session.add(entity)
            created_entities.append(entity)
            print(f"Created entity: {ent_data['name']}")

        db.session.flush()

        # Get services
        services = Service.query.filter_by(is_active=True).all()
        if not services:
            # Get default workflow
            workflow = ServiceWorkflow.query.filter_by(is_default=True).first()

            services_data = [
                {"name": "BAS Preparation", "code": "BAS", "price": 350.00, "description": "Business Activity Statement preparation and lodgement"},
                {"name": "Tax Return - Individual", "code": "ITR", "price": 250.00, "description": "Individual tax return preparation"},
                {"name": "Tax Return - Company", "code": "CTR", "price": 800.00, "description": "Company tax return preparation"},
                {"name": "Bookkeeping Monthly", "code": "BKM", "price": 500.00, "description": "Monthly bookkeeping services"},
                {"name": "SMSF Annual Compliance", "code": "SMSF", "price": 1500.00, "description": "SMSF audit and compliance"},
                {"name": "Payroll Processing", "code": "PAY", "price": 200.00, "description": "Fortnightly payroll processing"},
            ]

            for svc_data in services_data:
                svc = Service(
                    workflow_id=workflow.id if workflow else None,
                    name=svc_data["name"],
                    category=svc_data["code"],
                    description=svc_data["description"],
                    base_price=svc_data["price"],
                    is_active=True
                )
                db.session.add(svc)
                services.append(svc)
                print(f"Created service: {svc_data['name']}")

            db.session.flush()

        # Get workflow steps for creating requests in different statuses
        workflow = ServiceWorkflow.query.filter_by(is_default=True).first()
        steps = {}
        if workflow:
            for step in WorkflowStep.query.filter_by(workflow_id=workflow.id).all():
                steps[step.name] = step

        # Get accountants for assignment
        accountants = User.query.filter(
            User.role_id.in_([roles["accountant"].id, roles["senior_accountant"].id]),
            User.company_id == company_id
        ).all()

        # Create service requests in various statuses
        requests_data = [
            # Pending requests (unassigned)
            {"entity_idx": 0, "service_idx": 0, "status": "pending", "step": "pending", "assigned": False, "days_ago": 1},
            {"entity_idx": 1, "service_idx": 1, "status": "pending", "step": "pending", "assigned": False, "days_ago": 2},

            # Assigned/Collecting docs
            {"entity_idx": 2, "service_idx": 0, "status": "assigned", "step": "collecting_docs", "assigned": True, "days_ago": 3},
            {"entity_idx": 3, "service_idx": 2, "status": "assigned", "step": "collecting_docs", "assigned": True, "days_ago": 4},

            # In Progress
            {"entity_idx": 0, "service_idx": 3, "status": "in_progress", "step": "in_progress", "assigned": True, "days_ago": 5},
            {"entity_idx": 4, "service_idx": 1, "status": "in_progress", "step": "in_progress", "assigned": True, "days_ago": 6},
            {"entity_idx": 2, "service_idx": 4, "status": "in_progress", "step": "in_progress", "assigned": True, "days_ago": 7},

            # Under Review
            {"entity_idx": 1, "service_idx": 0, "status": "review", "step": "review", "assigned": True, "days_ago": 8},
            {"entity_idx": 5, "service_idx": 4, "status": "review", "step": "review", "assigned": True, "days_ago": 9},

            # Awaiting Client (Query raised)
            {"entity_idx": 3, "service_idx": 1, "status": "query_raised", "step": "awaiting_client", "assigned": True, "days_ago": 10, "has_query": True},
            {"entity_idx": 0, "service_idx": 2, "status": "query_raised", "step": "awaiting_client", "assigned": True, "days_ago": 11, "has_query": True},

            # Ready for Lodgement
            {"entity_idx": 4, "service_idx": 0, "status": "lodgement", "step": "lodgement", "assigned": True, "days_ago": 12},

            # Invoicing
            {"entity_idx": 2, "service_idx": 1, "status": "invoicing", "step": "invoicing", "assigned": True, "days_ago": 14, "invoice_amount": 350.00},

            # Completed
            {"entity_idx": 1, "service_idx": 3, "status": "completed", "step": "completed", "assigned": True, "days_ago": 20, "invoice_amount": 500.00, "invoice_paid": True},
            {"entity_idx": 0, "service_idx": 1, "status": "completed", "step": "completed", "assigned": True, "days_ago": 25, "invoice_amount": 250.00, "invoice_paid": True},
            {"entity_idx": 3, "service_idx": 0, "status": "completed", "step": "completed", "assigned": True, "days_ago": 30, "invoice_amount": 350.00, "invoice_paid": False},

            # On Hold
            {"entity_idx": 5, "service_idx": 1, "status": "on_hold", "step": "on_hold", "assigned": True, "days_ago": 15},
        ]

        # Get last request number
        last_request = ServiceRequest.query.order_by(ServiceRequest.request_number.desc()).first()
        next_num = 1
        if last_request and last_request.request_number:
            try:
                next_num = int(last_request.request_number.split('-')[1]) + 1
            except:
                pass

        for req_data in requests_data:
            entity = created_entities[req_data["entity_idx"] % len(created_entities)]
            service = services[req_data["service_idx"] % len(services)]
            step = steps.get(req_data["step"])

            # Check if similar request exists
            existing = ServiceRequest.query.filter_by(
                client_entity_id=entity.id,
                service_id=service.id,
                status=req_data["status"]
            ).first()
            if existing:
                print(f"Request for {entity.name} - {service.name} ({req_data['status']}) already exists")
                continue

            request_number = f"REQ-{next_num:06d}"
            next_num += 1

            created_date = datetime.utcnow() - timedelta(days=req_data["days_ago"])

            # Get owner user ID from the entity's created_by_id or a client user
            owner_id = getattr(entity, '_owner_id', None) or entity.created_by_id or (client_users[0].id if client_users else None)

            request = ServiceRequest(
                id=generate_uuid(),
                user_id=owner_id,
                client_entity_id=entity.id,
                service_id=service.id,
                current_step_id=step.id if step else None,
                request_number=request_number,
                status=req_data["status"],
                priority="medium",
                description=f"Request for {service.name}",
                invoice_amount=req_data.get("invoice_amount"),
                invoice_paid=req_data.get("invoice_paid", False),
                created_at=created_date,
                updated_at=datetime.utcnow()
            )

            # Assign accountant
            if req_data["assigned"] and accountants:
                request.assigned_accountant_id = random.choice(accountants).id

            db.session.add(request)
            db.session.flush()

            # Add query if needed
            if req_data.get("has_query"):
                query = Query(
                    service_request_id=request.id,
                    sender_id=request.assigned_accountant_id or (accountants[0].id if accountants else None),
                    message="Additional information required:\n\nPlease provide the following documents:\n- Bank statements for the period\n- Receipt for major expenses",
                    is_internal=False,
                    created_at=created_date + timedelta(days=1)
                )
                db.session.add(query)

            # Add job notes for in-progress and later stages
            if req_data["status"] not in ["pending"]:
                note = JobNote(
                    service_request_id=request.id,
                    created_by_id=request.assigned_accountant_id or (accountants[0].id if accountants else None),
                    content=f"Started working on {service.name} for {entity.name}",
                    note_type="time_entry",
                    time_spent_minutes=random.randint(30, 180),
                    created_at=created_date + timedelta(hours=3)
                )
                db.session.add(note)

            print(f"Created request: {request_number} - {entity.name} - {service.name} ({req_data['status']})")

        db.session.commit()
        print("\n" + "="*50)
        print("SEED DATA CREATION COMPLETE!")
        print("="*50)
        print("\nTest Users (all passwords: Demo@123):")
        print("-" * 40)
        for user_data in users_data:
            print(f"  {user_data['role']:20} : {user_data['email']}")
        print("\nYou can now login at http://localhost:5174")
        print("="*50)

if __name__ == "__main__":
    seed_data()
