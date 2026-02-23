"""
Renewal Service - Handles recurring service renewal tracking and reminders
"""
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import current_app
from app.extensions import db
from app.modules.services.models import Service, ServiceRequest, ServiceRenewal
from app.modules.notifications.models import EmailTemplate, Notification
from app.modules.user.models import User


class RenewalService:
    """Service for managing recurring service renewals and reminders"""

    @staticmethod
    def calculate_next_due_date(service, from_date=None):
        """
        Calculate the next due date for a recurring service.

        Args:
            service: Service model instance
            from_date: Date to calculate from (defaults to today)

        Returns:
            date: Next due date
        """
        if not service.is_recurring:
            return None

        base_date = from_date or date.today()

        # If service has a fixed due month/day (like ITR due Oct 31)
        if service.renewal_due_month and service.renewal_due_day:
            # Find the next occurrence of this month/day
            next_due = date(base_date.year, service.renewal_due_month, service.renewal_due_day)

            # If we've passed this year's due date, move to next year
            if next_due <= base_date:
                next_due = date(base_date.year + 1, service.renewal_due_month, service.renewal_due_day)

            return next_due

        # Otherwise calculate based on renewal period
        period_months = service.renewal_period_months or 12

        if service.renewal_due_day:
            # Use fixed day of month
            next_due = base_date + relativedelta(months=period_months)
            # Set to the specified day, handling month-end cases
            try:
                next_due = next_due.replace(day=service.renewal_due_day)
            except ValueError:
                # Day doesn't exist in this month (e.g., Feb 31), use last day
                next_month = next_due.replace(day=1) + relativedelta(months=1)
                next_due = next_month - timedelta(days=1)
        else:
            # Simply add the period
            next_due = base_date + relativedelta(months=period_months)

        return next_due

    @staticmethod
    def create_or_update_renewal(user_id, service_id, company_id, completed_request_id=None):
        """
        Create or update a renewal record when a service is completed.

        Args:
            user_id: ID of the client
            service_id: ID of the service
            company_id: ID of the company
            completed_request_id: ID of the completed service request

        Returns:
            ServiceRenewal instance or None
        """
        service = Service.query.get(service_id)
        if not service or not service.is_recurring:
            return None

        # Calculate next due date
        next_due = RenewalService.calculate_next_due_date(service)
        if not next_due:
            return None

        # Check if renewal record already exists for this due date
        existing = ServiceRenewal.query.filter_by(
            user_id=user_id,
            service_id=service_id,
            next_due_date=next_due
        ).first()

        if existing:
            # Update existing record
            existing.last_completed_at = datetime.utcnow()
            existing.last_request_id = completed_request_id
            existing.status = ServiceRenewal.STATUS_PENDING
            existing.reminders_sent = []
            existing.is_active = True
            db.session.commit()
            return existing

        # Create new renewal record
        renewal = ServiceRenewal(
            user_id=user_id,
            service_id=service_id,
            company_id=company_id,
            last_completed_at=datetime.utcnow(),
            last_request_id=completed_request_id,
            next_due_date=next_due,
            status=ServiceRenewal.STATUS_PENDING
        )
        db.session.add(renewal)
        db.session.commit()

        current_app.logger.info(
            f'Created renewal for user {user_id}, service {service_id}, due {next_due}'
        )
        return renewal

    @staticmethod
    def get_due_reminders():
        """
        Get all renewals that need reminders sent today.

        Returns:
            List of (ServiceRenewal, days_before) tuples
        """
        today = date.today()
        reminders_to_send = []

        # Get all active pending/reminded renewals
        renewals = ServiceRenewal.query.filter(
            ServiceRenewal.is_active == True,
            ServiceRenewal.status.in_([ServiceRenewal.STATUS_PENDING, ServiceRenewal.STATUS_REMINDED]),
            ServiceRenewal.next_due_date >= today
        ).all()

        for renewal in renewals:
            service = renewal.service
            if not service or not service.renewal_reminder_days:
                continue

            days_until_due = (renewal.next_due_date - today).days

            # Check each reminder threshold
            for days_before in service.renewal_reminder_days:
                if days_until_due == days_before:
                    # Check if this reminder hasn't been sent yet
                    already_sent = any(
                        r.get('days_before') == days_before
                        for r in (renewal.reminders_sent or [])
                    )
                    if not already_sent:
                        reminders_to_send.append((renewal, days_before))
                        break  # Only one reminder per day

        return reminders_to_send

    @staticmethod
    def get_renewal_template(service, company_id):
        """
        Get the appropriate email template for a renewal reminder.

        Priority:
        1. Company-specific template for this service
        2. Company-specific template for this category
        3. System template for this category
        4. General renewal template

        Args:
            service: Service model instance
            company_id: Company ID

        Returns:
            EmailTemplate instance
        """
        # Try company-specific service template
        if service:
            template = EmailTemplate.query.filter_by(
                service_id=service.id,
                company_id=company_id,
                template_type='renewal',
                is_active=True
            ).first()
            if template:
                return template

        # Try company-specific category template
        if service and service.category:
            template = EmailTemplate.query.filter_by(
                service_category=service.category,
                company_id=company_id,
                template_type='renewal',
                is_active=True
            ).first()
            if template:
                return template

        # Try system category template
        if service and service.category:
            category_slug_map = {
                'tax_agent': 'tax_renewal_reminder',
                'bas_agent': 'bas_renewal_reminder',
                'auditor': 'smsf_renewal_reminder',
                'bookkeeper': 'bookkeeping_monthly_reminder',
                'financial_planner': 'fp_annual_review_reminder',
            }
            slug = category_slug_map.get(service.category)
            if slug:
                template = EmailTemplate.query.filter_by(
                    slug=slug,
                    company_id=None,
                    is_active=True
                ).first()
                if template:
                    return template

        # Fallback to general renewal template
        return EmailTemplate.query.filter_by(
            slug='general_renewal_reminder',
            company_id=None,
            is_active=True
        ).first()

    @staticmethod
    def send_renewal_reminder(renewal, days_before):
        """
        Send a renewal reminder email.

        Args:
            renewal: ServiceRenewal instance
            days_before: Number of days before due date

        Returns:
            bool: True if sent successfully
        """
        from app.modules.notifications.services import NotificationService

        user = renewal.user
        service = renewal.service
        company = renewal.company

        if not user or not service or not company:
            current_app.logger.error(f'Missing data for renewal {renewal.id}')
            return False

        # Get appropriate template
        template = RenewalService.get_renewal_template(service, renewal.company_id)
        if not template:
            current_app.logger.error(f'No renewal template found for service {service.id}')
            return False

        # Build context for template
        portal_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        tax_year = f"{renewal.next_due_date.year - 1}-{renewal.next_due_date.year}"
        financial_year = tax_year

        context = {
            'client_name': user.full_name or user.email,
            'client_email': user.email,
            'company_name': company.name,
            'service_name': service.name,
            'due_date': renewal.next_due_date.strftime('%B %d, %Y'),
            'days_remaining': str(days_before),
            'tax_year': tax_year,
            'financial_year': financial_year,
            'due_year': str(renewal.next_due_date.year),
            'period': f"Q{((renewal.next_due_date.month - 1) // 3) + 1} {renewal.next_due_date.year}",
            'month': renewal.next_due_date.strftime('%B %Y'),
            'fund_name': f"{user.full_name} SMSF",  # Default for SMSF
            'portal_link': portal_url,
            'booking_link': f"{portal_url}/book-appointment",
        }

        # Render template
        subject, body = template.render(context)

        # Send email
        try:
            NotificationService.send_email(
                to_email=user.email,
                subject=subject,
                html_body=body,
                company_id=renewal.company_id
            )

            # Record reminder sent
            renewal.record_reminder_sent(days_before)
            db.session.commit()

            # Create in-app notification
            Notification.create(
                user_id=user.id,
                title=f'{service.name} Reminder',
                message=f'Your {service.name} is due on {renewal.next_due_date.strftime("%B %d, %Y")}',
                notification_type=Notification.TYPE_INFO,
                link='/services/new'
            )

            current_app.logger.info(
                f'Sent {days_before}-day renewal reminder to {user.email} for service {service.name}'
            )
            return True

        except Exception as e:
            current_app.logger.error(f'Failed to send renewal reminder: {str(e)}')
            return False

    @staticmethod
    def process_daily_reminders():
        """
        Process all due reminders for today.
        Called by the scheduler daily.

        Returns:
            dict: Summary of reminders sent
        """
        current_app.logger.info('Starting daily renewal reminder processing')

        reminders = RenewalService.get_due_reminders()
        sent_count = 0
        failed_count = 0

        for renewal, days_before in reminders:
            try:
                if RenewalService.send_renewal_reminder(renewal, days_before):
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                current_app.logger.error(f'Error processing renewal {renewal.id}: {str(e)}')
                failed_count += 1

        current_app.logger.info(
            f'Daily reminder processing complete. Sent: {sent_count}, Failed: {failed_count}'
        )

        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': len(reminders)
        }

    @staticmethod
    def get_upcoming_renewals(company_id, days_ahead=30, status=None):
        """
        Get upcoming renewals for a company.

        Args:
            company_id: Company ID
            days_ahead: Number of days to look ahead
            status: Filter by status (optional)

        Returns:
            List of ServiceRenewal instances
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        query = ServiceRenewal.query.filter(
            ServiceRenewal.company_id == company_id,
            ServiceRenewal.is_active == True,
            ServiceRenewal.next_due_date >= today,
            ServiceRenewal.next_due_date <= end_date
        )

        if status:
            query = query.filter(ServiceRenewal.status == status)

        return query.order_by(ServiceRenewal.next_due_date).all()

    @staticmethod
    def mark_renewal_completed(renewal_id, request_id=None):
        """
        Mark a renewal as completed and create next renewal.

        Args:
            renewal_id: ID of the renewal
            request_id: ID of the new service request (optional)

        Returns:
            ServiceRenewal: The new renewal record
        """
        renewal = ServiceRenewal.query.get(renewal_id)
        if not renewal:
            return None

        # Mark current as completed
        renewal.status = ServiceRenewal.STATUS_COMPLETED
        db.session.commit()

        # Create next renewal
        return RenewalService.create_or_update_renewal(
            user_id=renewal.user_id,
            service_id=renewal.service_id,
            company_id=renewal.company_id,
            completed_request_id=request_id
        )

    @staticmethod
    def skip_renewal(renewal_id, reason=None):
        """
        Skip a renewal (e.g., client no longer needs this service).

        Args:
            renewal_id: ID of the renewal
            reason: Optional reason for skipping

        Returns:
            ServiceRenewal instance
        """
        renewal = ServiceRenewal.query.get(renewal_id)
        if not renewal:
            return None

        renewal.status = ServiceRenewal.STATUS_SKIPPED
        renewal.is_active = False
        db.session.commit()

        return renewal

    @staticmethod
    def send_manual_reminder(renewal_id):
        """
        Manually send a reminder for a renewal.

        Args:
            renewal_id: ID of the renewal

        Returns:
            bool: True if sent successfully
        """
        renewal = ServiceRenewal.query.get(renewal_id)
        if not renewal:
            return False

        days_until_due = (renewal.next_due_date - date.today()).days
        return RenewalService.send_renewal_reminder(renewal, days_until_due)
