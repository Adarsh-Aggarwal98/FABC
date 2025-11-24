from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# CORS configuration - allow requests from all origins
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL', 'sam@aussupersource.com.au')

mail = Mail(app)

# Validation helper
def validate_contact_form(data):
    """Validate contact form data"""
    required_fields = ['name', 'email', 'message']
    errors = []

    for field in required_fields:
        if not data.get(field) or not data.get(field).strip():
            errors.append(f"{field.capitalize()} is required")

    # Basic email validation
    email = data.get('email', '')
    if email and '@' not in email:
        errors.append("Invalid email format")

    return errors

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Australian Super Source Contact API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'contact-form-api',
        'timestamp': datetime.now().isoformat(),
        'mail_configured': bool(app.config['MAIL_USERNAME'])
    })

@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        # Validate form data
        errors = validate_contact_form(data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': errors
            }), 400

        # Extract form fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        subject = data.get('subject', 'Contact Form Submission').strip()
        message = data.get('message', '').strip()

        # Log the submission
        logger.info(f"Contact form submission from: {name} ({email})")

        # Create email message
        try:
            # Email to admin
            admin_msg = Message(
                subject=f"[Contact Form] {subject}",
                recipients=[app.config['ADMIN_EMAIL']],
                reply_to=email
            )

            admin_msg.body = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject}

Message:
{message}

---
Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            admin_msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .field {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #1e40af; }}
        .value {{ margin-top: 5px; }}
        .message-box {{ background: white; padding: 15px; border-left: 4px solid #3b82f6; margin-top: 10px; }}
        .footer {{ background: #f3f4f6; padding: 15px; text-align: center; color: #6b7280; font-size: 12px; border-radius: 0 0 8px 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">New Contact Form Submission</h2>
        </div>
        <div class="content">
            <div class="field">
                <div class="label">Name:</div>
                <div class="value">{name}</div>
            </div>
            <div class="field">
                <div class="label">Email:</div>
                <div class="value"><a href="mailto:{email}">{email}</a></div>
            </div>
            {f'<div class="field"><div class="label">Phone:</div><div class="value">{phone}</div></div>' if phone else ''}
            <div class="field">
                <div class="label">Subject:</div>
                <div class="value">{subject}</div>
            </div>
            <div class="field">
                <div class="label">Message:</div>
                <div class="message-box">{message}</div>
            </div>
        </div>
        <div class="footer">
            Submitted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
            """

            mail.send(admin_msg)

            # Confirmation email to user
            if os.getenv('SEND_CONFIRMATION_EMAIL', 'True') == 'True':
                user_msg = Message(
                    subject="Thank you for contacting Australian Super Source",
                    recipients=[email]
                )

                user_msg.body = f"""
Dear {name},

Thank you for contacting Australian Super Source. We have received your message and will get back to you as soon as possible.

Your message:
{message}

Best regards,
Australian Super Source Team
                """

                user_msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e5e7eb; }}
        .message-box {{ background: #f9fafb; padding: 20px; border-left: 4px solid #3b82f6; margin: 20px 0; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; color: #6b7280; border-radius: 0 0 8px 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">Australian Super Source</h1>
            <p style="margin: 10px 0 0 0;">SMSF Specialists</p>
        </div>
        <div class="content">
            <h2>Thank You for Contacting Us</h2>
            <p>Dear {name},</p>
            <p>Thank you for reaching out to Australian Super Source. We have received your message and will respond as soon as possible.</p>
            <div class="message-box">
                <strong>Your message:</strong><br><br>
                {message}
            </div>
            <p>Our team of SMSF specialists will review your inquiry and get back to you shortly.</p>
            <p>Best regards,<br>
            <strong>Australian Super Source Team</strong></p>
        </div>
        <div class="footer">
            <p>Australian Super Source Pty Ltd<br>
            Email: info@aussupersource.com.au<br>
            Website: www.aussupersource.com.au</p>
        </div>
    </div>
</body>
</html>
                """

                mail.send(user_msg)

            logger.info(f"Email sent successfully for contact from {email}")

            return jsonify({
                'status': 'success',
                'message': 'Thank you for your message. We will get back to you soon!'
            }), 200

        except Exception as email_error:
            logger.error(f"Email sending failed: {str(email_error)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to send email. Please try again later or contact us directly.',
                'details': str(email_error) if app.debug else None
            }), 500

    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred processing your request',
            'details': str(e) if app.debug else None
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'

    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Admin email: {app.config['ADMIN_EMAIL']}")

    app.run(
        host='0.0.0.0',
        port='5000',
        debug=debug
    )
