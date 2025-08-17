import os
import mimetypes
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.utils.text import slugify
from .utils import extract_text_from_pdf, validate_video_url, get_video_embed_code

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
class Project(models.Model):
    PROJECT_CATEGORIES = [
        ('web', 'Website'),
        ('app', 'Mobile App'),
        ('ecom', 'E-commerce'),
        ('custom', 'Custom Software'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('launched', 'Launched'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=PROJECT_CATEGORIES)
    short_description = models.TextField(max_length=200)
    description = models.TextField()
    client = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    featured = models.BooleanField(default=False)
    technologies = models.CharField(max_length=255, help_text="Comma-separated list of technologies used")
    image = models.ImageField(upload_to='projects/')
    thumbnail = models.ImageField(upload_to='projects/thumbnails/', blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
        
    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',')]
        
    class Meta:
        ordering = ['-created_at']
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.TextField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    view_count = models.PositiveIntegerField(default=0)
    read_time = models.PositiveIntegerField(help_text='Estimated read time in minutes', default=5)
    author = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('article_detail', args=[str(self.slug)])
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'


class Comment(models.Model):
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f'Comment by {self.author} on {self.article.title}'
    
    def get_replies(self):
        return self.replies.filter(is_active=True)
    
    @property
    def is_reply(self):
        return self.parent is not None
def learning_resource_upload_path(instance, filename):
    """Generate file path for learning resource files"""
    ext = os.path.splitext(filename)[1]
    filename = f"resource_{instance.slug}{ext}"
    return f'learning_resources/resources/{filename}'

class LearningResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
        ('tutorial', 'Tutorial'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    resource_type = models.CharField(
        max_length=20, 
        choices=RESOURCE_TYPE_CHOICES, 
        default='article'
    )
    short_description = models.TextField(max_length=200)
    description = models.TextField(blank=True)
    
    # Content fields
    content = models.TextField(blank=True, help_text='Main content for articles/tutorials')
    video_url = models.URLField(
        blank=True, 
        null=True,
        validators=[validate_video_url],
        help_text='URL to video content (YouTube, Vimeo, etc.)'
    )
    video_embed_code = models.TextField(blank=True, editable=False)
    document = models.FileField(
        upload_to=learning_resource_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True,
        null=True,
        help_text='Upload PDF document (max 10MB)'
    )
    document_text = models.TextField(blank=True, editable=False)
    
    # Media
    image = models.ImageField(
        upload_to='learning_resources/covers/', 
        blank=True, 
        null=True,
        help_text='Cover image for the resource'
    )
    image_caption = models.CharField(max_length=200, blank=True, null=True)
    
    # Metadata
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft',
        db_index=True
    )
    view_count = models.PositiveIntegerField(default=0, db_index=True)
    read_time = models.PositiveIntegerField(
        help_text='Estimated read time in minutes', 
        default=5
    )
    
    # Relationships
    author = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='learning_resources'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Generate slug if not set
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Process video URL
        if self.video_url and self.video_url != getattr(self, '_original_video_url', None):
            self.video_embed_code = get_video_embed_code(self.video_url)
            self._original_video_url = self.video_url
        
        # Process PDF document
        if self.document and self.document != getattr(self, '_original_document', None):
            try:
                self.document_text = extract_text_from_pdf(self.document)
                self._original_document = self.document.name
                
                # If no description is set, use the first 200 chars of the PDF text
                if not self.description and self.document_text:
                    self.description = self.document_text[:200] + '...'
            except Exception as e:
                # If there's an error processing the PDF, don't fail the save
                print(f"Error processing PDF: {e}")
        
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validate that video and document aren't both set
        if self.video_url and self.document:
            raise ValidationError("Cannot have both a video URL and a document. Please choose one.")
        
        # Set resource type based on content
        if self.video_url:
            self.resource_type = 'video'
        elif self.document:
            self.resource_type = 'pdf'
    
    def increment_view_count(self):
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
    
    def get_absolute_url(self):
        return reverse('learning_resource_detail', args=[str(self.slug)])
    
    @property
    def is_video(self):
        return bool(self.video_url)
    
    @property
    def is_document(self):
        return bool(self.document)
    
    @property
    def file_extension(self):
        if self.document:
            return os.path.splitext(self.document.name)[1][1:].upper()
        return ''
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['resource_type', 'status']),
        ]
        verbose_name = 'Learning Resource'
        verbose_name_plural = 'Learning Resources'