# SMSF Website

Self-Managed Super Fund portal with document management and user authentication.

## Project Structure

```
smsf-website/
├── .env                    # Environment configuration
├── docker-compose.single.yml   # Single container deployment
├── Dockerfile.single       # Docker build file
├── FABC-Backend/           # Flask Backend
│   └── Backend/
│       ├── app.py          # Main Flask application
│       ├── models.py       # Database models
│       ├── zoho_service.py # Zoho WorkDrive integration
│       └── requirements.txt
└── FABC-FrontEnd/          # React Frontend
    ├── src/
    └── package.json
```

## Quick Start

### Docker (Single Container)

```bash
docker-compose -f docker-compose.single.yml up --build
```

Open: http://localhost:5000

### Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@aussupersource.com.au | Test@123 |
| Accountant | accountant@aussupersource.com.au | Test@123 |
| User | user@aussupersource.com.au | Test@123 |

## Features

- User authentication with email 2FA
- Role-based access (Admin, Accountant, User)
- Document upload/download via Zoho WorkDrive
- Admin user management and invitations
- Blog and ATO alerts management

## Environment Variables

See `.env` file for all configuration options.
