"""
Custom middleware for the Academic ERP system.
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log all POST/PUT/PATCH/DELETE requests for audit trail.
    
    Logs include:
    - User ID and username
    - HTTP method (action)
    - Endpoint/URL path
    - IP address
    - User agent
    - Request body (sanitized)
    - Response status code
    - Execution time
    - Timestamp
    
    Usage:
        Add 'academic_erp_project.middleware.AuditLogMiddleware' to MIDDLEWARE in settings.py
    """
    
    # HTTP methods to audit
    AUDITED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Endpoints to exclude from auditing (to avoid noise)
    EXCLUDED_PATHS = [
        '/admin/jsi18n/',  # Django admin i18n
        '/static/',         # Static files
        '/media/',          # Media files
    ]
    
    def process_request(self, request):
        """
        Called before the view is executed.
        Store the start time for execution time calculation.
        """
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Called after the view is executed.
        Log the request if it matches audit criteria.
        """
        # Check if this request should be audited
        if not self._should_audit(request):
            return response
        
        # Calculate execution time
        execution_time = None
        if hasattr(request, '_audit_start_time'):
            execution_time = time.time() - request._audit_start_time
        
        # Log the request asynchronously to avoid blocking
        try:
            self._log_request(request, response, execution_time)
        except Exception as e:
            # Don't let logging errors break the request
            logger.error(f"Error logging audit trail: {e}")
        
        return response
    
    def _should_audit(self, request):
        """
        Determine if this request should be audited.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            bool: True if request should be audited
        """
        # Only audit specific HTTP methods
        if request.method not in self.AUDITED_METHODS:
            return False
        
        # Skip excluded paths
        for excluded_path in self.EXCLUDED_PATHS:
            if request.path.startswith(excluded_path):
                return False
        
        return True
    
    def _log_request(self, request, response, execution_time):
        """
        Create an audit log entry.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
            execution_time: Request execution time in seconds
        """
        # Import here to avoid circular imports
        from users.audit_models import AuditLog
        
        # Create audit log entry
        AuditLog.log_request(
            request=request,
            response=response,
            execution_time=execution_time
        )
        
        # Also log to file for redundancy
        self._log_to_file(request, response, execution_time)
    
    def _log_to_file(self, request, response, execution_time):
        """
        Log to file as backup/redundancy.
        
        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
            execution_time: Request execution time in seconds
        """
        try:
            user_str = request.user.username if request.user.is_authenticated else 'Anonymous'
            status = response.status_code if response else 'N/A'
            exec_time_str = f"{execution_time:.3f}s" if execution_time else 'N/A'
            
            log_message = (
                f"[AUDIT] {request.method} {request.path} | "
                f"User: {user_str} | "
                f"Status: {status} | "
                f"Time: {exec_time_str}"
            )
            
            logger.info(log_message)
        except Exception as e:
            logger.error(f"Error logging to file: {e}")


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Optional middleware for general request logging (all methods).
    
    Logs all requests for debugging and monitoring purposes.
    Less detailed than AuditLogMiddleware.
    """
    
    def process_request(self, request):
        """Log incoming request."""
        user_str = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.debug(f"[REQUEST] {request.method} {request.path} | User: {user_str}")
        return None
    
    def process_response(self, request, response):
        """Log response status."""
        logger.debug(f"[RESPONSE] {request.path} | Status: {response.status_code}")
        return response
