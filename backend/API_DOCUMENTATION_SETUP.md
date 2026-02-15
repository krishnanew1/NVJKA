# API Documentation Setup Guide

## Overview

The Academic ERP system uses **drf-yasg** (Yet Another Swagger Generator) to provide interactive API documentation. This allows developers and API consumers to explore, test, and understand the API endpoints without writing code.

## Features

### 1. Interactive Swagger UI
- Browse all available API endpoints
- View request/response schemas
- Test endpoints directly from the browser
- See authentication requirements
- View example requests and responses

### 2. ReDoc Documentation
- Clean, responsive documentation
- Three-panel layout for easy navigation
- Search functionality
- Code samples in multiple languages

### 3. OpenAPI Schema
- Machine-readable API specification
- Can be used to generate client SDKs
- Compatible with API testing tools

## Accessing the Documentation

### Swagger UI (Interactive)
```
http://localhost:8000/swagger/
```

**Features:**
- Interactive API explorer
- "Try it out" functionality to test endpoints
- Authentication support (JWT tokens)
- Request/response examples
- Model schemas

### ReDoc (Read-Only)
```
http://localhost:8000/redoc/
```

**Features:**
- Clean, professional documentation
- Better for reading and understanding
- Responsive design
- Search functionality
- Downloadable OpenAPI spec

### OpenAPI Schema (JSON/YAML)
```
http://localhost:8000/swagger.json
http://localhost:8000/swagger.yaml
```

**Use Cases:**
- Generate client libraries
- Import into Postman/Insomnia
- API testing automation
- Contract testing

## Installation

### 1. Install drf-yasg

```bash
pip install drf-yasg
```

### 2. Add to INSTALLED_APPS

In `academic_erp_project/settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'drf_yasg',  # Add this
    # ... other apps
]
```

### 3. Configure URLs

In `academic_erp_project/urls.py`:

```python
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Academic ERP API",
        default_version='v1',
        description="API documentation for Academic ERP System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@academicerp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ... other URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

## Using the Documentation

### Testing Endpoints with Authentication

1. **Obtain JWT Token:**
   - Navigate to `/api/auth/login/` in Swagger
   - Click "Try it out"
   - Enter credentials:
     ```json
     {
       "username": "your_username",
       "password": "your_password"
     }
     ```
   - Click "Execute"
   - Copy the `access` token from the response

2. **Authorize:**
   - Click the "Authorize" button at the top of Swagger UI
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
   - Click "Close"

3. **Test Protected Endpoints:**
   - All subsequent requests will include the authorization header
   - Try any protected endpoint (e.g., `/api/academics/departments/`)

### Example: Testing Student Enrollment

1. **Authorize** as an admin user (see above)

2. **Navigate to** `/api/students/enroll/`

3. **Click** "Try it out"

4. **Enter request body:**
   ```json
   {
     "student_id": 1,
     "course_id": 2
   }
   ```

5. **Click** "Execute"

6. **View response:**
   - Status code (201 Created)
   - Response body with enrollment details
   - Response headers

## Documenting Your Views

### ViewSets (Automatic Documentation)

ViewSets are automatically documented by drf-yasg:

```python
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department model.
    
    Provides CRUD operations for departments with authentication,
    filtering, and search capabilities.
    
    list: Get all departments
    create: Create a new department
    retrieve: Get a specific department
    update: Update a department
    partial_update: Partially update a department
    destroy: Delete a department
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
```

### APIView (Manual Documentation)

For APIView classes, add detailed docstrings:

```python
class EnrollStudentView(APIView):
    """
    API endpoint for enrolling students in courses.
    
    POST: Enroll a student in a course
    
    Permissions: IsAuthenticated AND User role is ADMIN
    
    Request Body:
    {
        "student_id": 1,
        "course_id": 2
    }
    
    Responses:
    - 201: Student enrolled successfully
    - 400: Validation error
    - 403: Permission denied
    - 404: Student or course not found
    """
    permission_classes = [IsAdmin]
    
    def post(self, request):
        """
        Enroll a student in a course.
        
        Validates that the student and course exist,
        and that the student is not already enrolled.
        """
        # Implementation...
```

### Serializer Documentation

Document serializers for better schema generation:

```python
class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentProfile model.
    
    Includes nested user information (username, email, name).
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'enrollment_number', 'department', 
                  'current_semester', 'batch_year']
        read_only_fields = ['id']
```

### Field-Level Documentation

Add help_text to model fields for automatic documentation:

```python
class Department(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Full name of the department"
    )
    code = models.CharField(
        max_length=10,
        help_text="Short code for the department (e.g., 'CSE', 'ECE')"
    )
