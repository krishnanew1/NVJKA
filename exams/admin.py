from django.contrib import admin
from .models import Assessment, Grade


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for Assessment model."""
    
    list_display = (
        'name',
        'get_subject_code',
        'get_subject_name',
        'assessment_type',
        'max_marks',
        'weightage',
        'date_conducted'
    )
    
    list_filter = (
        'assessment_type',
        'date_conducted',
        'subject__course__department',
        'subject'
    )
    
    search_fields = (
        'name',
        'subject__name',
        'subject__code',
        'description'
    )
    
    raw_id_fields = ('subject',)
    
    date_hierarchy = 'date_conducted'
    
    fieldsets = (
        ('Assessment Information', {
            'fields': ('name', 'subject', 'assessment_type', 'date_conducted')
        }),
        ('Grading Details', {
            'fields': ('max_marks', 'weightage')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_subject_code(self, obj):
        return obj.subject.code
    get_subject_code.short_description = 'Subject Code'
    get_subject_code.admin_order_field = 'subject__code'
    
    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.short_description = 'Subject'
    get_subject_name.admin_order_field = 'subject__name'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin configuration for Grade model."""
    
    list_display = (
        'get_student_name',
        'get_enrollment_number',
        'get_assessment_name',
        'marks_obtained',
        'get_max_marks',
        'get_percentage',
        'get_letter_grade',
        'get_graded_by'
    )
    
    list_filter = (
        'assessment__subject',
        'assessment__assessment_type',
        'assessment__date_conducted'
    )
    
    search_fields = (
        'student__enrollment_number',
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name',
        'assessment__name',
        'assessment__subject__code'
    )
    
    raw_id_fields = ('student', 'assessment', 'graded_by')
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('student', 'assessment', 'marks_obtained')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'graded_by')
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
    
    def get_assessment_name(self, obj):
        return obj.assessment.name
    get_assessment_name.short_description = 'Assessment'
    get_assessment_name.admin_order_field = 'assessment__name'
    
    def get_max_marks(self, obj):
        return obj.assessment.max_marks
    get_max_marks.short_description = 'Max Marks'
    
    def get_percentage(self, obj):
        return f"{obj.percentage:.2f}%"
    get_percentage.short_description = 'Percentage'
    
    def get_letter_grade(self, obj):
        return obj.get_letter_grade()
    get_letter_grade.short_description = 'Letter Grade'
    
    def get_graded_by(self, obj):
        if obj.graded_by:
            return obj.graded_by.user.get_full_name() or obj.graded_by.employee_id
        return '-'
    get_graded_by.short_description = 'Graded By'
