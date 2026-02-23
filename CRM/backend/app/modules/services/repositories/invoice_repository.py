"""
Invoice Repository - Data access for Invoice, InvoiceLineItem, InvoicePayment entities
"""
from typing import List, Optional
from datetime import datetime
from app.common.repository import BaseRepository
from app.modules.services.models import Invoice, InvoiceLineItem, InvoicePayment
from app.modules.user.models import User, Role


class InvoiceRepository(BaseRepository[Invoice]):
    """Repository for Invoice data access"""
    model = Invoice

    def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        return Invoice.query.filter_by(invoice_number=invoice_number).first()

    def get_by_company(self, company_id: str, status: str = None,
                       page: int = 1, per_page: int = 20):
        """Get invoices for a company"""
        query = Invoice.query.filter_by(company_id=company_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Invoice.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_client(self, client_id: str, status: str = None,
                      page: int = 1, per_page: int = 20):
        """Get invoices for a client"""
        query = Invoice.query.filter_by(client_id=client_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Invoice.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_service_request(self, service_request_id: str) -> List[Invoice]:
        """Get invoices linked to a service request"""
        return Invoice.query.filter_by(service_request_id=service_request_id)\
            .order_by(Invoice.created_at.desc()).all()

    def get_overdue(self, company_id: str = None) -> List[Invoice]:
        """Get overdue invoices (past due date, not fully paid)"""
        from datetime import date
        query = Invoice.query.filter(
            Invoice.due_date < date.today(),
            Invoice.status.notin_([Invoice.STATUS_PAID, Invoice.STATUS_CANCELLED])
        )
        if company_id:
            query = query.filter_by(company_id=company_id)
        return query.order_by(Invoice.due_date.asc()).all()

    def get_pending_payment(self, company_id: str = None) -> List[Invoice]:
        """Get invoices with pending payments"""
        query = Invoice.query.filter(
            Invoice.status.in_([Invoice.STATUS_SENT, Invoice.STATUS_VIEWED, Invoice.STATUS_PARTIAL])
        )
        if company_id:
            query = query.filter_by(company_id=company_id)
        return query.order_by(Invoice.due_date.asc()).all()

    def get_draft_invoices(self, company_id: str) -> List[Invoice]:
        """Get draft invoices for a company"""
        return Invoice.query.filter_by(
            company_id=company_id,
            status=Invoice.STATUS_DRAFT
        ).order_by(Invoice.created_at.desc()).all()

    def get_revenue_summary(self, company_id: str, start_date: datetime = None,
                            end_date: datetime = None) -> dict:
        """Get revenue summary for a company"""
        from sqlalchemy import func

        query = Invoice.query.filter_by(company_id=company_id)

        if start_date:
            query = query.filter(Invoice.created_at >= start_date)
        if end_date:
            query = query.filter(Invoice.created_at <= end_date)

        invoices = query.all()

        return {
            'total_invoiced': sum(float(i.total or 0) for i in invoices),
            'total_paid': sum(float(i.amount_paid or 0) for i in invoices),
            'total_outstanding': sum(float(i.balance_due or 0) for i in invoices),
            'invoice_count': len(invoices),
            'paid_count': sum(1 for i in invoices if i.status == Invoice.STATUS_PAID),
            'pending_count': sum(1 for i in invoices if i.status in [
                Invoice.STATUS_SENT, Invoice.STATUS_VIEWED, Invoice.STATUS_PARTIAL
            ]),
        }

    def can_user_access_invoice(self, user: User, invoice: Invoice) -> bool:
        """Check if user can access a specific invoice"""
        if user.role.name == Role.SUPER_ADMIN:
            return True
        elif user.role.name in [Role.ADMIN, Role.ACCOUNTANT]:
            return user.company_id == invoice.company_id
        else:
            return user.id == invoice.client_id


class InvoiceLineItemRepository(BaseRepository[InvoiceLineItem]):
    """Repository for InvoiceLineItem data access"""
    model = InvoiceLineItem

    def get_by_invoice(self, invoice_id: str) -> List[InvoiceLineItem]:
        """Get all line items for an invoice"""
        return InvoiceLineItem.query.filter_by(invoice_id=invoice_id)\
            .order_by(InvoiceLineItem.order.asc()).all()

    def get_max_order(self, invoice_id: str) -> int:
        """Get the maximum order value for line items in an invoice"""
        from sqlalchemy import func
        result = InvoiceLineItem.query.filter_by(invoice_id=invoice_id)\
            .with_entities(func.max(InvoiceLineItem.order)).scalar()
        return result or 0


class InvoicePaymentRepository(BaseRepository[InvoicePayment]):
    """Repository for InvoicePayment data access"""
    model = InvoicePayment

    def get_by_invoice(self, invoice_id: str) -> List[InvoicePayment]:
        """Get all payments for an invoice"""
        return InvoicePayment.query.filter_by(invoice_id=invoice_id)\
            .order_by(InvoicePayment.payment_date.desc()).all()

    def get_total_paid(self, invoice_id: str) -> float:
        """Get total amount paid for an invoice"""
        from sqlalchemy import func
        result = InvoicePayment.query.filter_by(
            invoice_id=invoice_id,
            status='completed'
        ).with_entities(func.sum(InvoicePayment.amount)).scalar()
        return float(result or 0)

    def get_recent_payments(self, company_id: str = None, limit: int = 50) -> List[InvoicePayment]:
        """Get recent payments, optionally filtered by company"""
        query = InvoicePayment.query.join(Invoice)
        if company_id:
            query = query.filter(Invoice.company_id == company_id)
        return query.order_by(InvoicePayment.payment_date.desc()).limit(limit).all()
