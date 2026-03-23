# Production Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Configuration

Create a production `.env` file:

```bash
# Generate a new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Production .env
SECRET_KEY=your-generated-secret-key-50-chars-minimum
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Production Database
DB_HOST=your-production-db-host
DB_NAME=academic_erp_prod
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
DB_PORT=3306
```

### 2. Security Check

Run Django's deployment security check:

```bash
python manage.py check --deploy
```

All warnings should be resolved in production with `DEBUG=False`.

### 3. Database Setup

```sql
-- Create production database
CREATE DATABASE academic_erp_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create dedicated user
CREATE USER 'erp_prod'@'%' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON academic_erp_prod.* TO 'erp_prod'@'%';
FLUSH PRIVILEGES;
```

### 4. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 5. Database Migration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Web Server Configuration

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    location /static/ {
        alias /path/to/your/project/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Gunicorn Configuration

Install Gunicorn:
```bash
pip install gunicorn
```

Create `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

Run with Gunicorn:
```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

## Systemd Service (Linux)

Create `/etc/systemd/system/academic-erp.service`:

```ini
[Unit]
Description=Academic ERP Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project/backend
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/gunicorn config.wsgi:application -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable academic-erp
sudo systemctl start academic-erp
sudo systemctl status academic-erp
```

## Monitoring and Logging

### Application Logs

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/academic-erp/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Database Backup

Create automated backup script:

```bash
#!/bin/bash
# backup-db.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/academic-erp"
DB_NAME="academic_erp_prod"

mkdir -p $BACKUP_DIR

mysqldump -u erp_prod -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup-db.sh
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_attendance_date ON attendance_attendance(date);
CREATE INDEX idx_grade_student ON exams_grade(student_id);
CREATE INDEX idx_enrollment_status ON students_enrollment(status);
```

### Caching (Redis)

Install Redis and django-redis:
```bash
pip install django-redis redis
```

Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache sessions in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Security Hardening

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Block direct access to application port
sudo ufw deny 8000
```

### SSL/TLS Certificate

Using Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
pip install --upgrade -r requirements.txt

# Run security check
python manage.py check --deploy
```

## Troubleshooting

### Common Issues

1. **Static files not loading**
   - Ensure `STATIC_ROOT` is set and `collectstatic` was run
   - Check Nginx static file configuration

2. **Database connection errors**
   - Verify database credentials in `.env`
   - Check MySQL service status
   - Ensure database user has proper permissions

3. **Permission denied errors**
   - Check file/directory ownership and permissions
   - Ensure web server user can access project files

4. **High memory usage**
   - Adjust Gunicorn worker count based on server resources
   - Monitor database query performance
   - Consider implementing caching

### Log Locations

- Application logs: `/var/log/academic-erp/django.log`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- System logs: `journalctl -u academic-erp`

## Health Checks

Create a health check endpoint in `config/urls.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

urlpatterns = [
    # ... existing patterns
    path('health/', health_check, name='health_check'),
]
```

Monitor with:
```bash
curl -f http://yourdomain.com/health/ || echo "Service is down"
```