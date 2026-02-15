from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    
    list_display = (
        'get_student_name',
        'get_enrollment_number',
        'get_subject_name',
        'get_subject_code',
        'date',
        'status',
        'get_marked_by'
    )
    
    list_filter = (
        'status',
        'date',
        'subject__course__department',
        'subject'
    )
    
    search_fields = (
        'student__enrollment_number',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'subject__name',
        'subject__code',
        'remarks'
    )
    
    raw_id_fields = ('student', 'subject', 'marked_by')
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'subject', 'date', 'status')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'marked_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    list_per_page = 50
    
    actions = ['mark_as_present', 'mark_as_absent', 'mark_as_late']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_enrollment_number(self, obj):
        return obj.student.enrollment_number
    get_enrollment_number.short_description = 'Enrollment #'
    get_enrollment_number.admin_order_field = 'student__enrollment_number'
    
    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.short_description = 'Subject'
    get_subject_name.admin_order_field = 'subject__name'
    
    def get_subject_code(self, obj):
        return obj.subject.code
    get_subject_code.short_description = 'Subject Code'
    get_subject_code.admin_order_field = 'subject__code'
    
    def get_marked_by(self, obj):
        if obj.marked_by:
            return obj.marked_by.user.get_full_name() or obj.marked_by.employee_id
        return '-'
    get_marked_by.short_description = 'Marked By'
    
    # Bulk actions
    def mark_as_present(self, request, queryset):
        updated = queryset.update(status='PRESENT')
        self.message_user(request, f'{updated} attendance records marked as PRESENT.')
    mark_as_present.short_description = 'Mark selected as PRESENT'
    
    def mark_as_absent(self, request, queryset):
        updated = queryset.update(status='ABSENT')
        self.message_user(request, f'{updated} attendance records marked as ABSENT.')
    mark_as_absent.short_description = 'Mark selected as ABSENT'
    
    def mark_as_late(self, request, queryset):
        updated = queryset.update(status='LATE')
        self.message_user(request, f'{updated} attendance records marked as LATE.')
    mark_as_late.short_description = 'Mark selected as LATE'
