from django import forms
from .models import Course, InstructorProfile, Challenge, Lesson, Resource, Module


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


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'duration_minutes', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module title (e.g., Introduction to Python)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of what this module covers...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Module order'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Estimated duration in minutes'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'title': 'Give your module a clear, descriptive title',
            'description': 'Briefly describe what students will learn in this module',
            'order': 'Order of this module within the course',
            'duration_minutes': 'Estimated time to complete all lessons in this module',
            'is_published': 'Uncheck to hide this module from students',
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'module', 'order', 'lesson_type', 'video_url', 'content', 'duration_minutes', 'is_preview', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lesson title'}),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Lesson order'}),
            'lesson_type': forms.Select(attrs={'class': 'form-select'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube, Vimeo, or direct video URL'}),
            'content': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 8, 'placeholder': 'Lesson content and description...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Duration in minutes'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'module': 'Optional: Assign this lesson to a module for better organization',
            'lesson_type': 'Type of lesson content',
            'video_url': 'For video lessons, provide the video URL',
            'duration_minutes': 'Estimated time to complete this lesson',
            'is_preview': 'Allow students to preview this lesson without enrollment',
            'is_published': 'Uncheck to hide this lesson from students',
        }
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            # Only show modules from the current course
            self.fields['module'].queryset = Module.objects.filter(course=course)
            self.fields['module'].empty_label = "No Module (Direct to Course)"


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
            'title', 'slug', 'short_description', 'description', 'curriculum', 
            'category', 'instructor', 'image', 'duration_hours', 'prerequisites',
            'learning_outcomes', 'is_paid', 'price', 'difficulty', 'status', 'featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated-from-title'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description for course cards and previews...'}),
            'description': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 10, 'placeholder': 'Detailed course description...'}),
            'curriculum': forms.Textarea(attrs={'class': 'form-control richtext', 'rows': 12, 'placeholder': 'Outline your course curriculum here...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Total course duration in hours'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List any prerequisites or requirements...'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What will students learn? List key outcomes...'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'placeholder': '0.00'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        help_texts = {
            'slug': 'Leave empty to auto-generate from title',
            'short_description': 'Brief summary shown in course listings',
            'duration_hours': 'Estimated total time to complete the course',
            'prerequisites': 'Skills or knowledge students should have before taking this course',
            'learning_outcomes': 'What students will be able to do after completing this course',
            'status': 'Course publication status',
            'featured': 'Featured courses are highlighted in course listings',
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
