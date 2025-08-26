from django.contrib import admin
from .models import TemplateCategory, WebsiteTemplate


@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'template_type', 'difficulty_level', 'view_count', 'download_count', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'template_type', 'difficulty_level', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'technologies', 'tags', 'author']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'download_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'template_type')
        }),
        ('GitHub Integration', {
            'fields': ('github_url', 'github_pages_url')
        }),
        ('Template Details', {
            'fields': ('technologies', 'difficulty_level', 'author', 'license_type', 'tags')
        }),
        ('Media', {
            'fields': ('thumbnail', 'preview_images')
        }),
        ('Status & Stats', {
            'fields': ('is_featured', 'is_active', 'view_count', 'download_count', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_featured', 'unmark_featured', 'activate', 'deactivate']
    
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} templates marked as featured.')
    mark_featured.short_description = 'Mark selected templates as featured'
    
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} templates unmarked as featured.')
    unmark_featured.short_description = 'Unmark selected templates as featured'
    
    def activate(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} templates activated.')
    activate.short_description = 'Activate selected templates'
    
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} templates deactivated.')
    deactivate.short_description = 'Deactivate selected templates'
