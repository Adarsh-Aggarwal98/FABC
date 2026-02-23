"""
EmailService - Service for Email and In-App Notification Handling
=============================================================

This module provides centralized notification handling with support
for multiple email providers and in-app notifications.

Email Provider Priority:
----------------------
1. SMTP2GO API (primary - reliable delivery)
2. MailerSend API (best for Docker/cloud deployments)
3. Company-specific SMTP configuration
4. System SMTP from environment variables
5. Microsoft Graph API (fallback)

Features:
--------
- Template-based email sending
- In-app notification management
- Bulk email with recipient filtering
- Company-specific SMTP configuration
- PDF invoice attachments

Usage:
-----
    # Send invite email
    EmailService.send_invite_email(user, temp_password)

    # Send OTP
    EmailService.send_otp_email(user, otp_code)

    # Create in-app notification
    Notification.create(user_id, title, message, type, link)

Author: CRM Development Team
"""

import logging
from flask import current_app
from sqlalchemy import and_, or_
from app.extensions import db
from app.modules.notifications.models.notification import Notification
from app.modules.notifications.clients.graph_client import GraphAPIClient
from app.modules.notifications.clients.smtp_client import SMTPClient, EmailClientFactory
from app.modules.notifications.clients.mailersend_client import MailerSendClient
from app.modules.notifications.clients.smtp2go_client import SMTP2GoClient
from app.modules.user.models import User, Role

