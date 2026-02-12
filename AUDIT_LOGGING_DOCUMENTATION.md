# Audit Logging System Documentation

## Overview

The Academic ERP system includes a comprehensive audit logging system that tracks all data-modifying operations (POST, PUT, PATCH, DELETE requests) for security, compliance, and debugging purposes.

## Components

### 1. AuditLog Model (`users/audit_models.py`)

A dedicated database model that stores audit trail information.

**Fields:**
- `user`: ForeignKey to the user who performed the action (null for anonymous)
- `username`: Username preserved even if user is deleted
- `action`: HTTP method (POST, PUT, PATCH, DELETE)
- `endpoint`: URL path accessed
- `ip_address`: Client IP address
- `user_agent`: Browser/client information
- `request_body`: Sanitized request payload
- `response_status`: HTTP response status code
- `timestamp`: When the action occurred
- `execution_time`: Request processing time in seconds

**Features:**
- Automatic sensitive data sanitization (passwords, tokens, etc.)
- IP address extraction (handles proxies)
- Efficient database indexes for querying
- Preserved username even if user account is deleted

### 2. AuditLogMiddleware (`academic_erp_project/middleware.py`)

Django middleware that automatically logs qualifying requests.

**What Gets Logged:**
- All POST requests (create operations)
- All PUT requests (full update operations)
- All PATCH requests (partial update operations)
- All DELETE requests (delete operations)

**What Doesn't Get Logged:**
- GET requests (read-only, no data modification)
- HEAD, OPTIONS requests
- Static file requests (`/static/`, `/media/`)
- Django admin i18n requests
- Any paths in `EXCLUDED_PATHS` configuration

**Logged Information:**
- User identification (ID and username)
- Request method and endpoint
- Client IP address and user agent
- Request body (with sensitive data redacted)
- Response status code
- Execution time
- Timestamp

## Installation

### Step 1: Add Middleware to Settings

Edit `academic_erp_project/settings.py` and add the middleware to the `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Add audit logging middleware
    'academic_erp_project.middleware.AuditLogMiddleware',  # <-- Add this line
]
```

**Important:** Place it after authentication middleware so user information is available.

### Step 2: Configure Logging (Optional)

For file-based logging backup, configure Django logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/audit.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'academic_erp_project.middleware': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

Create the logs directory:
```bash
mkdir logs
```

### Step 3: Run Migrations

The AuditLog model migration should already be applied. If not:

```bash
python manage.py migrate users
```

## Usage

### Automatic Logging

Once the middleware is enabled, all qualifying requests are automatically logged. No code changes needed in views or serializers.

### Viewing Audit Logs

#### Via Django Admin

1. Log in to Django admin: `http://localhost:8000/admin/`
2. Navigate to "Users" → "Audit Logs"
3. Use filters to search by:
   - Action type (POST, PUT, PATCH, DELETE)
   - Response status
   - Date/time
   - Username
   - Endpoint

#### Via Database Query

```python
from users.audit_models import AuditLog

# Get all logs for a specific user
user_logs = AuditLog.objects.filter(username='john_doe')

# Get all failed requests (4xx, 5xx status codes)
failed_requests = AuditLog.objects.filter(response_status__gte=400)

# Get logs for a specific endpoint
endpoint_logs = AuditLog.objects.filter(endpoint='/api/students/enroll/')

# Get recent logs (last 24 hours)
from django.utils import timezone
from datetime import timedelta

recent = AuditLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(days=1)
)

# Get slow requests (> 1 second)
slow_requests = AuditLog.objects.filter(execution_time__gt=1.0)
```

#### Via Management Command (Future Enhancement)

```bash
# Export audit logs to CSV
python manage.py export_audit_logs --start-date 2024-01-01 --end-date 2024-12-31 --output audit_2024.csv

# Generate audit report
python manage.py audit_report --user john_doe --days 30
```

## Security Features

### 1. Sensitive Data Sanitization

The system automatically redacts sensitive fields from request bodies:

**Sanitized Fields:**
- `password`, `password1`, `password2`
- `old_password`, `new_password`
- `token`, `secret`, `api_key`
- `credit_card`, `cvv`, `ssn`

**Example:**
```json
// Original request
{
    "username": "john_doe",
    "password": "secret123",
    "email": "john@example.com"
}

// Logged request
{
    "username": "john_doe",
    "password": "***REDACTED***",
    "email": "john@example.com"
}
```

### 2. IP Address Tracking

Handles both direct connections and proxied requests:
- Checks `HTTP_X_FORWARDED_FOR` header for proxied requests
- Falls back to `REMOTE_ADDR` for direct connections
- Extracts first IP from comma-separated list

### 3. Read-Only Admin Interface

- Audit logs cannot be created manually via admin
- Audit logs cannot be edited
- Only superusers can delete audit logs
- Prevents tampering with audit trail

