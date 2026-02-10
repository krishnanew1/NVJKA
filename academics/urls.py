"""
URL configuration for academics app.

This module defines URL patterns for academic API endpoints using
Django REST Framework routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, CourseViewSet, SubjectViewSet, TimetableViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'timetables', TimetableViewSet, basename='timetable')

app_name = 'academics'

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
]