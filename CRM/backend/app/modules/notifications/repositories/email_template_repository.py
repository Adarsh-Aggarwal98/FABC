"""
EmailTemplateRepository - Data access layer for EmailTemplate model
"""
from sqlalchemy import or_
from app.extensions import db
from app.modules.notifications.models.email_template import EmailTemplate


class EmailTemplateRepository:
    """Repository for email template data access operations"""

    @staticmethod
    def create(name, slug, subject, body_html, variables=None, company_id=None,
               service_id=None, template_type=None, service_category=None):
        """Create a new email template"""
        template = EmailTemplate(
            name=name,
            slug=slug,
            subject=subject,
            body_html=body_html,
            variables=variables or [],
            company_id=company_id,
            service_id=service_id,
            template_type=template_type,
            service_category=service_category
        )
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_by_id(template_id):
        """Get template by ID"""
        return EmailTemplate.query.get(template_id)

    @staticmethod
    def get_by_slug(slug, company_id=None):
        """Get template by slug, falling back to system template"""
        # First try company-specific template
        if company_id:
            template = EmailTemplate.query.filter_by(
                slug=slug,
                company_id=company_id,
                is_active=True
            ).first()
            if template:
                return template

        # Fall back to system template
        return EmailTemplate.query.filter_by(
            slug=slug,
            company_id=None,
            is_active=True
        ).first()

    @staticmethod
    def get_available_templates(company_id=None):
        """Get all templates available to a company (company + system templates)"""
        if company_id:
            return EmailTemplate.query.filter(
                EmailTemplate.is_active == True,
                or_(EmailTemplate.company_id == company_id, EmailTemplate.company_id == None)
            ).order_by(EmailTemplate.name).all()
        else:
            # Super admin sees all
            return EmailTemplate.query.filter_by(is_active=True).order_by(EmailTemplate.name).all()

    @staticmethod
    def get_by_company(company_id, include_system=True):
        """Get templates for a company"""
        if include_system:
            return EmailTemplate.query.filter(
                EmailTemplate.is_active == True,
                or_(EmailTemplate.company_id == company_id, EmailTemplate.company_id == None)
            ).order_by(EmailTemplate.name).all()
        else:
            return EmailTemplate.query.filter_by(
                company_id=company_id,
                is_active=True
            ).order_by(EmailTemplate.name).all()

    @staticmethod
    def get_system_templates():
        """Get all system-wide templates"""
        return EmailTemplate.query.filter_by(
            company_id=None,
            is_active=True
        ).order_by(EmailTemplate.name).all()

    @staticmethod
    def update(template_id, **kwargs):
        """Update a template"""
        template = EmailTemplate.query.get(template_id)
        if not template:
            return None

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        db.session.commit()
        return template

    @staticmethod
    def delete(template_id):
        """Delete a template"""
        template = EmailTemplate.query.get(template_id)
        if template:
            db.session.delete(template)
            db.session.commit()
            return True
        return False

    @staticmethod
    def exists_slug(slug, company_id=None, exclude_id=None):
        """Check if a slug already exists for the company"""
        query = EmailTemplate.query.filter_by(slug=slug, company_id=company_id)
        if exclude_id:
            query = query.filter(EmailTemplate.id != exclude_id)
        return query.first() is not None
