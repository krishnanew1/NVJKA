"""
URL configuration for attendance app.
"""
from django.urls import path
from .views import BulkAttendanceView

app_name = 'attendance'

urlpatterns = [
    # Bulk attendance marking endpoint
    path('bulk-mark/', BulkAttendanceView.as_view(), name='bulk_mark_attendance'),
]