### 4. User Preservation

- Username is stored separately from user FK
- If user account is deleted, username remains in audit log
- Maintains complete audit trail even after user deletion

## Performance Considerations

### Database Indexes

The AuditLog model includes optimized indexes:
```python
indexes = [
    models.Index(fields=['-timestamp']),
    models.Index(fields=['user', '-timestamp']),
    models.Index(fields=['action', '-timestamp']),
    models.Index(fields=['endpoint', '-timestamp']),
]
```

### Asynchronous Logging

The middleware logs asynchronously to avoid blocking requests:
- Logging errors don't break the request
- Failed logs are caught and logged to error log
- Request processing continues even if logging fails

### Request Body Size Limit

Request bodies are truncated to 5000 characters to prevent database bloat:
```python
return json.dumps(data)[:5000]  # Limit size
```

### Log Rotation (File-Based)

When using file-based logging:
- Maximum file size: 10 MB
- Backup count: 5 files
- Automatic rotation when size limit reached

## Compliance and Regulations

### GDPR Compliance

- User data is logged for legitimate security purposes
- Users should be informed via privacy policy
- Audit logs should be included in data export requests
- Logs should be deleted when user requests data deletion (if legally permissible)

### SOC 2 / ISO 27001

- Comprehensive audit trail for all data modifications
- Immutable logs (read-only in admin)
- Timestamp and user tracking
- IP address logging for security investigations

### HIPAA / FERPA (if applicable)

- Tracks access to sensitive student/health records
- Identifies who accessed what data and when
- Supports compliance audits and investigations

## Monitoring and Alerts

### Failed Request Monitoring

```python
# Check for unusual number of failed requests
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

failed_by_user = AuditLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=1),
    response_status__gte=400
).values('username').annotate(
    count=Count('id')
).filter(count__gt=10)

# Alert if any user has > 10 failed requests in last hour
for user_stat in failed_by_user:
    print(f"Alert: {user_stat['username']} has {user_stat['count']} failed requests")
```

### Suspicious Activity Detection

```python
# Detect unusual activity patterns
suspicious = AuditLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(minutes=5),
    action='DELETE'
).values('username').annotate(
    count=Count('id')
).filter(count__gt=5)

# Alert if any user performs > 5 deletes in 5 minutes
```

## Maintenance

### Archiving Old Logs

```python
# Archive logs older than 1 year
from datetime import timedelta
from django.utils import timezone

cutoff_date = timezone.now() - timedelta(days=365)
old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)

# Export to file before deleting
import csv
with open('archived_logs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Username', 'Action', 'Endpoint', 'Status'])
    for log in old_logs:
        writer.writerow([log.timestamp, log.username, log.action, log.endpoint, log.response_status])

# Delete old logs
old_logs.delete()
```

### Database Cleanup

```python
# Delete logs for deleted test users
AuditLog.objects.filter(username__startswith='test_').delete()

# Delete logs with no response status (incomplete requests)
AuditLog.objects.filter(response_status__isnull=True).delete()
```

## Troubleshooting

### Middleware Not Logging

1. **Check middleware is enabled:**
   ```python
   # In settings.py
   print(MIDDLEWARE)  # Should include AuditLogMiddleware
   ```

2. **Check database migration:**
   ```bash
   python manage.py showmigrations users
   # Should show [X] 0005_auditlog
   ```

3. **Check request method:**
   - Only POST/PUT/PATCH/DELETE are logged
   - GET requests are not logged by default

4. **Check excluded paths:**
   - Static files and admin i18n are excluded
   - Check `EXCLUDED_PATHS` in middleware

### High Database Growth

1. **Implement log rotation:**
   - Archive old logs periodically
   - Delete logs older than retention period

2. **Reduce logged data:**
   - Decrease request body size limit
   - Exclude more paths from logging

3. **Use file-based logging:**
   - Log to files instead of database
   - Use log rotation for files

### Performance Impact

1. **Add database indexes:**
   - Already included in model
   - Verify indexes are created: `python manage.py sqlmigrate users 0005`

2. **Use database connection pooling:**
   - Configure in settings.py
   - Reduces connection overhead

3. **Consider async logging:**
   - Use Celery for background logging
   - Queue log entries for batch processing

## Future Enhancements

Potential improvements:
1. Async logging with Celery
2. Elasticsearch integration for log search
3. Real-time alerting system
4. Audit log analytics dashboard
5. Automated compliance reports
6. Log export to external SIEM systems
7. Anomaly detection with machine learning
8. User activity timeline visualization

## Related Documentation

- [Django Middleware Documentation](https://docs.djangoproject.com/en/stable/topics/http/middleware/)
- [Django Logging Documentation](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Security Best Practices](academic_erp_project/SECURITY.md)
