"""
Test script to verify Zoho Mail configuration
Run this to test your email settings before using the contact form
"""

from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

print("=" * 60)
print("ZOHO MAIL CONFIGURATION TEST")
print("=" * 60)
print()

# Display current configuration
print("Current Configuration:")
print(f"  MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
print(f"  MAIL_PORT: {os.getenv('MAIL_PORT')}")
print(f"  MAIL_USE_TLS: {os.getenv('MAIL_USE_TLS')}")
print(f"  MAIL_USE_SSL: {os.getenv('MAIL_USE_SSL')}")
print(f"  MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"  MAIL_PASSWORD: {'*' * len(os.getenv('MAIL_PASSWORD', '')) if os.getenv('MAIL_PASSWORD') else 'NOT SET'}")
print(f"  MAIL_DEFAULT_SENDER: {os.getenv('MAIL_DEFAULT_SENDER')}")
print(f"  ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")
print()

# Check if required variables are set
required_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'ADMIN_EMAIL']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("❌ ERROR: Missing required environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print()
    print("Please configure these in your .env file")
    exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

mail = Mail(app)

print("Sending test email...")
print("-" * 60)

with app.app_context():
    try:
        # Create test message
        msg = Message(
            subject="✅ Test Email from Contact Form API",
            recipients=[os.getenv('ADMIN_EMAIL')],
            reply_to=os.getenv('MAIL_USERNAME')
        )

        # Plain text body
        msg.body = """
This is a test email from your Australian Super Source Contact Form API.

If you are receiving this email, your Zoho Mail configuration is working correctly!

Configuration Details:
- SMTP Server: {}
- Port: {}
- Authentication: Successful
- Sender: {}

You can now use the contact form on your website.

---
Australian Super Source
Contact Form API Test
        """.format(
            os.getenv('MAIL_SERVER'),
            os.getenv('MAIL_PORT'),
            os.getenv('MAIL_USERNAME')
        )

        # HTML body
        msg.html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e5e7eb; }}
        .success {{ background: #dcfce7; border-left: 4px solid #22c55e; padding: 15px; margin: 20px 0; }}
        .info {{ background: #f0f9ff; padding: 15px; margin: 20px 0; border-radius: 8px; }}
        .footer {{ background: #f3f4f6; padding: 20px; text-align: center; color: #6b7280; font-size: 12px; border-radius: 0 0 8px 8px; }}
        .label {{ font-weight: bold; color: #1e40af; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">✅ Configuration Test Successful</h1>
            <p style="margin: 10px 0 0 0;">Contact Form API</p>
        </div>
        <div class="content">
            <div class="success">
                <strong>Success!</strong> If you are receiving this email, your Zoho Mail configuration is working correctly.
            </div>

            <p>Your Australian Super Source Contact Form API is now ready to receive and send emails.</p>

            <div class="info">
                <div class="label">Configuration Details:</div>
                <ul>
                    <li><strong>SMTP Server:</strong> {}</li>
                    <li><strong>Port:</strong> {}</li>
                    <li><strong>Authentication:</strong> Successful</li>
                    <li><strong>Sender:</strong> {}</li>
                </ul>
            </div>

            <p>You can now:</p>
            <ul>
                <li>Test the contact form on your website</li>
                <li>Receive contact form submissions</li>
                <li>Send automatic confirmation emails to users</li>
            </ul>
        </div>
        <div class="footer">
            <p>Australian Super Source<br>
            Contact Form API Test Email</p>
        </div>
    </div>
</body>
</html>
        """.format(
            os.getenv('MAIL_SERVER'),
            os.getenv('MAIL_PORT'),
            os.getenv('MAIL_USERNAME')
        )

        # Send the email
        mail.send(msg)

        print("✅ SUCCESS!")
        print()
        print(f"Test email sent successfully to: {os.getenv('ADMIN_EMAIL')}")
        print()
        print("Please check your inbox (and spam folder) for the test email.")
        print()
        print("If you received the email, your Zoho Mail configuration is correct!")
        print("You can now run the Flask app and use the contact form.")
        print()

    except Exception as e:
        print("❌ FAILED!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Wrong email or password")
        print("  2. If 2FA is enabled, you MUST use App Password")
        print("  3. Wrong SMTP server for your region")
        print("  4. Firewall blocking port 587/465")
        print()
        print("Solutions:")
        print("  - Double-check your credentials in .env file")
        print("  - If you have 2FA: Generate App Password in Zoho Mail")
        print("  - For Australia, use: smtp.zoho.com.au")
        print("  - Try port 465 with SSL instead of 587 with TLS")
        print()
        print("See ZOHO_MAIL_SETUP.md for detailed troubleshooting")
        print()

print("=" * 60)
