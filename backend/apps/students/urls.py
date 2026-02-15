"""
URL configuration for students app.
"""
from django.urls import path
from .views import EnrollStudentView

app_name = 'students'

urlpatterns = [
    # Enrollment endpoint
    path('enroll/', EnrollStudentView.as_view(), name='enroll_student'),
]
