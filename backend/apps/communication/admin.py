from django.contrib import admin
from communication.models import Notice, Resource


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """Admin configuration for Notice model"""
    
    list_display = [
        'title', 
        'audience', 
        'priority', 
        'created_by', 
        'is_active',
        'created_at',
        'expires_at'
    ]
    
    list_filter = [
        'audience',
        'priority',
        'is_active',
        'created_at',
        'expires_at'
    ]
    
    search_fields = [
        'title',
        'content',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Notice Information', {
            'fields': ('title', 'content', 'audience', 'priority')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        """Mark selected notices as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} notice(s) marked as active.')
    mark_as_active.short_description = 'Mark selected notices as active'
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected notices as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} notice(s) marked as inactive.')
    mark_as_inactive.short_description = 'Mark selected notices as inactive'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin configuration for Resource model"""
    
    list_display = [
        'title',
        'subject',
        'resource_type',
        'uploaded_by',
        'get_file_size_display',
        'download_count',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'resource_type',
        'is_active',
        'subject__course',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'description',
        'subject__name',
        'subject__code',
        'uploaded_by__username',
        'uploaded_by__first_name',
        'uploaded_by__last_name'
    ]
    
    readonly_fields = [
        'file_size',
        'download_count',
        'created_at',
        'updated_at',
        'get_file_extension'
    ]
    
    fieldsets = (
        ('Resource Information', {
            'fields': ('title', 'description', 'subject', 'resource_type')
        }),
        ('File', {
            'fields': ('file', 'file_size', 'get_file_extension')
        }),
        ('Statistics', {
            'fields': ('download_count', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_active', 'mark_as_inactive', 'reset_download_count']
    
    def mark_as_active(self, request, queryset):
        """Mark selected resources as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} resource(s) marked as active.')
    mark_as_active.short_description = 'Mark selected resources as active'
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected resources as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} resource(s) marked as inactive.')
    mark_as_inactive.short_description = 'Mark selected resources as inactive'
    
    def reset_download_count(self, request, queryset):
        """Reset download count to zero"""
        updated = queryset.update(download_count=0)
        self.message_user(request, f'Download count reset for {updated} resource(s).')
    reset_download_count.short_description = 'Reset download count'

