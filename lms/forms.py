from django import forms
from .models import Course, InstructorProfile, Challenge, Lesson, Resource


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            'title', 'slug', 'description', 'difficulty', 'points',
            'active', 'start_at', 'end_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control rich-text-editor', 'rows': 6}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'order', 'video_url', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'content': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 10}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'description', 'curriculum', 'category', 'instructor',
            'image', 'is_paid', 'price', 'difficulty', 'published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 10}),
            'curriculum': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 12, 'placeholder': 'Outline your course curriculum here...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ['user', 'bio', 'avatar']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
