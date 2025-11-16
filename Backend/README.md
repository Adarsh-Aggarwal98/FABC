# Australian Super Source - Contact Form API

Flask backend API for handling contact form submissions with email notifications.

## Features

- RESTful API endpoint for contact form submissions
- Email notifications to admin
- Automatic confirmation emails to users
- CORS enabled for frontend integration
- Input validation
- Professional HTML email templates
- Health check endpoints
- Error handling and logging

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd "C:\Users\aggar\Desktop\smsf website\aussupersource-website\FABC\Backend"
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` and configure your email settings:

```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=info@aussupersource.com.au
```

**For Gmail Users:**
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use the App Password in `MAIL_PASSWORD`

### 3. Run the Application

**Development Mode:**
```bash
python app.py
```

**Production Mode (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "contact-form-api",
  "timestamp": "2025-11-16T10:30:00",
  "mail_configured": true
}
```

### Contact Form Submission
```
POST /api/contact
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "0412345678",
  "subject": "SMSF Inquiry",
  "message": "I would like to learn more about SMSF services"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Thank you for your message. We will get back to you soon!"
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": ["Name is required", "Email is required"]
}
```

## Frontend Integration

Update your React contact form to send requests to the Flask API:

```javascript
const handleSubmit = async (formData) => {
  try {
    const response = await fetch('http://localhost:5000/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (response.ok) {
      console.log('Success:', data.message);
    } else {
      console.error('Error:', data.message);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_DEBUG` | Enable debug mode | `False` |
| `PORT` | Server port | `5000` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `MAIL_SERVER` | SMTP server address | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP server port | `587` |
| `MAIL_USE_TLS` | Use TLS encryption | `True` |
| `MAIL_USERNAME` | Email account username | - |
| `MAIL_PASSWORD` | Email account password/app password | - |
| `ADMIN_EMAIL` | Admin email for notifications | `info@aussupersource.com.au` |
| `SEND_CONFIRMATION_EMAIL` | Send confirmation to users | `True` |

## Testing

Test the API using curl:

```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"message\":\"Test message\"}"
```

Or use Postman/Insomnia to test the endpoints.

## Deployment

### Deploy on Render/Railway/Heroku

1. Push your code to GitHub
2. Connect your repository to the platform
3. Set environment variables in the platform dashboard
4. The platform will automatically install dependencies and run the app

### Deploy with Docker (optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t aussupersource-api .
docker run -p 5000:5000 --env-file .env aussupersource-api
```

## Troubleshooting

### Email not sending

1. Check that `MAIL_USERNAME` and `MAIL_PASSWORD` are correctly set
2. For Gmail, ensure you're using an App Password, not your regular password
3. Check the logs for error messages
4. Verify your email provider allows SMTP access

### CORS errors

1. Make sure `FRONTEND_URL` in `.env` matches your frontend URL
2. Check that the frontend is making requests to the correct backend URL
3. Ensure Flask-CORS is properly installed

### Port already in use

Change the `PORT` in `.env` to a different port number (e.g., 5001, 8000)

## Security Notes

- Never commit `.env` file to git
- Use App Passwords for email instead of account passwords
- Enable rate limiting in production
- Use HTTPS in production
- Validate and sanitize all inputs
- Keep dependencies updated

## Support

For issues or questions, contact the development team.
