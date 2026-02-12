"""
Audit logging models for tracking system changes.
"""
from django.db import models
from django.contrib.auth import get_user_model


class AuditLog(models.Model):
    """
    Model for logging all POST/PUT/DELETE requests for audit trail.
    
    Tracks who made what changes, when, and from where.
    """
    
    ACTION_CHOICES = [
        ('POST', 'Create'),
        ('PUT', 'Update'),
        ('PATCH', 'Partial Update'),
        ('DELETE', 'Delete'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='User who performed the action (null for anonymous)'
    )
    
    username = models.CharField(
        max_length=150,
        blank=True,
        help_text='Username at time of action (preserved even if user deleted)'
    )
    
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        help_text='HTTP method used'
    )
    
    endpoint = models.CharField(
        max_length=500,
        help_text='API endpoint/URL path accessed'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the client'
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='Browser/client user agent string'
    )
    
    request_body = models.TextField(
        blank=True,
        help_text='Request body/payload (sanitized)'
    )
    
    response_status = models.IntegerField(
        null=True,
        blank=True,
        help_text='HTTP response status code'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When the action was performed'
    )
    
    execution_time = models.FloatField(
        null=True,
        blank=True,
        help_text='Request execution time in seconds'
    )
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['endpoint', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.username or 'Anonymous'
        return f"{user_str} - {self.action} {self.endpoint} at {self.timestamp}"
    
    @classmethod
    def log_request(cls, request, response=None, execution_time=None):
        """
        Create an audit log entry from a request and response.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object (optional)
            execution_time: Request execution time in seconds (optional)
        """
        # Get user information
        user = request.user if request.user.is_authenticated else None
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Get IP address
        ip_address = cls._get_client_ip(request)
        
        # Get request body (sanitize sensitive data)
        request_body = cls._sanitize_request_body(request)
        
        # Create log entry
        return cls.objects.create(
            user=user,
            username=username,
            action=request.method,
            endpoint=request.path,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_body=request_body,
            response_status=response.status_code if response else None,
            execution_time=execution_time
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _sanitize_request_body(request):
        """
        Get request body and sanitize sensitive fields.
        
        Removes passwords and other sensitive data from the log.
        """
        try:
            import json
            
            # Try to parse JSON body
            if hasattr(request, 'body') and request.body:
                body = request.body.decode('utf-8')
                
                # Try to parse as JSON
                try:
                    data = json.loads(body)
                    
                    # Sanitize sensitive fields
                    sensitive_fields = [
                        'password', 'password1', 'password2', 
                        'old_password', 'new_password',
                        'token', 'secret', 'api_key',
                        'credit_card', 'cvv', 'ssn'
                    ]
                    
                    if isinstance(data, dict):
                        for field in sensitive_fields:
                            if field in data:
                                data[field] = '***REDACTED***'
                    
                    return json.dumps(data)[:5000]  # Limit size
                except json.JSONDecodeError:
                    # Not JSON, return truncated body
                    return body[:5000]
            
            return ''
        except Exception:
            return 'Error reading request body'
