from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify


class TemplateCategory(models.Model):
    """Categories for organizing templates"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder', help_text='Bootstrap icon class')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Template Categories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class WebsiteTemplate(models.Model):
    """Model for storing website templates with GitHub links"""
    TEMPLATE_TYPES = [
        ('landing', 'Landing Page'),
        ('portfolio', 'Portfolio'),
        ('business', 'Business'),
        ('blog', 'Blog'),
        ('ecommerce', 'E-commerce'),
        ('dashboard', 'Dashboard'),
        ('app', 'Web App'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='templates')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='other')
    
    # GitHub information
    github_url = models.URLField(help_text='GitHub repository URL')
    github_pages_url = models.URLField(blank=True, help_text='GitHub Pages live demo URL')
    
    # Template details
    technologies = models.CharField(max_length=300, help_text='Technologies used (e.g., HTML, CSS, JavaScript, React)')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    
    # Media
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', blank=True, null=True)
    preview_images = models.JSONField(default=list, blank=True, help_text='List of preview image URLs')
    
    # Metadata
    author = models.CharField(max_length=100, blank=True)
    license_type = models.CharField(max_length=50, default='MIT')
    tags = models.CharField(max_length=300, blank=True, help_text='Comma-separated tags')
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['category', 'template_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('website_templates:template_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def __str__(self):
        return self.title
