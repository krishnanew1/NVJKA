from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, FacultyProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""
    
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'profile_picture', 'phone_number', 'address')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'profile_picture', 'phone_number', 'address')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin configuration for StudentProfile model."""
    
    list_display = ('enrollment_number', 'get_student_name', 'department', 'current_semester', 'batch_year')
    list_filter = ('department', 'batch_year', 'current_semester')
    search_fields = ('enrollment_number', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('enrollment_number', 'department', 'current_semester', 'batch_year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_student_name.short_description = 'Student Name'


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    """Admin configuration for FacultyProfile model."""
    
    list_display = ('employee_id', 'get_faculty_name', 'department', 'designation', 'date_of_joining')
    list_filter = ('department', 'designation', 'date_of_joining')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'specialization')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Employment Information', {
            'fields': ('employee_id', 'department', 'designation', 'specialization', 'date_of_joining')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_faculty_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_faculty_name.short_description = 'Faculty Name'
