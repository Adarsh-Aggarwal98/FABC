"""
Company Form Use Cases - Business Logic for Company-specific Form operations
"""
import logging
from app.common.usecase import BaseCommandUseCase, BaseQueryUseCase, UseCaseResult
from app.extensions import db
from app.modules.forms.models.form import Form
from app.modules.forms.models.form_question import FormQuestion
from app.modules.forms.repositories.form_repository import FormRepository

# Configure module-level logger
logger = logging.getLogger(__name__)


class ListDefaultFormsUseCase(BaseQueryUseCase):
    """List all default/system forms available for cloning"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, include_questions: bool = False) -> UseCaseResult:
        # Get all default forms (system forms)
        forms = Form.query.filter_by(is_default=True, is_active=True).all()

        return UseCaseResult.ok({
            'forms': [f.to_dict(include_questions=include_questions) for f in forms],
            'total': len(forms)
        })


class CloneFormUseCase(BaseCommandUseCase):
    """
    Clone a form for a company.

    Business Rules:
    - Admin can clone any default form to their company
    - Super Admin can clone any form
    - Creates a copy with all questions
    - New form starts in draft status
    """

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int, user_id: str, new_name: str,
                description: str = None) -> UseCaseResult:
        from app.modules.user.models import User, Role

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            return UseCaseResult.fail('Only admins can clone forms', 'FORBIDDEN')

        if not user.company_id and user.role.name != Role.SUPER_ADMIN:
            return UseCaseResult.fail('User must belong to a company', 'NO_COMPANY')

        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        # Non-super admins can only clone default forms
        if user.role.name != Role.SUPER_ADMIN and not form.is_default:
            return UseCaseResult.fail('Can only clone default forms', 'FORBIDDEN')

        # Create cloned form
        cloned_form = form.clone(
            new_name=new_name,
            company_id=user.company_id,
            created_by_id=user_id
        )
        if description:
            cloned_form.description = description

        db.session.add(cloned_form)
        db.session.flush()  # Get the new form ID

        # Clone all questions
        for question in form.questions:
            cloned_question = FormQuestion(
                form_id=cloned_form.id,
                question_text=question.question_text,
                question_type=question.question_type,
                is_required=question.is_required,
                allow_attachment=question.allow_attachment,
                options=question.options,
                validation_rules=question.validation_rules,
                placeholder=question.placeholder,
                help_text=question.help_text,
                order=question.order,
                section_number=question.section_number,
                section_title=question.section_title,
                section_description=question.section_description,
                is_section_repeatable=question.is_section_repeatable,
                section_group=question.section_group,
                min_section_repeats=question.min_section_repeats,
                max_section_repeats=question.max_section_repeats,
                conditional_value=question.conditional_value
                # Note: conditional_on_question_id needs special handling for cloned forms
            )
            db.session.add(cloned_question)

        db.session.commit()

        return UseCaseResult.ok({
            'form': cloned_form.to_dict(),
            'message': f"Form cloned successfully from '{form.name}'"
        })


class CreateCompanyFormUseCase(BaseCommandUseCase):
    """
    Create a new form for a company (Admin can create).

    Business Rules:
    - Super Admin creates system/default forms
    - Admin creates company-specific forms
    """

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, name: str, form_type: str, user_id: str,
                description: str = None, questions: list = None) -> UseCaseResult:
        from app.modules.user.models import User, Role

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            return UseCaseResult.fail('Only admins can create forms', 'FORBIDDEN')

        # Determine if this is a system form or company form
        is_default = user.role.name == Role.SUPER_ADMIN
        company_id = None if is_default else user.company_id

        if not company_id and user.role.name == Role.ADMIN:
            return UseCaseResult.fail('User must belong to a company', 'NO_COMPANY')

        form = Form(
            name=name,
            description=description,
            form_type=form_type,
            created_by_id=user_id,
            company_id=company_id,
            is_default=is_default,
            status=Form.STATUS_DRAFT
        )
        self.form_repo.create(form)
        db.session.flush()

        if questions:
            for idx, q_data in enumerate(questions):
                question = FormQuestion(
                    form_id=form.id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    is_required=q_data.get('is_required', False),
                    allow_attachment=q_data.get('allow_attachment', False),
                    options=q_data.get('options'),
                    validation_rules=q_data.get('validation_rules'),
                    placeholder=q_data.get('placeholder'),
                    help_text=q_data.get('help_text'),
                    order=q_data.get('order', idx)
                )
                db.session.add(question)

        db.session.commit()
        return UseCaseResult.ok({'form': form.to_dict()})


class UpdateFormStatusUseCase(BaseCommandUseCase):
    """Update form status (publish, archive, etc.)"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int, user_id: str, status: str) -> UseCaseResult:
        from app.modules.user.models import User, Role

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        # Check access
        if user.role.name == Role.SUPER_ADMIN:
            pass  # Can update any form
        elif user.role.name == Role.ADMIN:
            # Can only update company forms
            if form.company_id != user.company_id:
                return UseCaseResult.fail('Access denied to this form', 'FORBIDDEN')
        else:
            return UseCaseResult.fail('Only admins can update form status', 'FORBIDDEN')

        if status not in [Form.STATUS_DRAFT, Form.STATUS_PUBLISHED, Form.STATUS_ARCHIVED]:
            return UseCaseResult.fail(f'Invalid status: {status}', 'INVALID_STATUS')

        form.status = status
        db.session.commit()

        return UseCaseResult.ok({
            'form': form.to_dict(),
            'message': f"Form status updated to '{status}'"
        })


