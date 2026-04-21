"""
URL configuration for attendance app.
"""
from django.urls import path
from .views import (
    BulkAttendanceView, 
    StudentAttendanceView, 
    AttendanceRecordsView,
    FacultyAttendanceSummaryView,
    SubmitAttendanceReportView,
    AdminReportsView,
    FacultyReportsView
)

app_name = 'attendance'

urlpatterns = [
    # Bulk attendance marking endpoint
    path('bulk-mark/', BulkAttendanceView.as_view(), name='bulk_mark_attendance'),
    # Student attendance records endpoint
    path('my-records/', StudentAttendanceView.as_view(), name='student_attendance'),
    # Fetch and update attendance records endpoint
    path('records/', AttendanceRecordsView.as_view(), name='attendance_records'),
    # Faculty attendance summary endpoint
    path('faculty/summary/', FacultyAttendanceSummaryView.as_view(), name='faculty_attendance_summary'),
    # Submit attendance report endpoint
    path('faculty/submit-report/', SubmitAttendanceReportView.as_view(), name='submit_attendance_report'),
    # Faculty reports history endpoint
    path('faculty/reports/', FacultyReportsView.as_view(), name='faculty_reports'),
    # Admin reports review endpoint
    path('admin/reports/', AdminReportsView.as_view(), name='admin_reports'),
]
