"""
Form Model - Core form template entity
"""
from datetime import datetime
from app.extensions import db


class Form(db.Model):
    """Form template that can be linked to services or used standalone"""
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    form_type = db.Column(db.String(50), default='service')  # 'service', 'onboarding', 'general'
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Company-specific forms (NULL = system/default form)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)
    is_default = db.Column(db.Boolean, default=False)  # System-seeded default forms

    # Cloning support
    cloned_from_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=True)

    # Form status for draft/published workflow
    status = db.Column(db.String(20), default='published')  # draft, published, archived

    # Relationships
    questions = db.relationship('FormQuestion', backref='form', lazy='dynamic',
                                order_by='FormQuestion.order', cascade='all, delete-orphan',
                                foreign_keys='FormQuestion.form_id')
    created_by = db.relationship('User', backref='created_forms')
    company = db.relationship('Company', backref='forms')
    cloned_from = db.relationship('Form', remote_side=[id], backref='clones')

    TYPE_SERVICE = 'service'
    TYPE_ONBOARDING = 'onboarding'
    TYPE_GENERAL = 'general'

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    def to_dict(self, include_questions=True):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'form_type': self.form_type,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'company_id': self.company_id,
            'cloned_from_id': self.cloned_from_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if self.cloned_from:
            data['cloned_from_name'] = self.cloned_from.name
        if include_questions:
            data['questions'] = [q.to_dict() for q in self.questions]
        data['question_count'] = self.questions.count()
        return data

    def clone(self, new_name: str, company_id: int, created_by_id: str):
        """
        Clone this form for a company with all questions.

        Args:
            new_name: Name for the cloned form
            company_id: Company that owns the clone
            created_by_id: User creating the clone

        Returns:
            New Form instance (not committed)
        """
        cloned_form = Form(
            name=new_name,
            description=self.description,
            form_type=self.form_type,
            is_active=True,
            company_id=company_id,
            is_default=False,
            cloned_from_id=self.id,
            status=Form.STATUS_DRAFT,
            created_by_id=created_by_id
        )
        return cloned_form

    def __repr__(self):
        return f'<Form {self.name}>'