class ListCompanyFormsUseCase(BaseQueryUseCase):
    """List forms available to a company (includes defaults + company-specific)"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, user_id: str, include_defaults: bool = True,
                form_type: str = None, page: int = 1, per_page: int = 20) -> UseCaseResult:
        from app.modules.user.models import User, Role

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Build query
        query = Form.query.filter_by(is_active=True)

        # Filter by type if specified
        if form_type:
            query = query.filter_by(form_type=form_type)

        if user.role.name == Role.SUPER_ADMIN:
            # Super Admin sees all forms
            pass
        else:
            # Regular users see: default forms + their company's forms
            if include_defaults:
                query = query.filter(
                    db.or_(
                        Form.is_default == True,
                        Form.company_id == user.company_id
                    )
                )
            else:
                query = query.filter_by(company_id=user.company_id)

        # Only show published forms to non-admins
        if user.role.name not in [Role.SUPER_ADMIN, Role.ADMIN]:
            query = query.filter_by(status=Form.STATUS_PUBLISHED)

        pagination = query.order_by(Form.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return UseCaseResult.ok({
            'forms': [f.to_dict(include_questions=False) for f in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })


class DeleteCompanyFormUseCase(BaseCommandUseCase):
    """Delete a company-specific form (not default forms)"""

    def __init__(self):
        self.form_repo = FormRepository()

    def execute(self, form_id: int, user_id: str) -> UseCaseResult:
        from app.modules.user.models import User, Role

        user = User.query.get(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        form = self.form_repo.get_by_id(form_id)
        if not form:
            return UseCaseResult.fail('Form not found', 'NOT_FOUND')

        # Check access
        if user.role.name == Role.SUPER_ADMIN:
            pass  # Can delete any form
        elif user.role.name == Role.ADMIN:
            # Can only delete company forms
            if form.company_id != user.company_id:
                return UseCaseResult.fail('Access denied to this form', 'FORBIDDEN')
            if form.is_default:
                return UseCaseResult.fail('Cannot delete default forms', 'FORBIDDEN')
        else:
            return UseCaseResult.fail('Only admins can delete forms', 'FORBIDDEN')

        self.form_repo.delete(form)
        db.session.commit()

        return UseCaseResult.ok({'message': 'Form deleted successfully'})
