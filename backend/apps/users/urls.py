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
    StudentListView,
    FacultyListView,
    FacultyWorkListCreateView,
    FacultyWorkDetailView,
    FacultyPublicWorksView,
)

app_name = 'users'

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration endpoint
    path('register/', RegisterUserView.as_view(), name='register'),
    
    # List endpoints
    path('students/', StudentListView.as_view(), name='student_list'),
    path('faculty/', FacultyListView.as_view(), name='faculty_list'),

    # Faculty works (research papers/projects)
    path('faculty/works/', FacultyWorkListCreateView.as_view(), name='faculty_works'),
    path('faculty/works/<int:pk>/', FacultyWorkDetailView.as_view(), name='faculty_work_detail'),
    path('faculty/<int:faculty_id>/works/', FacultyPublicWorksView.as_view(), name='faculty_public_works'),
    
    # Dashboard endpoints
    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/faculty/', FacultyDashboardView.as_view(), name='faculty_dashboard'),
]