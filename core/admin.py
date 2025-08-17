from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import LearningResource, Project, Contact, Article, Comment

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'client', 'created_at', 'featured', 'admin_thumbnail')
    list_filter = ('status', 'category', 'featured', 'created_at')
    search_fields = ('title', 'client', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_editable = ('status', 'featured')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description', 'technologies')
        }),
        ('Client Information', {
            'fields': ('client', 'website'),
            'classes': ('collapse',)
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'status'),
            'classes': ('collapse',)
        }),
        ('Media & Links', {
            'fields': ('image', 'thumbnail', 'github_url', 'live_url')
        }),
        ('Metadata', {
            'fields': ('featured', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />'.format(obj.image.url))
        return "No Image"
    admin_thumbnail.short_description = 'Thumbnail'
    
    def save_model(self, request, obj, form, change):
        # Generate thumbnail if not provided
        if obj.image and not obj.thumbnail:
            from PIL import Image
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.core.files.images import ImageFile
            
            # Open the original image
            image = Image.open(obj.image)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Create thumbnail
            thumb_size = (300, 200)
            image.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            
            # Save the thumbnail to memory
            thumb_io = BytesIO()
            image.save(thumb_io, format='JPEG', quality=85)
            
            # Set the thumbnail field
            thumb_file = ContentFile(thumb_io.getvalue())
            obj.thumbnail.save(
                f"{obj.slug}_thumb.jpg",
                ImageFile(thumb_file),
                save=False
            )
        
        super().save_model(request, obj, form, change)

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'status', 'view_count', 'created_at', 'admin_thumbnail')
    list_filter = ('status', 'resource_type', 'created_at')
    search_fields = ('title', 'short_description', 'description', 'document_text')
    list_editable = ('status',)
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'published_at', 'admin_thumbnail')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'resource_type', 'status', 'author')
        }),
        ('Content', {
            'fields': ('short_description', 'description', 'content', 'read_time')
        }),
        ('Media', {
            'fields': ('image', 'admin_thumbnail', 'image_caption', 'video_url', 'document')
        }),
        ('Metadata', {
            'fields': ('view_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "No Image"
    admin_thumbnail.short_description = 'Thumbnail'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Contact)
admin.site.register(Article)
admin.site.register(Comment)


