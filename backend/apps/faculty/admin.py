from django.contrib import admin
from .models import ClassAssignment


@admin.register(ClassAssignment)
class ClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'subject', 'semester', 'academic_year')
    list_filter = ('semester', 'academic_year', 'subject__course__department')
    search_fields = (
        'faculty__employee_id',
        'faculty__user__username',
        'subject__name',
        'subject__code',
    )
