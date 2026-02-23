"""
Service Catalog Service - Domain service for service catalog operations
"""
from datetime import datetime
from app.extensions import db
from app.modules.services.models import Service, ServiceRequest, Query
from app.modules.user.models import User, Role
from app.common.exceptions import ValidationError, NotFoundError, AuthorizationError


class ServiceCatalogService:
    """Service for managing service catalog"""

    @staticmethod
    def create_service(name, description=None, category=None, base_price=None, form_id=None):
        """Create a new service"""
        service = Service(
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            form_id=form_id
        )
        db.session.add(service)
        db.session.commit()
        return service

    @staticmethod
    def update_service(service_id, data):
        """Update a service"""
        service = Service.query.get(service_id)
        if not service:
            raise NotFoundError('Service not found')

        updateable_fields = ['name', 'description', 'category', 'base_price', 'is_active', 'form_id']
        for field in updateable_fields:
            if field in data:
                setattr(service, field, data[field])

        db.session.commit()
        return service

    @staticmethod
    def get_service(service_id):
        """Get a service by ID"""
        service = Service.query.get(service_id)
        if not service:
            raise NotFoundError('Service not found')
        return service

    @staticmethod
    def get_services(active_only=True, category=None):
        """Get all services"""
        query = Service.query

        if active_only:
            query = query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)

        return query.order_by(Service.name).all()


