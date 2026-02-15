from django.contrib import admin
from .models import ClassAssignment


@admin.register(ClassAssignment)
class ClassAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for ClassAssignment model."""
    
    list_display = (
        'get_faculty_name',
        'get_employee_id',
        'get_subject_name',
        'get_subject_code',
        'semester',
        'academic_year',
        'section',
        'max_students',
        'is_active'
    )
    
    list_filter = (
        'academic_year',
        'semester',
        'is_active',
        'subject__course__department',
        'faculty__department'
    )
    
    search_fields = (
        'faculty__employee_id',
        'faculty__user__username',
        'faculty__user__first_name',
        'faculty__user__last_name',
        'subject__name',
        'subject__code',
        'academic_year',
        'section'
    )
    
    raw_id_fields = ('faculty', 'subject')
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('faculty', 'subject', 'semester', 'academic_year', 'section')
        }),
        ('Class Settings', {
            'fields': ('max_students', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_faculty_name(self, obj):
        return obj.faculty.user.get_full_name() or obj.faculty.user.username
    get_faculty_name.short_description = 'Faculty Name'
    get_faculty_name.admin_order_field = 'faculty__user__first_name'
    
    def get_employee_id(self, obj):
        return obj.faculty.employee_id
    get_employee_id.short_description = 'Employee ID'
    get_employee_id.admin_order_field = 'faculty__employee_id'
    
    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.short_description = 'Subject'
    get_subject_name.admin_order_field = 'subject__name'
    
    def get_subject_code(self, obj):
        return obj.subject.code
    get_subject_code.short_description = 'Subject Code'
    get_subject_code.admin_order_field = 'subject__code'