# Configure module-level logger
logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for handling email notifications.

    Supports multiple email providers with automatic fallback:
    - SMTP2GO (primary - reliable delivery)
    - MailerSend
    - Company-specific SMTP
    - System SMTP
    - Microsoft Graph API
    """

    # ============== Email Templates ==============

    @staticmethod
    def _get_email_template(template_name, **kwargs):
        """Get email template by name"""
        templates = {
            'invite': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Welcome to Accountant CRM</h2>
                        <p>Hello{name_greeting},</p>
                        <p>You have been invited to join the Accountant CRM platform.</p>
                        <p>Here are your login credentials:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Temporary Password:</strong> {password}</p>
                        </div>
                        <p>Please login at <a href="{login_url}" style="color: #2563eb;">{login_url}</a> and complete your profile setup.</p>
                        <p style="color: #ef4444; font-weight: bold;">Important: Please change your password after first login.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">This is an automated email. Please do not reply.</p>
                    </div>
                </body>
                </html>
            """,
            'otp': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Login Verification Code</h2>
                        <p>Hello,</p>
                        <p>Your one-time verification code is:</p>
                        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb;">{otp}</span>
                        </div>
                        <p>This code will expire in 10 minutes.</p>
                        <p style="color: #ef4444;">If you did not request this code, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">This is an automated email. Please do not reply.</p>
                    </div>
                </body>
                </html>
            """,
            'password_reset': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Password Reset Request</h2>
                        <p>Hello,</p>
                        <p>We received a request to reset your password. Your reset code is:</p>
                        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb;">{otp}</span>
                        </div>
                        <p>This code will expire in 10 minutes.</p>
                        <p style="color: #ef4444;">If you did not request a password reset, please ignore this email and your password will remain unchanged.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">This is an automated email. Please do not reply.</p>
                    </div>
                </body>
                </html>
            """,
            'new_request': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">New Service Request</h2>
                        <p>Hello,</p>
                        <p>A new service request has been submitted:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Client:</strong> {client_name}</p>
                            <p><strong>Service:</strong> {service_name}</p>
                            <p><strong>Request ID:</strong> {request_id}</p>
                        </div>
                        <p>Please login to the dashboard to review and assign this request.</p>
                        <a href="{dashboard_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">View Dashboard</a>
                    </div>
                </body>
                </html>
            """,
            'request_assigned': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">New Request Assigned</h2>
                        <p>Hello {accountant_name},</p>
                        <p>A new service request has been assigned to you:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Client:</strong> {client_name}</p>
                            <p><strong>Service:</strong> {service_name}</p>
                            <p><strong>Request ID:</strong> {request_id}</p>
                        </div>
                        <a href="{request_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">View Request</a>
                    </div>
                </body>
                </html>
            """,
            'query_raised': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #f59e0b;">Query on Your Service Request</h2>
                        <p>Hello {client_name},</p>
                        <p>The accountant has raised a query on your service request:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Service:</strong> {service_name}</p>
                            <p><strong>Query:</strong> {query_message}</p>
                        </div>
                        <p>Please login to respond to this query.</p>
                        <a href="{request_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">Respond to Query</a>
                    </div>
                </body>
                </html>
            """,
            'invoice_raised': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Invoice for Your Service</h2>
                        <p>Hello {client_name},</p>
                        <p>An invoice has been raised for your service request:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Service:</strong> {service_name}</p>
                            <p><strong>Amount:</strong> {amount}</p>
                        </div>
                        <p>Please click the button below to make the payment:</p>
                        <a href="{payment_link}" style="display: inline-block; background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">Pay Now</a>
                    </div>
                </body>
                </html>
            """,
            'practice_owner_welcome': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Welcome to Accountant CRM - Practice Owner</h2>
                        <p>Hello {owner_name},</p>
                        <p>Congratulations! Your practice <strong>{company_name}</strong> has been set up on Accountant CRM.</p>
                        <p>As the Practice Owner, you have administrative access to manage your team and clients.</p>
                        <p>Here are your login credentials:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Temporary Password:</strong> {password}</p>
                        </div>
                        <p>What you can do as Practice Owner:</p>
                        <ul>
                            <li>Add and manage accountants in your team</li>
                            <li>Invite clients to the platform</li>
                            <li>Assign service requests to accountants</li>
                            <li>Track all requests and invoices</li>
                            <li>Customize your practice settings</li>
                        </ul>
                        <a href="{login_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">Login to Dashboard</a>
                        <p style="color: #ef4444; font-weight: bold; margin-top: 20px;">Important: Please change your password after first login.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">This is an automated email. Please do not reply.</p>
                    </div>
                </body>
                </html>
            """,
            'user_invitation': """
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">You've Been Invited to {company_name}</h2>
                        <p>Hello {user_name},</p>
                        <p>You have been invited to join <strong>{company_name}</strong> on Accountant CRM as {role_display}.</p>
                        <p>Here are your login credentials:</p>
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Temporary Password:</strong> {password}</p>
                        </div>
                        <a href="{login_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">Login Now</a>
                        <p style="color: #ef4444; font-weight: bold; margin-top: 20px;">Important: Please change your password after first login.</p>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                        <p style="color: #6b7280; font-size: 12px;">This is an automated email. Please do not reply.</p>
                    </div>
                </body>
                </html>
            """,
        }

        template = templates.get(template_name, '')
        return template.format(**kwargs)

    # ============== Email Client Helper ==============

    @classmethod
    def _get_email_client(cls, company_id=None):
        """
        Get the appropriate email client.
        Priority: SMTP2GO > MailerSend > Graph API > Company SMTP > System SMTP

        Args:
            company_id: Optional company ID for company-specific SMTP

        Returns:
            Email client (SMTP2GoClient, MailerSendClient, GraphAPIClient, or SMTPClient)
        """
        current_app.logger.info(f'[EmailClient] Getting email client for company_id: {company_id}')

        # Try SMTP2GO first (primary - reliable delivery)
        smtp2go_api_key = current_app.config.get('SMTP2GO_API_KEY')
        smtp2go_sender = current_app.config.get('SMTP2GO_SENDER_EMAIL')

        if smtp2go_api_key and smtp2go_sender:
            current_app.logger.info(f'[EmailClient] SMTP2GO configured, sender: {smtp2go_sender}')
            client = SMTP2GoClient(
                api_key=smtp2go_api_key,
                sender_email=smtp2go_sender,
                sender_name=current_app.config.get('SMTP2GO_SENDER_NAME', 'Accountant CRM')
            )
            if client.is_configured():
                current_app.logger.info(f'[EmailClient] Using SMTP2GO API')
                return client

        # Try MailerSend second (works best with Docker/cloud)
        mailersend_api_key = current_app.config.get('MAILERSEND_API_KEY')
        mailersend_sender = current_app.config.get('MAILERSEND_SENDER_EMAIL')

        if mailersend_api_key and mailersend_sender:
            current_app.logger.info(f'[EmailClient] MailerSend configured, sender: {mailersend_sender}')
            client = MailerSendClient(
                api_key=mailersend_api_key,
                sender_email=mailersend_sender,
                sender_name=current_app.config.get('MAILERSEND_SENDER_NAME', 'Accountant CRM')
            )
            if client.is_configured():
                current_app.logger.info(f'[EmailClient] Using MAILERSEND API')
                return client

        # If company_id provided, try company-specific config
        if company_id:
            current_app.logger.info(f'[EmailClient] Checking company-specific SMTP config...')
            try:
                client, client_type = EmailClientFactory.get_client_for_company(company_id)
                if client:
                    if hasattr(client, 'smtp_host'):
                        current_app.logger.info(f'[EmailClient] Using COMPANY SMTP: host={client.smtp_host}, port={client.smtp_port}, username={client.smtp_username}')
                    else:
                        current_app.logger.info(f'[EmailClient] Using company {client_type} client')
                    return client
                else:
                    current_app.logger.info(f'[EmailClient] No company SMTP config found or not enabled')
            except Exception as e:
                current_app.logger.error(f'[EmailClient] Error getting company config: {str(e)}')

        # Try system SMTP from environment variables
        current_app.logger.info(f'[EmailClient] Checking system SMTP from env vars...')
        current_app.logger.info(f'[EmailClient] SYSTEM_SMTP_ENABLED={current_app.config.get("SYSTEM_SMTP_ENABLED")}')

        if current_app.config.get('SYSTEM_SMTP_ENABLED'):
            smtp_config = {
                'smtp_host': current_app.config.get('SYSTEM_SMTP_HOST'),
                'smtp_port': current_app.config.get('SYSTEM_SMTP_PORT', 587),
                'smtp_username': current_app.config.get('SYSTEM_SMTP_USERNAME'),
                'smtp_password': current_app.config.get('SYSTEM_SMTP_PASSWORD'),
                'smtp_use_tls': current_app.config.get('SYSTEM_SMTP_USE_TLS', True),
                'smtp_use_ssl': current_app.config.get('SYSTEM_SMTP_USE_SSL', False),
                'sender_email': current_app.config.get('SYSTEM_SMTP_SENDER_EMAIL'),
                'sender_name': current_app.config.get('SYSTEM_SMTP_SENDER_NAME', 'Accountant CRM'),
            }
            current_app.logger.info(f'[EmailClient] System SMTP config: host={smtp_config["smtp_host"]}, port={smtp_config["smtp_port"]}, username={smtp_config["smtp_username"]}, sender={smtp_config["sender_email"]}')

            client = SMTPClient(smtp_config)
            if client.is_configured():
                current_app.logger.info(f'[EmailClient] Using SYSTEM SMTP (env vars): {smtp_config["smtp_host"]}:{smtp_config["smtp_port"]}')
                return client
            else:
                current_app.logger.warning(f'[EmailClient] System SMTP not fully configured')

        # No email client configured - log warning
        current_app.logger.warning('[EmailClient] No email client configured - emails will not be sent')
        return None

    # ============== Email Sending Methods ==============

    @classmethod
    def send_invite_email(cls, user, password):
        """Send invitation email to new user"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        name_greeting = f" {user.first_name}" if user.first_name else ""

        body = cls._get_email_template(
            'invite',
            name_greeting=name_greeting,
            email=user.email,
            password=password,
            login_url=f"{frontend_url}/login"
        )

        try:
            client = cls._get_email_client(getattr(user, 'company_id', None))
            if client:
                client.send_email(user.email, 'Welcome to Accountant CRM', body)
            else:
                current_app.logger.warning(f'No email client configured - invite email to {user.email} not sent')
        except Exception as e:
            current_app.logger.error(f'Failed to send invite email: {str(e)}')

    @classmethod
    def send_otp_email(cls, user, otp_code):
        """Send OTP email for 2FA"""
        body = cls._get_email_template('otp', otp=otp_code)

        try:
            client = cls._get_email_client(getattr(user, 'company_id', None))
            if client:
                result = client.send_email(user.email, 'Your Login Verification Code', body)
                if isinstance(result, dict) and not result.get('success', True):
                    current_app.logger.error(f"OTP email failed: {result.get('error')}")
            else:
                current_app.logger.warning(f'No email client configured - OTP email to {user.email} not sent. OTP: {otp_code}')
        except Exception as e:
            current_app.logger.error(f'Failed to send OTP email: {str(e)}')

    @classmethod
    def send_password_reset_email(cls, user, otp_code):
        """Send password reset OTP email"""
        body = cls._get_email_template('password_reset', otp=otp_code)

        try:
            client = cls._get_email_client(getattr(user, 'company_id', None))
            if client:
                client.send_email(user.email, 'Password Reset Request', body)
            else:
                current_app.logger.warning(f'No email client configured - password reset email to {user.email} not sent. OTP: {otp_code}')
        except Exception as e:
            current_app.logger.error(f'Failed to send password reset email: {str(e)}')

    @classmethod
    def send_new_request_notification(cls, request, admins):
        """Send notification to admins about new request"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

        body = cls._get_email_template(
            'new_request',
            client_name=request.user.full_name,
            service_name=request.service.name,
            request_id=request.id,
            dashboard_url=f"{frontend_url}/dashboard"
        )

        # Send email to all admins
        admin_emails = [admin.email for admin in admins]
        try:
            # Get company_id from request
            company_id = getattr(request, 'company_id', None)
            client = cls._get_email_client(company_id)
            if client:
                if hasattr(client, 'send_email_to_multiple'):
                    client.send_email_to_multiple(admin_emails, 'New Service Request', body)
                else:
                    # SMTP client doesn't have send_email_to_multiple, send one by one
                    for email in admin_emails:
                        client.send_email(email, 'New Service Request', body)
            else:
                current_app.logger.warning('No email client configured - new request notification not sent')
        except Exception as e:
            current_app.logger.error(f'Failed to send new request notification: {str(e)}')

        # Create in-app notifications
        for admin in admins:
            Notification.create(
                user_id=admin.id,
                title='New Service Request',
                message=f'{request.user.full_name} submitted a request for {request.service.name}',
                notification_type=Notification.TYPE_INFO,
                link=f'/requests/{request.id}'
            )

    @classmethod
    def send_assignment_notification(cls, request):
        """Send notification to accountant about assignment"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        accountant = request.assigned_accountant

        body = cls._get_email_template(
            'request_assigned',
            accountant_name=accountant.full_name,
            client_name=request.user.full_name,
            service_name=request.service.name,
            request_id=request.id,
            request_url=f"{frontend_url}/requests/{request.id}"
        )

        try:
            company_id = getattr(request, 'company_id', None)
            client = cls._get_email_client(company_id)
            if client:
                client.send_email(accountant.email, 'New Request Assigned', body)
            else:
                current_app.logger.warning('No email client configured - assignment notification not sent')
        except Exception as e:
            current_app.logger.error(f'Failed to send assignment notification: {str(e)}')

        # Create in-app notification
        Notification.create(
            user_id=accountant.id,
            title='New Request Assigned',
            message=f'You have been assigned to handle {request.service.name} for {request.user.full_name}',
            notification_type=Notification.TYPE_INFO,
            link=f'/requests/{request.id}'
        )

    @classmethod
    def send_query_notification(cls, request, query_message):
        """Send notification to user about query"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        user = request.user

        body = cls._get_email_template(
            'query_raised',
            client_name=user.full_name,
            service_name=request.service.name,
            query_message=query_message,
            request_url=f"{frontend_url}/requests/{request.id}"
        )

        try:
            company_id = getattr(request, 'company_id', None)
            client = cls._get_email_client(company_id)
            if client:
                client.send_email(user.email, 'Query on Your Service Request', body)
            else:
                current_app.logger.warning('No email client configured - query notification not sent')
        except Exception as e:
            current_app.logger.error(f'Failed to send query notification: {str(e)}')

        # Create in-app notification
        Notification.create(
            user_id=user.id,
            title='Query on Your Request',
            message=f'The accountant has a question about your {request.service.name} request',
            notification_type=Notification.TYPE_WARNING,
            link=f'/requests/{request.id}'
        )

    @classmethod
    def send_user_response_notification(cls, request, recipients, message):
        """Send notification to admin and assigned accountant when user responds to a query"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        user = request.user

        # Create email body — escape user-supplied content to prevent HTML injection
        import html as html_lib
        safe_name = html_lib.escape(user.full_name or '')
        safe_service = html_lib.escape(request.service.name or '')
        safe_message = html_lib.escape(message[:200]) + ('...' if len(message) > 200 else '')

        body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Client Response on Service Request</h2>
                    <p>Hello,</p>
                    <p><strong>{safe_name}</strong> has responded to the query on their service request:</p>
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Service:</strong> {safe_service}</p>
                        <p><strong>Response:</strong> {safe_message}</p>
                    </div>
                    <p>Please review and continue processing the request.</p>
                    <a href="{frontend_url}/requests/{request.id}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 10px;">View Request</a>
                </div>
            </body>
            </html>
        """

        # Send email to recipients
        recipient_emails = [r.email for r in recipients]
        try:
            company_id = getattr(request, 'company_id', None) or (user.company_id if user else None)
            client = cls._get_email_client(company_id)
            if client:
                for email in recipient_emails:
                    client.send_email(email, 'Client Response on Service Request', body)
            else:
                current_app.logger.warning('No email client configured - user response notification not sent')
        except Exception as e:
            current_app.logger.error(f'Failed to send user response notification email: {str(e)}')

        # Create in-app notifications
        for recipient in recipients:
            Notification.create(
                user_id=recipient.id,
                title='Client Response Received',
                message=f'{user.full_name} has responded to the query on {request.service.name}',
                notification_type=Notification.TYPE_INFO,
                link=f'/requests/{request.id}'
            )

    @classmethod
    def send_invoice_notification(cls, request, attach_pdf=True):
        """Send invoice notification to user with company's custom template and optional PDF attachment"""
        from app.modules.company.models import Company
        from app.modules.services.invoice_service import InvoicePDFService

        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        user = request.user
        company = Company.query.get(user.company_id) if user.company_id else None

        # Generate invoice number for subject
        prefix = company.invoice_prefix if company and company.invoice_prefix else 'INV'
        invoice_number = f"{prefix}-{request.id:05d}"

        # Build email subject - use company's custom subject if available
        default_subject = f'Invoice #{invoice_number} for Your Service'
        if company and company.invoice_email_subject:
            subject = company.invoice_email_subject.replace('{company_name}', company.name or '')
            subject = subject.replace('{invoice_number}', invoice_number)
        else:
            subject = default_subject

        # Build email body - use company's custom body if available
        if company and company.invoice_email_body:
            # Use custom template with variable replacements
            body = company.invoice_email_body
            body = body.replace('{client_name}', user.full_name or user.email)
            body = body.replace('{service_name}', request.service.name)
            body = body.replace('{amount}', f"${request.invoice_amount:.2f}" if request.invoice_amount else "N/A")
            body = body.replace('{invoice_number}', invoice_number)
            body = body.replace('{payment_link}', request.payment_link or f"{frontend_url}/requests/{request.id}")
            body = body.replace('{company_name}', company.name or '')
            body = body.replace('{payment_terms}', company.invoice_payment_terms or 'Due within 14 days')
            body = body.replace('{bank_details}', company.invoice_bank_details or '')
            body = body.replace('{invoice_notes}', company.invoice_notes or '')
            body = body.replace('{invoice_footer}', company.invoice_footer or '')

            # Wrap in HTML if not already
            if not body.strip().startswith('<'):
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        {body.replace(chr(10), '<br>')}
                    </div>
                </body>
                </html>
                """
        else:
            # Use default template
            body = cls._get_email_template(
                'invoice_raised',
                client_name=user.full_name,
                service_name=request.service.name,
                amount=f"${request.invoice_amount:.2f}" if request.invoice_amount else "N/A",
                payment_link=request.payment_link or f"{frontend_url}/requests/{request.id}"
            )

        try:
            company_id = getattr(user, 'company_id', None)
            client = cls._get_email_client(company_id)

            if not client:
                current_app.logger.warning('No email client configured - invoice notification not sent')
            elif attach_pdf:
                # Generate PDF invoice
                try:
                    pdf_bytes = InvoicePDFService.generate_invoice_pdf(request, company)
                    pdf_filename = InvoicePDFService.get_invoice_filename(request, company)

                    # Send email with PDF attachment
                    client.send_email_with_attachment(
                        to_email=user.email,
                        subject=subject,
                        body=body,
                        attachment_bytes=pdf_bytes,
                        attachment_name=pdf_filename,
                        attachment_content_type='application/pdf'
                    )
                except Exception as pdf_error:
                    current_app.logger.error(f'Failed to generate invoice PDF, sending without attachment: {str(pdf_error)}')
                    client.send_email(user.email, subject, body)
            else:
                client.send_email(user.email, subject, body)

        except Exception as e:
            current_app.logger.error(f'Failed to send invoice notification: {str(e)}')

        # Create in-app notification
        Notification.create(
            user_id=user.id,
            title='Invoice Ready',
            message=f'Invoice #{invoice_number} for {request.service.name} is ready for payment - ${request.invoice_amount:.2f}' if request.invoice_amount else f'Invoice for {request.service.name} is ready',
            notification_type=Notification.TYPE_INFO,
            link=f'/requests/{request.id}'
        )

    @classmethod
    def send_practice_owner_welcome_email(cls, to_email, owner_name, company_name, temp_password):
        """Send welcome email to new practice owner"""
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

        body = cls._get_email_template(
            'practice_owner_welcome',
            owner_name=owner_name,
            company_name=company_name,
            email=to_email,
            password=temp_password,
            login_url=f"{frontend_url}/login"
        )

        try:
            client = cls._get_email_client()
            if client:
                client.send_email(to_email, f'Welcome to {company_name} - Practice Owner Account', body)
            else:
                current_app.logger.warning(f'No email client configured - practice owner welcome email not sent')
                raise Exception('No email client configured')
        except Exception as e:
            current_app.logger.error(f'Failed to send practice owner welcome email: {str(e)}')
            raise

    @classmethod
    def send_user_invitation_email(cls, to_email, user_name, company_name, temp_password, role, company_id=None):
        """Send invitation email to new user (accountant or client)

        Uses company's configured SMTP if is_enabled=True, otherwise falls back to system SMTP.
        """
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

        role_display = 'an Accountant' if role == 'accountant' else 'a Client'

        body = cls._get_email_template(
            'user_invitation',
            user_name=user_name,
            company_name=company_name,
            role_display=role_display,
            email=to_email,
            password=temp_password,
            login_url=f"{frontend_url}/login"
        )

        try:
            # Use company SMTP if enabled, otherwise fall back to system SMTP
            client = cls._get_email_client(company_id)
            if client:
                client.send_email(to_email, f'Invitation to join {company_name}', body)
            else:
                current_app.logger.warning(f'No email client configured - user invitation email not sent')
                raise Exception('No email client configured')
        except Exception as e:
            current_app.logger.error(f'Failed to send user invitation email: {str(e)}')
            raise

    @classmethod
    def send_email(cls, to_email, subject, body_html, company_id=None):
        """Send a generic email with custom content"""
        try:
            client = cls._get_email_client(company_id)
            if client:
                client.send_email(to_email, subject, body_html)
            else:
                current_app.logger.warning(f'No email client configured - email to {to_email} not sent')
                raise Exception('No email client configured')
        except Exception as e:
            current_app.logger.error(f'Failed to send email to {to_email}: {str(e)}')
            raise

