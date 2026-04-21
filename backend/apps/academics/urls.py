"""
URL configuration for academics app.

This module defines URL patterns for academic API endpoints using
Django REST Framework routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, CourseViewSet, SubjectViewSet, TimetableViewSet,
    CustomRegistrationFieldViewSet, ProgramViewSet, MySubjectsView,
    TimetablePDFUploadView, TimetablePDFListView, TimetablePDFDetailView
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'custom-fields', CustomRegistrationFieldViewSet, basename='custom-field')
router.register(r'programs', ProgramViewSet, basename='program')

app_name = 'academics'

urlpatterns = [
    # Faculty-specific endpoints
    path('faculty/my-subjects/', MySubjectsView.as_view(), name='my-subjects'),
    
    # Timetable PDF endpoints
    path('timetables/upload/', TimetablePDFUploadView.as_view(), name='timetable-upload'),
    path('timetables/pdfs/', TimetablePDFListView.as_view(), name='timetable-pdfs'),
    path('timetables/pdfs/<int:pk>/', TimetablePDFDetailView.as_view(), name='timetable-pdf-detail'),
    
    # Include all router URLs
    path('', include(router.urls)),
]