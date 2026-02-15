from django.contrib import admin
from .models import (
    Department, StudentProfile, FacultyProfile, 
    Course, FacultyAssignment, Enrollment, Attendance, FeePayment
)

# Register models
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_name', 'dept_code')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'abc_id', 'scholarship_eligible')

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'department')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'department', 'credits')
    list_filter = ('department',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester_no', 'status')
    list_filter = ('status', 'semester_no')

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_paid', 'payment_status', 'transaction_id')

# Simple registrations for others
admin.site.register(FacultyAssignment)
admin.site.register(Attendance)