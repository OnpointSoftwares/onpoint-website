from django import forms
from .models import Project, Article, Comment
from django.core.exceptions import ValidationError
import re
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title (e.g., E-commerce Platform)'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL-friendly version (e.g., ecommerce-platform)'
            }),
            'short_description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Brief description of the project (2-3 sentences)'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6, 
                'class': 'form-control',
                'placeholder': 'Detailed project description, features, and objectives...'
            }),
            'client': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Client or company name (optional)'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://client-website.com (optional)'
            }),
            'technologies': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Django, React, PostgreSQL, AWS, Docker...'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/repository (optional)'
            }),
            'live_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://live-project-url.com (optional)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'Project Title',
            'slug': 'URL Slug',
            'category': 'Project Category',
            'short_description': 'Short Description',
            'description': 'Detailed Description',
            'client': 'Client Name',
            'website': 'Client Website',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'status': 'Project Status',
            'featured': 'Featured Project',
            'technologies': 'Technologies Used',
            'image': 'Project Image',
            'thumbnail': 'Thumbnail Image',
            'github_url': 'GitHub Repository',
            'live_url': 'Live Project URL',
        }
        help_texts = {
            'slug': 'URL-friendly version of the title (auto-generated if left empty)',
            'short_description': 'Brief summary displayed on project cards (max 200 characters)',
            'description': 'Detailed project information, features, and technical details',
            'client': 'Name of the client or organization (optional)',
            'website': 'Client\'s official website URL (optional)',
            'technologies': 'Comma-separated list of technologies, frameworks, and tools used',
            'start_date': 'When the project development started',
            'end_date': 'When the project was completed (leave empty if ongoing)',
            'featured': 'Check to display this project on the home page portfolio section',
            'image': 'Main project image (recommended: 1200x800px)',
            'thumbnail': 'Smaller version for listings (auto-generated if not provided)',
            'github_url': 'Link to the project\'s source code repository (optional)',
            'live_url': 'Link to the live/deployed project (optional)',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set field requirements
        optional_fields = ['website', 'github_url', 'live_url', 'thumbnail', 'end_date', 'client', 'image', 'slug']
        for field_name, field in self.fields.items():
            if field_name in optional_fields:
                field.required = False
            
            # Add Bootstrap classes and styling
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    if isinstance(field.widget, forms.CheckboxInput):
                        field.widget.attrs['class'] = 'form-check-input'
                    elif isinstance(field.widget, forms.Select):
                        field.widget.attrs['class'] = 'form-select'
                    else:
                        field.widget.attrs['class'] = 'form-control'
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slug.strip()
            if slug == '':
                return None  # Will be auto-generated
            # Check for uniqueness (excluding current instance if updating)
            queryset = Project.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('A project with this slug already exists.')
        return slug
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError('Project title is required.')
        return title.strip()
    
    def clean_technologies(self):
        technologies = self.cleaned_data.get('technologies')
        if not technologies or technologies.strip() == '':
            raise forms.ValidationError('Please specify at least one technology.')
        return technologies.strip()

class ProjectFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + Project.STATUS_CHOICES
    CATEGORY_CHOICES = [('', 'All Categories')] + Project.PROJECT_CATEGORIES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects...'
        })
    )
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'required': 'required'
            })
        }
        labels = {
            'text': 'Comment',
        }
        help_texts = {
            'text': 'Your comment will be visible after moderation.'
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Add is_active field for staff users only
        if self.request and self.request.user.is_staff:
            self.fields['is_active'] = forms.BooleanField(
                required=False,
                initial=True,
                label='Approve this comment',
                help_text='Uncheck to hold for moderation',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input',
                    'role': 'switch'
                })
            )
    
    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 10:
            raise ValidationError('Comment is too short. Please provide more details.')
        if len(text) > 2000:
            raise ValidationError('Comment is too long. Maximum 2000 characters allowed.')
        
        # Check for spam-like patterns
        spam_keywords = ['http://', 'https://', 'www.', '.com', '.net', '.org']
        if any(keyword in text.lower() for keyword in spam_keywords):
            self.cleaned_data['is_active'] = False
            
        return text
    
    def save(self, commit=True, *args, **kwargs):
        comment = super().save(commit=False)
        
        # Set the author if user is authenticated
        if self.request and self.request.user.is_authenticated:
            comment.author = self.request.user
        
        # Set is_active based on staff approval or spam detection
        if 'is_active' in self.cleaned_data:
            comment.is_active = self.cleaned_data['is_active']
        elif self.request and self.request.user.is_staff:
            # Default to True for staff if not set
            comment.is_active = True
        else:
            # For non-staff, default to False (needs moderation)
            comment.is_active = False
        
        if commit:
            comment.save()
        
        return comment
        return email


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'short_description', 'description', 'image', 'image_caption', 'status', 'read_time', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter article title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated-from-title'}),
            'short_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Brief description for SEO and previews'}),
            'description': forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'placeholder': 'Article content...'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'image_caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'read_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '60'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make slug field optional (will be auto-generated)
        self.fields['slug'].required = False
        self.fields['author'].required = False
        self.fields['image'].required = False
        self.fields['image_caption'].required = False
        
        # Add help text
        self.fields['slug'].help_text = 'Leave blank to auto-generate from title'
        self.fields['short_description'].help_text = 'Brief description for SEO and article previews'
        self.fields['status'].help_text = 'Set to "Published" to make this article visible to the public'
        self.fields['read_time'].help_text = 'Estimated reading time in minutes'