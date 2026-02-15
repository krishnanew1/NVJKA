from django.contrib import admin
from .models import Enrollment, AcademicHistory


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model."""
    
    list_display = ('get_student_name', 'get_enrollment_number', 'get_course_name', 'get_course_code', 'status', 'date_enrolled')
    list_filter = ('status', 'date_enrolled', 'course__department')
    search_fields = (
        'student__enrollment_number',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'course__name',
        'course__code'
    )
    raw_id_fields = ('student', 'course')
    date_hierarchy = 'date_enrolled'
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'status')
        }),
        ('Dates', {
            'fields': ('date_enrolled', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('date_enrolled', 'created_at', 'updated_at')
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_enrollment_number(self, obj):
        return obj.student.enrollment_number
    get_enrollment_number.short_description = 'Enrollment #'
    get_enrollment_number.admin_order_field = 'student__enrollment_number'
    
    def get_course_name(self, obj):
        return obj.course.name
    get_course_name.short_description = 'Course'
    get_course_name.admin_order_field = 'course__name'
    
    def get_course_code(self, obj):
        return obj.course.code
    get_course_code.short_description = 'Course Code'
    get_course_code.admin_order_field = 'course__code'


@admin.register(AcademicHistory)
class AcademicHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for AcademicHistory model."""
    
    list_display = ('get_student_name', 'get_enrollment_number', 'year_completed', 'semester', 'gpa')
    list_filter = ('year_completed', 'semester')
    search_fields = (
        'student__enrollment_number',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'year_completed'
    )
    raw_id_fields = ('student',)
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Academic Period', {
            'fields': ('year_completed', 'semester', 'gpa')
        }),
        ('Grade Data', {
            'fields': ('previous_grades', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__user__first_name'
    
    def get_enrollment_number(self, obj):
        return obj.student.enrollment_number
    get_enrollment_number.short_description = 'Enrollment #'
    get_enrollment_number.admin_order_field = 'student__enrollment_number'
