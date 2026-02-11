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
from django.urls import path, include  # 1. Import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),  # Portal app URLs
    path('api/auth/', include('users.urls')),  # JWT authentication endpoints
    path('api/academics/', include('academics.urls')),  # Academic API endpoints
    path('api/students/', include('students.urls')),  # Student management endpoints
    path('api/attendance/', include('attendance.urls')),  # Attendance management endpoints
]
