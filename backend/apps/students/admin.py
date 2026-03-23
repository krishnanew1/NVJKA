from django.contrib import admin
from .models import Enrollment, AcademicHistory


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'status', 'date_enrolled')
    list_filter = ('status', 'semester')
    search_fields = ('student__enrollment_number', 'course__name')


@admin.register(AcademicHistory)
class AcademicHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'institution_name', 'board_university', 'passing_year', 'percentage_cgpa')
    list_filter = ('passing_year',)
    search_fields = ('student__enrollment_number', 'institution_name', 'board_university')
