"""
Service Model - Service catalog definition
"""
from datetime import datetime
from app.extensions import db


class Service(db.Model):
    """Service catalog - types of services offered"""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)  # System-seeded default services
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=True)  # Link to custom form

    # Workflow - link to custom workflow (NULL means use default workflow)
    workflow_id = db.Column(db.String(36), db.ForeignKey('service_workflows.id'), nullable=True)

    # Cost tracking - default estimated cost as percentage of revenue
    cost_percentage = db.Column(db.Numeric(5, 2), default=0)  # e.g., 40 means 40% cost
    cost_category = db.Column(db.String(50))  # For grouping in analytics

    # Renewal configuration for recurring services
    is_recurring = db.Column(db.Boolean, default=False)  # Is this a recurring service?
    renewal_period_months = db.Column(db.Integer, default=12)  # How often (12=yearly, 3=quarterly, 1=monthly)
    renewal_reminder_days = db.Column(db.JSON, default=lambda: [30, 14, 7])  # Days before due to send reminders
    renewal_due_month = db.Column(db.Integer)  # Fixed due month (e.g., 10 for October) - NULL means calculated
    renewal_due_day = db.Column(db.Integer)  # Fixed due day (e.g., 31)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    form = db.relationship('Form', backref='services')
    requests = db.relationship('ServiceRequest', backref='service', lazy='dynamic')
    company_settings = db.relationship('CompanyServiceSettings', backref='service', lazy='dynamic')

    def to_dict(self, include_form=False, company_id=None):
        from .company_service_settings import CompanyServiceSettings

        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'base_price': float(self.base_price) if self.base_price else None,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'form_id': self.form_id,
            'workflow_id': self.workflow_id,
            'cost_percentage': float(self.cost_percentage) if self.cost_percentage else 0,
            'cost_category': self.cost_category,
            'is_recurring': self.is_recurring,
            'renewal_period_months': self.renewal_period_months,
            'renewal_reminder_days': self.renewal_reminder_days or [30, 14, 7],
            'renewal_due_month': self.renewal_due_month,
            'renewal_due_day': self.renewal_due_day,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        # Include company-specific settings if company_id provided
        if company_id:
            settings = CompanyServiceSettings.query.filter_by(
                company_id=company_id,
                service_id=self.id
            ).first()
            if settings:
                data['company_settings'] = settings.to_dict()
                # Apply overrides for display
                if settings.custom_name:
                    data['display_name'] = settings.custom_name
                if settings.custom_description:
                    data['display_description'] = settings.custom_description
                if settings.custom_price is not None:
                    data['display_price'] = float(settings.custom_price)
                data['is_active_for_company'] = settings.is_active
            else:
                data['is_active_for_company'] = True  # Default to active if no settings

        if include_form and self.form:
            data['form'] = self.form.to_dict()
        return data

    def __repr__(self):
        return f'<Service {self.name}>'
