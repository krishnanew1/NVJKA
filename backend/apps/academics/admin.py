from django.contrib import admin
from .models import Department, Course, Subject, Timetable


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model."""
    list_display = ('code', 'name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code', 'description')
    ordering = ('code',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    list_display = ('code', 'name', 'department', 'credits', 'duration_years')
    list_filter = ('department', 'duration_years', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('department__code', 'code')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin configuration for Subject model."""
    list_display = ('code', 'name', 'course', 'semester', 'credits', 'is_mandatory')
    list_filter = ('course__department', 'course', 'semester', 'is_mandatory', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('course__code', 'semester', 'code')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    """Admin configuration for Timetable model."""
    list_display = ('class_name', 'subject', 'day_of_week', 'start_time', 'end_time', 'room_number', 'is_active')
    list_filter = ('day_of_week', 'subject__course__department', 'subject__course', 'academic_year', 'is_active')
    search_fields = ('class_name', 'subject__name', 'subject__code', 'room_number')
    ordering = ('day_of_week', 'start_time', 'class_name')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('subject__course__department')
