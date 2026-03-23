from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'recorded_by')
    list_filter = ('status', 'date', 'subject__course__department')
    search_fields = (
        'student__enrollment_number',
        'student__user__username',
        'subject__name',
        'subject__code',
    )
    date_hierarchy = 'date'
    raw_id_fields = ('student', 'subject', 'recorded_by')
