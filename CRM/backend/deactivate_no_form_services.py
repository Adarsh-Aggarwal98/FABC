"""
One-time script to deactivate all services that don't have a form attached.
Run: python deactivate_no_form_services.py
"""
import os
from app import create_app
from app.extensions import db
from app.modules.services.models import Service

app = create_app()

with app.app_context():
    services_without_forms = Service.query.filter(
        Service.form_id.is_(None),
        Service.is_active == True
    ).all()

    if not services_without_forms:
        print("No active services without forms found.")
    else:
        print(f"Found {len(services_without_forms)} active services without forms:")
        for s in services_without_forms:
            print(f"  - [{s.id}] {s.name} (category: {s.category})")
            s.is_active = False

        db.session.commit()
        print(f"\nDeactivated {len(services_without_forms)} services.")
