# Deployment Guide

This guide covers deploying the Accountant CRM application to production.

## Prerequisites

- A Linux server (Ubuntu 22.04 recommended) with:
  - At least 2GB RAM
  - Docker and Docker Compose installed
  - Domain name pointed to the server (optional but recommended)

## Quick Deploy Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url> /opt/accountant-crm
cd /opt/accountant-crm
```

### 2. Configure Environment Variables

```bash
cp .env.production.example .env.production

# Edit the file with your values
nano .env.production
```

**Required variables:**
- `DB_PASSWORD` - Strong password for PostgreSQL
- `JWT_SECRET_KEY` - Generate with: `openssl rand -hex 32`

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Test the API
curl http://localhost/api/health

# Test the frontend
curl http://localhost/
```

## Database Management

### Restore from Backup

The database is automatically initialized with data from `backend/db_full_backup.sql` on first run.

### Create a New Backup

```bash
docker exec crm-db-prod pg_dump -U postgres -d accountant_crm > backup_$(date +%Y%m%d).sql
```

### Restore a Backup

```bash
docker exec -i crm-db-prod psql -U postgres -d accountant_crm < backup_file.sql
```

## SSL/HTTPS Setup (Recommended)

### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
apt install certbot

# Get certificate
certbot certonly --standalone -d your-domain.com

# Copy certificates
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Update nginx.conf to enable HTTPS (uncomment the SSL server block)
nano nginx/nginx.conf

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Option 2: Cloudflare (Easiest)

1. Add your domain to Cloudflare
2. Enable "Full" SSL mode
3. Cloudflare will handle SSL termination

## Cloud Platform Deployment Options

### Option A: DigitalOcean Droplet

1. Create a Droplet (2GB RAM, Ubuntu 22.04)
2. SSH into the server
3. Install Docker: `curl -fsSL https://get.docker.com | sh`
4. Install Docker Compose: `apt install docker-compose-plugin`
5. Follow the Quick Deploy Steps above

**Estimated cost:** ~$12-24/month

### Option B: AWS EC2

1. Launch an EC2 instance (t3.small or t3.medium)
2. Configure Security Group (allow ports 80, 443, 22)
3. SSH into the instance
4. Install Docker and follow Quick Deploy Steps

**Estimated cost:** ~$15-30/month

### Option C: Azure VM

1. Create a Virtual Machine (B2s or B2ms)
2. Configure NSG rules
3. SSH and follow Quick Deploy Steps

**Estimated cost:** ~$15-40/month

### Option D: Railway/Render (Managed)

For Railway:
1. Connect your GitHub repo
2. Add PostgreSQL service
3. Configure environment variables
4. Deploy

## Updating the Application

```bash
cd /opt/accountant-crm

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## Monitoring & Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Check container resource usage
docker stats
```

## Troubleshooting

### Database connection issues
```bash
# Check if database is healthy
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Check database logs
docker-compose -f docker-compose.prod.yml logs db
```

### Backend not starting
```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Frontend not loading
```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Check frontend build logs
docker-compose -f docker-compose.prod.yml logs frontend
```

## Security Checklist

- [ ] Change default database password
- [ ] Generate secure JWT secret
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set up automated backups
- [ ] Enable Cloudflare or similar CDN/DDoS protection
- [ ] Regular security updates: `apt update && apt upgrade`

## Default Login Credentials

After deployment, you can login with:

- **Super Admin:** `admin@example.com` / `Admin@123`
- **Practice Admin:** `practiceadmin@example.com` / `Practice@123`

**Important:** Change these passwords immediately after first login!
