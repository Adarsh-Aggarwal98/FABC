"""
Custom Test Script - Send email to specific address for testing
This script sends a test email to aggarwal.adarsh98@gmail.com
"""

from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Test email recipient
TEST_EMAIL = "aggarwal.adarsh98@gmail.com"

print("=" * 60)
print("CUSTOM EMAIL TEST - Send to Gmail")
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
print(f"  TEST RECIPIENT: {TEST_EMAIL}")
print()

# Check if required variables are set
required_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
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

print("Sending test email to Gmail...")
print("-" * 60)

with app.app_context():
    try:
        # Create test message
        msg = Message(
            subject="✅ AusSuperSource Contact Form - Test Email",
            recipients=[TEST_EMAIL],
            reply_to=os.getenv('MAIL_USERNAME')
        )

        # Plain text body
        msg.body = f"""
Hello!

This is a test email from Australian Super Source Contact Form API.

If you are receiving this email in your Gmail inbox, your Zoho Mail configuration is working perfectly!

Configuration Details:
- SMTP Server: {os.getenv('MAIL_SERVER')}
- Port: {os.getenv('MAIL_PORT')}
- Sender Email: {os.getenv('MAIL_USERNAME')}
- Authentication: Successful ✅

What this means:
✓ Your Zoho Mail SMTP is configured correctly
✓ Your credentials are valid
✓ Emails can be sent successfully
✓ Contact form is ready to use

Next Steps:
1. Test the contact form on your website
2. Submit a test inquiry
3. Check if emails arrive to the admin email

---
Australian Super Source
Contact Form API Test
Sent to: {TEST_EMAIL}
        """

        # HTML body
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 14px; }}
        .content {{ padding: 40px 30px; }}
        .success-badge {{ background: #dcfce7; border-left: 4px solid #22c55e; padding: 20px; margin: 0 0 30px 0; border-radius: 4px; }}
        .success-badge h2 {{ margin: 0 0 10px 0; color: #166534; font-size: 20px; }}
        .success-badge p {{ margin: 0; color: #166534; }}
        .info-box {{ background: #f0f9ff; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #bae6fd; }}
        .info-box h3 {{ margin: 0 0 15px 0; color: #0c4a6e; font-size: 16px; }}
        .info-list {{ list-style: none; padding: 0; margin: 0; }}
        .info-list li {{ padding: 8px 0; border-bottom: 1px solid #e0f2fe; }}
        .info-list li:last-child {{ border-bottom: none; }}
        .info-list strong {{ color: #0369a1; display: inline-block; width: 140px; }}
        .checklist {{ background: #fefce8; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #facc15; }}
        .checklist h3 {{ margin: 0 0 15px 0; color: #854d0e; }}
        .checklist ul {{ margin: 0; padding-left: 20px; }}
        .checklist li {{ padding: 5px 0; color: #713f12; }}
        .next-steps {{ background: #eff6ff; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .next-steps h3 {{ margin: 0 0 15px 0; color: #1e40af; }}
        .next-steps ol {{ margin: 0; padding-left: 20px; }}
        .next-steps li {{ padding: 5px 0; color: #1e3a8a; }}
        .footer {{ background: #f8fafc; padding: 30px; text-align: center; color: #64748b; font-size: 14px; border-top: 1px solid #e2e8f0; }}
        .footer strong {{ color: #334155; display: block; margin-bottom: 5px; }}
        .checkmark {{ color: #22c55e; font-size: 20px; margin-right: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="checkmark">✅</span> Test Email Successful!</h1>
            <p>Australian Super Source - Contact Form API</p>
        </div>

        <div class="content">
            <div class="success-badge">
                <h2>🎉 Congratulations!</h2>
                <p>Your Zoho Mail configuration is working perfectly. This email was sent successfully from your backend server.</p>
            </div>

            <p>Hello,</p>
            <p>If you're reading this in your Gmail inbox, it means your <strong>Australian Super Source Contact Form</strong> email system is configured correctly and ready to use!</p>

            <div class="info-box">
                <h3>📧 Email Configuration Status</h3>
                <ul class="info-list">
                    <li><strong>SMTP Server:</strong> {os.getenv('MAIL_SERVER')}</li>
                    <li><strong>Port:</strong> {os.getenv('MAIL_PORT')}</li>
                    <li><strong>Sender Email:</strong> {os.getenv('MAIL_USERNAME')}</li>
                    <li><strong>Authentication:</strong> <span style="color: #22c55e;">✅ Successful</span></li>
                    <li><strong>Recipient:</strong> {TEST_EMAIL}</li>
                </ul>
            </div>

            <div class="checklist">
                <h3>✓ What's Working</h3>
                <ul>
                    <li>✅ Zoho Mail SMTP connection established</li>
                    <li>✅ Email credentials validated</li>
                    <li>✅ Emails can be sent successfully</li>
                    <li>✅ Email delivery to Gmail working</li>
                    <li>✅ Contact form backend ready</li>
                </ul>
            </div>

            <div class="next-steps">
                <h3>🚀 Next Steps</h3>
                <ol>
                    <li>Test the contact form on your website</li>
                    <li>Submit a test inquiry through the form</li>
                    <li>Check if emails arrive at the admin email (sam@aussupersource.com.au)</li>
                    <li>Verify user confirmation emails are being sent</li>
                    <li>Deploy to production when ready</li>
                </ol>
            </div>

            <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                <strong>Need help?</strong> Check the documentation files in your Backend folder:
            </p>
            <ul style="color: #6b7280; font-size: 14px;">
                <li>QUICK_START_ZOHO.md - Quick setup guide</li>
                <li>ZOHO_MAIL_SETUP.md - Detailed configuration</li>
                <li>EMAIL_CONFIGURATION_EXPLAINED.md - Email flow details</li>
            </ul>
        </div>

        <div class="footer">
            <strong>Australian Super Source</strong>
            Contact Form API Test Email<br>
            Sent from: {os.getenv('MAIL_USERNAME')}<br>
            Sent to: {TEST_EMAIL}
        </div>
    </div>
</body>
</html>
        """

        # Send the email
        mail.send(msg)

        print("✅ SUCCESS!")
        print()
        print(f"Test email sent successfully to: {TEST_EMAIL}")
        print()
        print("Please check your Gmail inbox for the test email.")
        print("Don't forget to check the spam/junk folder if you don't see it.")
        print()
        print("If you received the email, your Zoho Mail configuration is working perfectly!")
        print("Your contact form is ready to use.")
        print()

    except Exception as e:
        print("❌ FAILED!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Wrong email or password in .env file")
        print("  2. If 2FA is enabled on Zoho, you MUST use App Password")
        print("  3. Wrong SMTP server for your region")
        print("  4. Firewall blocking port 587/465")
        print("  5. Invalid Zoho account credentials")
        print()
        print("Solutions:")
        print("  - Double-check MAIL_USERNAME and MAIL_PASSWORD in .env")
        print("  - If 2FA enabled: Generate App Password in Zoho Mail settings")
        print("  - For Australia: Use smtp.zoho.com.au as MAIL_SERVER")
        print("  - Try port 465 with SSL: MAIL_PORT=465, MAIL_USE_SSL=True")
        print()
        print("See ZOHO_MAIL_SETUP.md for detailed troubleshooting")
        print()

print("=" * 60)
