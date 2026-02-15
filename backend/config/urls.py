"""
URL configuration for academic_erp_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Academic ERP API",
        default_version='v1',
        description="""
        Academic ERP System API Documentation
        
        This API provides comprehensive endpoints for managing an academic institution's 
        operations including:
        - User authentication and authorization (JWT)
        - Academic structure (departments, courses, subjects, timetables)
        - Student management (enrollment, academic history)
        - Faculty management (class assignments)
        - Attendance tracking and reporting
        - Examination and grading system
        - Communication (notices, learning resources)
        
        ## Authentication
        Most endpoints require JWT authentication. Obtain a token from `/api/auth/login/`
        and include it in the Authorization header:
        ```
        Authorization: Bearer <your_token>
        ```
        
        ## Permissions
        - **Admin**: Full access to all endpoints
        - **Faculty**: Access to class management, attendance, grading
        - **Student**: Read-only access to their own data
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@academicerp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),  # Portal app URLs
    path('api/auth/', include('users.urls')),  # JWT authentication endpoints
    path('api/academics/', include('academics.urls')),  # Academic API endpoints
    path('api/students/', include('apps.students.urls')),  # Student management endpoints
    path('api/attendance/', include('apps.attendance.urls')),  # Attendance management endpoints
    
    # Swagger/OpenAPI documentation endpoints
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