```

## Advanced Configuration

### Custom Schema Information

```python
schema_view = get_schema_view(
    openapi.Info(
        title="Academic ERP API",
        default_version='v1',
        description="""
        Comprehensive API for managing academic operations.
        
        ## Features
        - User authentication with JWT
        - Department, course, and subject management
        - Student enrollment and tracking
        - Attendance management
        - Examination and grading
        - Communication (notices and resources)
        
        ## Authentication
        Use JWT tokens obtained from /api/auth/login/
        Include in header: Authorization: Bearer <token>
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="API Support",
            email="api@academicerp.com",
            url="https://www.academicerp.com/support"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
```

### Security Definitions

Add JWT authentication to schema:

```python
from drf_yasg import openapi

schema_view = get_schema_view(
    # ... other config
    public=True,
    permission_classes=(permissions.AllowAny,),
)
```

### Custom Response Examples

Use drf-yasg decorators for custom examples:

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class EnrollStudentView(APIView):
    @swagger_auto_schema(
        operation_description="Enroll a student in a course",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['student_id', 'course_id'],
            properties={
                'student_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the student to enroll'
                ),
                'course_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the course'
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Student enrolled successfully",
                examples={
                    "application/json": {
                        "message": "Student enrolled successfully",
                        "enrollment": {
                            "id": 1,
                            "student": {"id": 1, "enrollment_number": "2026CS001"},
                            "course": {"id": 2, "code": "BTCS"},
                            "status": "ENROLLED"
                        }
                    }
                }
            ),
            400: "Validation error",
            403: "Permission denied",
            404: "Student or course not found"
        }
    )
    def post(self, request):
        # Implementation...
```

## Customization

### Swagger UI Settings

In `settings.py`:

```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}
```

### ReDoc Settings

```python
REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
}
```

## Best Practices

### 1. Write Clear Docstrings
- Describe what the endpoint does
- List required permissions
- Document request/response formats
- Include example payloads

### 2. Use Meaningful Names
- Clear endpoint names
- Descriptive parameter names
- Consistent naming conventions

### 3. Document Error Responses
- List all possible status codes
- Explain error conditions
- Provide example error responses

### 4. Keep Documentation Updated
- Update docstrings when changing endpoints
- Review documentation regularly
- Test examples to ensure they work

### 5. Use Serializer Help Text
- Add help_text to model fields
- Document serializer fields
- Explain complex relationships

## Troubleshooting

### Swagger UI Not Loading

1. **Check INSTALLED_APPS:**
   ```python
   'drf_yasg' in INSTALLED_APPS
   ```

2. **Check URL Configuration:**
   ```python
   path('swagger/', schema_view.with_ui('swagger'))
   ```

3. **Clear Browser Cache:**
   - Hard refresh (Ctrl+Shift+R)
   - Clear cache and reload

### Endpoints Not Appearing

1. **Check URL Registration:**
   - Ensure app URLs are included in main urls.py
   - Verify router registration for ViewSets

2. **Check Permissions:**
   - Schema view should have `AllowAny` permission
   - Individual endpoints can have stricter permissions

3. **Check View Documentation:**
   - Add docstrings to views
   - Ensure views inherit from DRF classes

### Authentication Not Working

1. **Obtain Fresh Token:**
   - Login via `/api/auth/login/`
   - Copy the access token

2. **Format Authorization Header:**
   ```
   Bearer <your_access_token>
   ```
   (Note: "Bearer" with capital B and space)

3. **Check Token Expiration:**
   - JWT tokens expire after configured time
   - Obtain new token if expired

## Integration with Other Tools

### Postman

1. Access `/swagger.json`
2. In Postman: Import → Link → Paste URL
3. Collection will be created automatically

### Insomnia

1. Access `/swagger.json`
2. In Insomnia: Import/Export → Import Data → From URL
3. Paste the swagger.json URL

### API Testing

```python
import requests

# Get OpenAPI schema
schema = requests.get('http://localhost:8000/swagger.json').json()

# Use schema for contract testing
# Validate responses against schema
```

## Security Considerations

### Production Deployment

1. **Restrict Access:**
   ```python
   # Only allow authenticated users in production
   permission_classes=(permissions.IsAuthenticated,)
   ```

2. **Disable in Production (Optional):**
   ```python
   # In settings.py
   if not DEBUG:
       # Remove swagger URLs or restrict access
       pass
   ```

3. **Use HTTPS:**
   - Always use HTTPS in production
   - Protect API tokens in transit

### Sensitive Data

- Don't expose sensitive endpoints
- Sanitize example data
- Remove internal implementation details

## Related Documentation

- [drf-yasg Documentation](https://drf-yasg.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
