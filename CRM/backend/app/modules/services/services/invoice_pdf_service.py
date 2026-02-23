"""
Invoice PDF Generation Service

This service handles the generation of PDF invoices using the company's custom template.
"""
import io
from datetime import datetime, timedelta
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class InvoicePDFService:
    """Service for generating PDF invoices"""

    @classmethod
    def generate_invoice_pdf(cls, request, company=None):
        """
        Generate a PDF invoice for a service request.

        Args:
            request: ServiceRequest model instance
            company: Company model instance (optional, will be fetched if not provided)

        Returns:
            bytes: PDF file content
        """
        from app.modules.company.models import Company

        if not company:
            company = Company.query.get(request.user.company_id) if request.user.company_id else None

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            textColor=colors.HexColor('#1f2937')
        ))

        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=5,
            textColor=colors.HexColor('#2563eb')
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#374151')
        ))

        styles.add(ParagraphStyle(
            name='Normal2',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            textColor=colors.HexColor('#4b5563')
        ))

        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#4b5563')
        ))

        styles.add(ParagraphStyle(
            name='FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280')
        ))

        # Build document content
        story = []

        # Header section with company info
        cls._add_header(story, styles, company, request)

        # Invoice details section
        cls._add_invoice_details(story, styles, request, company)

        # Line items section
        cls._add_line_items(story, styles, request, company)

        # Payment details section
        cls._add_payment_details(story, styles, company, request)

        # Notes and terms
        cls._add_notes(story, styles, company)

        # Footer
        cls._add_footer(story, styles, company)

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    @classmethod
    def _add_header(cls, story, styles, company, request):
        """Add header section with company info and INVOICE title"""
        # Company logo (check visibility setting)
        show_logo = company.invoice_show_logo if company and company.invoice_show_logo is not None else True
        if show_logo and company and company.logo_data:
            try:
                logo_buffer = io.BytesIO(company.logo_data)
                logo_img = Image(logo_buffer, width=40*mm, height=40*mm, kind='proportional')
                logo_img.hAlign = 'LEFT'
                story.append(logo_img)
                story.append(Spacer(1, 3*mm))
            except Exception as e:
                current_app.logger.warning(f"Failed to add logo to invoice: {e}")

        # Company name and info (check visibility setting)
        show_company_details = company.invoice_show_company_details if company and company.invoice_show_company_details is not None else True
        if company and show_company_details:
            story.append(Paragraph(company.name, styles['CompanyName']))
            if company.trading_name:
                story.append(Paragraph(f"Trading as: {company.trading_name}", styles['Normal2']))
            if company.abn:
                story.append(Paragraph(f"ABN: {company.abn}", styles['Normal2']))

            address_parts = []
            if company.address_line1:
                address_parts.append(company.address_line1)
            if company.address_line2:
                address_parts.append(company.address_line2)
            city_state = []
            if company.city:
                city_state.append(company.city)
            if company.state:
                city_state.append(company.state)
            if company.postcode:
                city_state.append(company.postcode)
            if city_state:
                address_parts.append(' '.join(city_state))
            if address_parts:
                story.append(Paragraph(' | '.join(address_parts), styles['Normal2']))

            contact_parts = []
            if company.phone:
                contact_parts.append(f"Phone: {company.phone}")
            if company.email:
                contact_parts.append(f"Email: {company.email}")
            if contact_parts:
                story.append(Paragraph(' | '.join(contact_parts), styles['Normal2']))
        elif not show_company_details:
            # Just show company name even if details are hidden
            if company:
                story.append(Paragraph(company.name, styles['CompanyName']))
            else:
                story.append(Paragraph("Accountant CRM", styles['CompanyName']))
        else:
            story.append(Paragraph("Accountant CRM", styles['CompanyName']))

        story.append(Spacer(1, 15*mm))

        # Large INVOICE title
        story.append(Paragraph("INVOICE", styles['InvoiceTitle']))

    @classmethod
    def _add_invoice_details(cls, story, styles, request, company):
        """Add invoice number, dates, and client info"""
        # Generate invoice number
        prefix = company.invoice_prefix if company and company.invoice_prefix else 'INV'
        invoice_number = f"{prefix}-{request.id:05d}"
        invoice_date = request.invoice_raised_at or datetime.utcnow()
        due_date = invoice_date + timedelta(days=14)

        # Check if client details should be shown
        show_client = company.invoice_show_client_details if company and company.invoice_show_client_details is not None else True

        if show_client:
            # Create two-column layout for invoice details and client info
            data = [
                [
                    Paragraph(f"<b>Invoice Number:</b> {invoice_number}", styles['Normal2']),
                    Paragraph("<b>Bill To:</b>", styles['Normal2'])
                ],
                [
                    Paragraph(f"<b>Date:</b> {invoice_date.strftime('%d %B %Y')}", styles['Normal2']),
                    Paragraph(f"{request.user.full_name}", styles['Normal2'])
                ],
                [
                    Paragraph(f"<b>Due Date:</b> {due_date.strftime('%d %B %Y')}", styles['Normal2']),
                    Paragraph(f"{request.user.email}", styles['Normal2'])
                ],
                [
                    Paragraph(f"<b>Status:</b> {'Paid' if request.invoice_paid else 'Unpaid'}", styles['Normal2']),
                    Paragraph(f"{request.user.address or ''}", styles['Normal2']) if request.user.address else Paragraph("", styles['Normal2'])
                ],
            ]
            table = Table(data, colWidths=[90*mm, 80*mm])
        else:
            # Only show invoice details without client info
            data = [
                [Paragraph(f"<b>Invoice Number:</b> {invoice_number}", styles['Normal2'])],
                [Paragraph(f"<b>Date:</b> {invoice_date.strftime('%d %B %Y')}", styles['Normal2'])],
                [Paragraph(f"<b>Due Date:</b> {due_date.strftime('%d %B %Y')}", styles['Normal2'])],
                [Paragraph(f"<b>Status:</b> {'Paid' if request.invoice_paid else 'Unpaid'}", styles['Normal2'])],
            ]
            table = Table(data, colWidths=[170*mm])

        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        story.append(table)
        story.append(Spacer(1, 10*mm))

    @classmethod
    def _add_line_items(cls, story, styles, request, company=None):
        """Add the invoice line items table"""
        story.append(Paragraph("Services", styles['SectionHeader']))

        # Check if tax should be shown
        show_tax = company.invoice_show_tax if company and company.invoice_show_tax is not None else True
        tax_label = company.tax_label if company and company.tax_label else 'GST'
        tax_rate = float(company.default_tax_rate) if company and company.default_tax_rate else 10.0

        # Table header and data
        data = [
            ['Description', 'Quantity', 'Unit Price', 'Amount']
        ]

        # Add main service as line item
        amount = request.invoice_amount or request.service.base_price or 0
        data.append([
            request.service.name,
            '1',
            f"${amount:.2f}",
            f"${amount:.2f}"
        ])

        # Add subtotal, tax, total
        data.append(['', '', 'Subtotal:', f"${amount:.2f}"])
        if show_tax and tax_rate > 0:
            tax_amount = amount * (tax_rate / 100)
            total = amount + tax_amount
            data.append(['', '', f'{tax_label} ({tax_rate:.0f}%):', f"${tax_amount:.2f}"])
            data.append(['', '', '', ''])
            data.append(['', '', f'Total (incl. {tax_label}):', f"${total:.2f}"])
        else:
            data.append(['', '', '', ''])
            data.append(['', '', 'Total:', f"${amount:.2f}"])

        table = Table(data, colWidths=[80*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # All cells
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),

            # Grid
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e5e7eb')),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor('#e5e7eb')),

            # Total row emphasis
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (-1, -1), 11),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.white),
            ('TOPPADDING', (2, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (2, -1), (-1, -1), 8),
        ]))

        story.append(table)
        story.append(Spacer(1, 10*mm))

    @classmethod
    def _add_payment_details(cls, story, styles, company, request):
        """Add payment details section"""
        show_payment_terms = company.invoice_show_payment_terms if company and company.invoice_show_payment_terms is not None else True
        show_bank_details = company.invoice_show_bank_details if company and company.invoice_show_bank_details is not None else True

        # Only show section if at least one item is visible
        if not show_payment_terms and not show_bank_details and not request.payment_link:
            return

        story.append(Paragraph("Payment Details", styles['SectionHeader']))

        # Payment terms
        if show_payment_terms:
            terms = company.invoice_payment_terms if company else 'Due within 14 days'
            story.append(Paragraph(f"<b>Terms:</b> {terms}", styles['Normal2']))
            story.append(Spacer(1, 3*mm))

        # Bank details
        if show_bank_details and company and company.invoice_bank_details:
            story.append(Paragraph("<b>Bank Transfer Details:</b>", styles['Normal2']))
            for line in company.invoice_bank_details.split('\n'):
                if line.strip():
                    story.append(Paragraph(line.strip(), styles['Normal2']))
            story.append(Spacer(1, 3*mm))

        # Online payment link (always show if available)
        if request.payment_link:
            story.append(Paragraph(f"<b>Pay Online:</b> {request.payment_link}", styles['Normal2']))

        story.append(Spacer(1, 5*mm))

    @classmethod
    def _add_notes(cls, story, styles, company):
        """Add notes and terms section"""
        show_notes = company.invoice_show_notes if company and company.invoice_show_notes is not None else True
        if show_notes and company and company.invoice_notes:
            story.append(Paragraph("Terms & Conditions", styles['SectionHeader']))
            for line in company.invoice_notes.split('\n'):
                if line.strip():
                    story.append(Paragraph(line.strip(), styles['Normal2']))
            story.append(Spacer(1, 5*mm))

    @classmethod
    def _add_footer(cls, story, styles, company):
        """Add footer section"""
        show_footer = company.invoice_show_footer if company and company.invoice_show_footer is not None else True
        if not show_footer:
            return

        story.append(Spacer(1, 10*mm))

        # Footer text
        if company and company.invoice_footer:
            story.append(Paragraph(company.invoice_footer, styles['FooterStyle']))
        else:
            story.append(Paragraph("Thank you for your business!", styles['FooterStyle']))

    @classmethod
    def get_invoice_filename(cls, request, company=None):
        """Generate filename for the invoice PDF"""
        from app.modules.company.models import Company

        if not company:
            company = Company.query.get(request.user.company_id) if request.user.company_id else None

        prefix = company.invoice_prefix if company and company.invoice_prefix else 'INV'
        invoice_number = f"{prefix}-{request.id:05d}"
        return f"{invoice_number}.pdf"

    @classmethod
    def generate_sample_invoice_pdf(cls, company=None, current_user=None):
        """
        Generate a sample PDF invoice for preview purposes (using dummy data).

        Args:
            company: Company model instance
            current_user: Current user for context

        Returns:
            bytes: PDF file content
        """
        # Create a mock request object with sample data
        class MockUser:
            full_name = "John Smith"
            email = "john.smith@example.com"
            address = "123 Sample Street, Sydney NSW 2000"

        class MockService:
            name = "Individual Tax Return"
            base_price = 350.00

        class MockRequest:
            id = 1
            invoice_amount = 350.00
            invoice_raised = True
            invoice_paid = False
            invoice_raised_at = datetime.utcnow()
            payment_link = "https://pay.example.com/sample"
            user = MockUser()
            service = MockService()

        return cls.generate_invoice_pdf(MockRequest(), company)
