from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Department, StudentProfile, FacultyProfile, 
    Course, FacultyAssignment, Enrollment, Attendance, FeePayment
)

# 1. Register the Custom User Model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )

# 2. Register other models
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