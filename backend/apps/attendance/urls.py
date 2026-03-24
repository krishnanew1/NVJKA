"""
URL configuration for attendance app.
"""
from django.urls import path
from .views import BulkAttendanceView, StudentAttendanceView, AttendanceRecordsView

app_name = 'attendance'

urlpatterns = [
    # Bulk attendance marking endpoint
    path('bulk-mark/', BulkAttendanceView.as_view(), name='bulk_mark_attendance'),
    # Student attendance records endpoint
    path('my-records/', StudentAttendanceView.as_view(), name='student_attendance'),
    # Fetch and update attendance records endpoint
    path('records/', AttendanceRecordsView.as_view(), name='attendance_records'),
]
