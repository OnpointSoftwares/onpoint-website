from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Django, React, PostgreSQL, ...'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except optional ones
        for field_name, field in self.fields.items():
            if field_name in ['website', 'github_url', 'live_url', 'thumbnail', 'end_date', 'client']:
                field.required = False
            else:
                field.required = True
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

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
    
    featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects...'
        })
    )
