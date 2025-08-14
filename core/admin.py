from django.contrib import admin
from django.utils.html import format_html
from .models import Project

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

admin.site.register(Project, ProjectAdmin)
