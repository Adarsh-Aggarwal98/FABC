"""
Workflow Automation Executor

Executes automation actions triggered by workflow step transitions.
"""
import requests
from flask import current_app
from app.extensions import db
from app.modules.services.models import ServiceRequest
from app.modules.user.models import User, Role


class WorkflowAutomationExecutor:
    """Executes workflow automation actions"""

    @classmethod
    def execute(cls, automation, request: ServiceRequest, triggered_by: User):
        """
        Execute a single automation action.

        Args:
            automation: The automation configuration
            request: The service request
            triggered_by: The user who triggered the transition
        """
        from app.modules.services.models.workflow_models import WorkflowAutomation

        # Check conditions first
        if not cls._check_conditions(automation, request):
            return

        action_type = automation.action_type
        config = automation.action_config or {}

        try:
            if action_type == WorkflowAutomation.ACTION_NOTIFY:
                cls._execute_notify(automation, request, config)
            elif action_type == WorkflowAutomation.ACTION_ASSIGN:
                cls._execute_auto_assign(automation, request, config)
            elif action_type == WorkflowAutomation.ACTION_WEBHOOK:
                cls._execute_webhook(automation, request, config)
            elif action_type == WorkflowAutomation.ACTION_EMAIL:
                cls._execute_email(automation, request, config)
            elif action_type == WorkflowAutomation.ACTION_UPDATE_FIELD:
                cls._execute_update_field(automation, request, config)
            else:
                current_app.logger.warning(f'Unknown automation action type: {action_type}')
        except Exception as e:
            current_app.logger.error(f'Automation {automation.id} failed: {str(e)}')
            raise

    @classmethod
    def _check_conditions(cls, automation, request: ServiceRequest):
        """Check if automation conditions are met"""
        conditions = automation.conditions or {}

        # Invoice conditions
        if conditions.get('requires_invoice_raised') and not request.invoice_raised:
            return False
        if conditions.get('requires_invoice_paid') and not request.invoice_paid:
            return False

        # Assignment conditions
        if conditions.get('requires_assignment') and not request.assigned_accountant_id:
            return False
        if conditions.get('requires_no_assignment') and request.assigned_accountant_id:
            return False

        # Priority conditions
        required_priority = conditions.get('priority')
        if required_priority and request.priority != required_priority:
            return False

        return True

    @classmethod
    def _execute_notify(cls, automation, request: ServiceRequest, config: dict):
        """Send notification to specified recipients"""
        from app.modules.notifications.services import NotificationService

        notify_to = config.get('to', 'client')
        template = config.get('template')
        subject = config.get('subject', 'Notification from your accountant')

        recipients = []

        if notify_to == 'client':
            client = User.query.get(request.user_id)
            if client:
                recipients.append(client)
        elif notify_to == 'assigned_accountant':
            if request.assigned_accountant_id:
                accountant = User.query.get(request.assigned_accountant_id)
                if accountant:
                    recipients.append(accountant)
        elif notify_to == 'admins':
            request_user = User.query.get(request.user_id)
            if request_user and request_user.company_id:
                admin_role = Role.query.filter_by(name=Role.ADMIN).first()
                if admin_role:
                    admins = User.query.filter(
                        User.role_id == admin_role.id,
                        User.company_id == request_user.company_id,
                        User.is_active == True
                    ).all()
                    recipients.extend(admins)

        if recipients:
            NotificationService.send_automation_notification(
                request=request,
                recipients=recipients,
                subject=subject,
                template=template
            )

    @classmethod
    def _execute_auto_assign(cls, automation, request: ServiceRequest, config: dict):
        """Auto-assign request to an accountant"""
        if request.assigned_accountant_id:
            # Already assigned, skip
            return

        strategy = config.get('strategy', 'least_busy')
        fallback_to_admin = config.get('fallback_to_admin', True)

        # Get request user's company
        request_user = User.query.get(request.user_id)
        if not request_user or not request_user.company_id:
            current_app.logger.warning(f'Cannot auto-assign: request user has no company')
            return

        accountant = None

        if strategy == 'least_busy':
            accountant = cls._get_least_busy_accountant(request_user.company_id)
        elif strategy == 'round_robin':
            accountant = cls._get_round_robin_accountant(request_user.company_id)
        elif strategy == 'specific':
            accountant_id = config.get('accountant_id')
            if accountant_id:
                accountant = User.query.get(accountant_id)

        # Fallback to admin if no accountant found
        if not accountant and fallback_to_admin:
            admin_role = Role.query.filter_by(name=Role.ADMIN).first()
            if admin_role:
                accountant = User.query.filter(
                    User.role_id == admin_role.id,
                    User.company_id == request_user.company_id,
                    User.is_active == True
                ).first()

        if accountant:
            request.assigned_accountant_id = accountant.id
            db.session.commit()
            current_app.logger.info(f'Auto-assigned request {request.id} to {accountant.email}')

    @classmethod
    def _get_least_busy_accountant(cls, company_id: str):
        """Get the accountant with the fewest active requests"""
        from sqlalchemy import func

        accountant_role = Role.query.filter_by(name=Role.ACCOUNTANT).first()
        if not accountant_role:
            return None

        # Get all accountants in the company
        accountants = User.query.filter(
            User.role_id == accountant_role.id,
            User.company_id == company_id,
            User.is_active == True
        ).all()

        if not accountants:
            return None

        # Count active requests per accountant
        min_count = float('inf')
        least_busy = None

        for accountant in accountants:
            count = ServiceRequest.query.filter(
                ServiceRequest.assigned_accountant_id == accountant.id,
                ServiceRequest.status.notin_(['completed', 'cancelled'])
            ).count()

            if count < min_count:
                min_count = count
                least_busy = accountant

        return least_busy

    @classmethod
    def _get_round_robin_accountant(cls, company_id: str):
        """Get the next accountant in round-robin fashion"""
        accountant_role = Role.query.filter_by(name=Role.ACCOUNTANT).first()
        if not accountant_role:
            return None

        accountants = User.query.filter(
            User.role_id == accountant_role.id,
            User.company_id == company_id,
            User.is_active == True
        ).order_by(User.id).all()

        if not accountants:
            return None

        # Get the last assigned accountant for this company
        last_request = ServiceRequest.query.join(
            User, ServiceRequest.user_id == User.id
        ).filter(
            User.company_id == company_id,
            ServiceRequest.assigned_accountant_id.isnot(None)
        ).order_by(ServiceRequest.created_at.desc()).first()

        if last_request:
            last_accountant_id = last_request.assigned_accountant_id
            # Find the next accountant in the list
            for i, acc in enumerate(accountants):
                if acc.id == last_accountant_id:
                    next_index = (i + 1) % len(accountants)
                    return accountants[next_index]

        # Default to first accountant
        return accountants[0]

    @classmethod
    def _execute_webhook(cls, automation, request: ServiceRequest, config: dict):
        """Send webhook to external URL"""
        url = config.get('url')
        if not url:
            current_app.logger.warning('Webhook automation missing URL')
            return

        method = config.get('method', 'POST').upper()
        headers = config.get('headers', {})
        body_template = config.get('body', {})

        # Replace template variables
        body = cls._replace_template_vars(body_template, request)

        try:
            if method == 'POST':
                response = requests.post(url, json=body, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=body, headers=headers, timeout=30)
            elif method == 'GET':
                response = requests.get(url, params=body, headers=headers, timeout=30)
            else:
                current_app.logger.warning(f'Unsupported webhook method: {method}')
                return

            response.raise_for_status()
            current_app.logger.info(f'Webhook sent to {url}, status: {response.status_code}')
        except requests.RequestException as e:
            current_app.logger.error(f'Webhook to {url} failed: {str(e)}')
            raise

    @classmethod
    def _execute_email(cls, automation, request: ServiceRequest, config: dict):
        """Send email notification"""
        from app.modules.notifications.services import NotificationService

        to_email = config.get('to')
        if not to_email:
            # Default to client email
            client = User.query.get(request.user_id)
            if client:
                to_email = client.email

        subject = config.get('subject', 'Notification')
        template = config.get('template')
        body = config.get('body')

        if to_email:
            NotificationService.send_custom_email(
                to_email=to_email,
                subject=subject,
                template=template,
                body=body,
                context={'request': request.to_dict()}
            )

    @classmethod
    def _execute_update_field(cls, automation, request: ServiceRequest, config: dict):
        """Update a field on the service request"""
        field_name = config.get('field')
        value = config.get('value')

        if not field_name:
            current_app.logger.warning('Update field automation missing field name')
            return

        # Only allow updating certain safe fields
        allowed_fields = ['priority', 'internal_notes']

        if field_name not in allowed_fields:
            current_app.logger.warning(f'Field {field_name} not allowed for automation update')
            return

        if hasattr(request, field_name):
            setattr(request, field_name, value)
            db.session.commit()
            current_app.logger.info(f'Updated {field_name} on request {request.id}')

    @classmethod
    def _replace_template_vars(cls, template, request: ServiceRequest):
        """Replace template variables with actual values"""
        if isinstance(template, str):
            return cls._replace_string_vars(template, request)
        elif isinstance(template, dict):
            return {k: cls._replace_template_vars(v, request) for k, v in template.items()}
        elif isinstance(template, list):
            return [cls._replace_template_vars(item, request) for item in template]
        return template

    @classmethod
    def _replace_string_vars(cls, text: str, request: ServiceRequest):
        """Replace template variables in a string"""
        replacements = {
            '{{request.id}}': request.id,
            '{{request.request_number}}': request.request_number or '',
            '{{request.status}}': request.status,
            '{{request.xero_reference_job_id}}': request.xero_reference_job_id or '',
            '{{request.internal_reference}}': request.internal_reference or '',
            '{{request.invoice_amount}}': str(request.invoice_amount) if request.invoice_amount else '',
        }

        for var, value in replacements.items():
            text = text.replace(var, str(value))

        return text
