"""
URL configuration for users app.

This module defines URL patterns for user authentication and JWT token management.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    StudentDashboardView, 
    FacultyDashboardView,
    RegisterUserView,
    StudentListView
)

app_name = 'users'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration endpoint
    path('register/', RegisterUserView.as_view(), name='register'),
    
    # Student list endpoint
    path('students/', StudentListView.as_view(), name='student_list'),
    
    # Dashboard endpoints
    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/faculty/', FacultyDashboardView.as_view(), name='faculty_dashboard'),
]