class ServiceRequestService:
    """Service for managing service requests"""

    @staticmethod
    def _generate_internal_reference(company_id=None):
        """Generate a unique internal reference number for a request.

        Format: REF-YYYYMM-XXXXX (e.g., REF-202601-00001)
        The sequence resets each month.
        """
        from datetime import datetime
        from sqlalchemy import func

        current_date = datetime.utcnow()
        year_month = current_date.strftime('%Y%m')
        prefix = f"REF-{year_month}-"

        # Find the highest sequence number for this month
        latest_ref = db.session.query(
            func.max(ServiceRequest.internal_reference)
        ).filter(
            ServiceRequest.internal_reference.like(f"{prefix}%")
        ).scalar()

        if latest_ref:
            # Extract the sequence number and increment
            try:
                last_seq = int(latest_ref.split('-')[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"

    @staticmethod
    def create_request(user, service_id):
        """Create a single service request"""
        service = Service.query.get(service_id)
        if not service:
            raise NotFoundError('Service not found')

        # Generate internal reference
        internal_ref = ServiceRequestService._generate_internal_reference(user.company_id)

        request = ServiceRequest(
            user_id=user.id,
            service_id=service_id,
            status=ServiceRequest.STATUS_PENDING,
            internal_reference=internal_ref
        )
        db.session.add(request)
        db.session.commit()

        # Notify admins
        ServiceRequestService._notify_admins_new_request(request)

        return request

    @staticmethod
    def create_requests_for_user(user, service_ids):
        """Create multiple service requests for a user (during onboarding)"""
        requests = []
        for service_id in service_ids:
            service = Service.query.get(service_id)
            if service and service.is_active:
                # Generate internal reference for each request
                internal_ref = ServiceRequestService._generate_internal_reference(user.company_id)

                request = ServiceRequest(
                    user_id=user.id,
                    service_id=service_id,
                    status=ServiceRequest.STATUS_PENDING,
                    internal_reference=internal_ref
                )
                db.session.add(request)
                requests.append(request)

        db.session.commit()

        # Notify admins for each request
        for request in requests:
            ServiceRequestService._notify_admins_new_request(request)

        return requests

    @staticmethod
    def _notify_admins_new_request(request):
        """Send notification to all admins about new request"""
        from app.modules.notifications.services import NotificationService

        admin_role = Role.query.filter_by(name=Role.ADMIN).first()
        super_admin_role = Role.query.filter_by(name=Role.SUPER_ADMIN).first()

        admins = User.query.filter(
            User.role_id.in_([admin_role.id, super_admin_role.id]),
            User.is_active == True
        ).all()

        if admins:
            NotificationService.send_new_request_notification(request, admins)

    @staticmethod
    def assign_request(request_id, accountant_id, assigned_by):
        """Assign a request to an accountant"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        accountant = User.query.get(accountant_id)
        if not accountant:
            raise NotFoundError('Accountant not found')

        if accountant.role.name != Role.ACCOUNTANT:
            raise ValidationError('User is not an accountant')

        request.assigned_accountant_id = accountant_id
        request.status = ServiceRequest.STATUS_ASSIGNED
        db.session.commit()

        # Notify accountant
        from app.modules.notifications.services import NotificationService
        NotificationService.send_assignment_notification(request)

        return request

    @staticmethod
    def add_internal_note(request_id, note, added_by):
        """Add internal note to a request"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        # Only accountants, admins can add notes
        if added_by.role.name not in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]:
            raise AuthorizationError('Not authorized to add notes')

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        new_note = f"\n[{timestamp}] {added_by.full_name}: {note}"

        if request.internal_notes:
            request.internal_notes += new_note
        else:
            request.internal_notes = new_note.strip()

        db.session.commit()
        return request

    @staticmethod
    def update_invoice(request_id, invoice_raised=None, invoice_paid=None,
                       invoice_amount=None, payment_link=None):
        """Update invoice details"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        if invoice_raised is not None:
            request.invoice_raised = invoice_raised
            if invoice_raised:
                # Send invoice notification to user
                from app.modules.notifications.services import NotificationService
                NotificationService.send_invoice_notification(request)

        if invoice_paid is not None:
            request.invoice_paid = invoice_paid
            if invoice_paid:
                request.status = ServiceRequest.STATUS_PROCESSING

        if invoice_amount is not None:
            request.invoice_amount = invoice_amount

        if payment_link is not None:
            request.payment_link = payment_link

        db.session.commit()
        return request

    @staticmethod
    def update_status(request_id, status, updated_by):
        """Update request status"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        if status not in ServiceRequest.VALID_STATUSES:
            raise ValidationError(f'Invalid status: {status}')

        request.status = status

        if status == ServiceRequest.STATUS_COMPLETED:
            request.completed_at = datetime.utcnow()

        db.session.commit()
        return request

    @staticmethod
    def get_request(request_id):
        """Get a request by ID"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')
        return request

    @staticmethod
    def get_requests(user, status=None, page=1, per_page=20):
        """Get requests based on user role"""
        query = ServiceRequest.query

        if user.role.name == Role.USER:
            # Users see only their own requests
            query = query.filter_by(user_id=user.id)
        elif user.role.name == Role.ACCOUNTANT:
            # Accountants see only assigned requests
            query = query.filter_by(assigned_accountant_id=user.id)
        # Admins and super admins see all

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(ServiceRequest.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)


class QueryService:
    """Service for managing queries on requests"""

    @staticmethod
    def create_query(request_id, sender, message, attachment_url=None):
        """Create a query on a request"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        # Validate sender has access
        is_accountant = sender.role.name in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]
        is_request_owner = request.user_id == sender.id

        if not is_accountant and not is_request_owner:
            raise AuthorizationError('Not authorized to post query')

        query = Query(
            service_request_id=request_id,
            sender_id=sender.id,
            message=message,
            attachment_url=attachment_url
        )
        db.session.add(query)

        # Update request status
        if is_accountant and request.status != ServiceRequest.STATUS_QUERY_RAISED:
            request.status = ServiceRequest.STATUS_QUERY_RAISED
            # Notify user
            from app.modules.notifications.services import NotificationService
            NotificationService.send_query_notification(request, message)
        elif is_request_owner and request.status == ServiceRequest.STATUS_QUERY_RAISED:
            request.status = ServiceRequest.STATUS_ACCOUNTANT_REVIEW_PENDING

        db.session.commit()
        return query

    @staticmethod
    def get_queries(request_id, user):
        """Get all queries for a request"""
        request = ServiceRequest.query.get(request_id)
        if not request:
            raise NotFoundError('Request not found')

        # Validate access
        is_staff = user.role.name in [Role.SUPER_ADMIN, Role.ADMIN, Role.ACCOUNTANT]
        is_owner = request.user_id == user.id

        if not is_staff and not is_owner:
            raise AuthorizationError('Not authorized to view queries')

        return request.queries.order_by(Query.created_at.asc()).all()
