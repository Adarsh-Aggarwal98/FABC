"""
EmailTemplate Model - Customizable email templates
"""
from datetime import datetime
from app.extensions import db


class EmailTemplate(db.Model):
    """Email templates for customizable email communications"""
    __tablename__ = 'email_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)  # Unique identifier for template
    subject = db.Column(db.String(500), nullable=False)
    body_html = db.Column(db.Text, nullable=False)

    # Template variables as JSON (e.g., ["client_name", "service_name", "due_date"])
    variables = db.Column(db.JSON, default=list)

    # Company scope - NULL means system-wide template (super admin created)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

    # Service association - NULL means general template (applies to all services)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='SET NULL'), nullable=True)

    # Template type for categorization
    template_type = db.Column(db.String(50))  # welcome, invoice, payment, query, documents, renewal, completion

    # Service category for category-specific templates
    service_category = db.Column(db.String(50))  # tax_agent, bas_agent, auditor, bookkeeper, etc.

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('email_templates', lazy='dynamic'))

    # Unique constraint: slug must be unique within a company (or globally for system templates)
    __table_args__ = (
        db.UniqueConstraint('slug', 'company_id', name='uq_template_slug_company'),
    )

    # Default template slugs
    SLUG_DOCUMENT_REQUEST = 'document_request'
    SLUG_LODGEMENT_CONFIRMATION = 'lodgement_confirmation'
    SLUG_PAYMENT_REMINDER = 'payment_reminder'
    SLUG_ANNUAL_REMINDER = 'annual_reminder'
    SLUG_BIRTHDAY = 'birthday'
    SLUG_WELCOME = 'welcome'
    SLUG_ASSIGNMENT_NOTIFICATION = 'assignment_notification'

    @classmethod
    def get_template(cls, slug, company_id=None):
        """Get template by slug, falling back to system template if company template not found"""
        # First try company-specific template
        if company_id:
            template = cls.query.filter_by(slug=slug, company_id=company_id, is_active=True).first()
            if template:
                return template

        # Fall back to system template
        return cls.query.filter_by(slug=slug, company_id=None, is_active=True).first()

    @classmethod
    def get_available_templates(cls, company_id=None):
        """Get all templates available to a company (company + system templates)"""
        from sqlalchemy import or_

        if company_id:
            return cls.query.filter(
                cls.is_active == True,
                or_(cls.company_id == company_id, cls.company_id == None)
            ).order_by(cls.name).all()
        else:
            # Super admin sees all
            return cls.query.filter_by(is_active=True).order_by(cls.name).all()

    def render(self, context):
        """Render template with given context variables"""
        subject = self.subject
        body = self.body_html

        for key, value in context.items():
            placeholder = f'{{{key}}}'
            subject = subject.replace(placeholder, str(value) if value else '')
            body = body.replace(placeholder, str(value) if value else '')

        return subject, body

    def to_dict(self, include_company=False, include_service=False):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'subject': self.subject,
            'body_html': self.body_html,
            'variables': self.variables,
            'service_id': self.service_id,
            'template_type': self.template_type,
            'service_category': self.service_category,
            'is_active': self.is_active,
            'is_system': self.company_id is None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_company and self.company:
            data['company'] = {
                'id': self.company.id,
                'name': self.company.name
            }

        if include_service and self.service_id:
            from app.modules.services.models import Service
            service = Service.query.get(self.service_id)
            if service:
                data['service'] = {
                    'id': service.id,
                    'name': service.name,
                    'category': service.category
                }

        return data

    def __repr__(self):
        return f'<EmailTemplate {self.slug}>'
