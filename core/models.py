from django.db import models

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
        