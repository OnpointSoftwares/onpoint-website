from django import forms
from .models import Submission, Challenge

LANG_CHOICES = (
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("javascript", "JavaScript"),
)

class SubmissionForm(forms.ModelForm):
    language = forms.ChoiceField(choices=LANG_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    code = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control font-monospace",
        "rows": 16,
        "spellcheck": "false",
        "placeholder": "Write your code here..."
    }))

    class Meta:
        model = Submission
        fields = ["language", "code"]


class ChallengeForm(forms.ModelForm):
    # Present JSON field as multiple checkboxes
    allowed_languages = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),  # populated in __init__
        label="Allowed languages",
        help_text="Select languages participants can use."
    )

    class Meta:
        model = Challenge
        fields = [
            "title", "slug", "difficulty", "tags",
            "problem_statement",
            "time_limit_ms", "memory_limit_kb", "allowed_languages",
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Two Sum'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated from title if blank'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'problem_statement': forms.Textarea(attrs={'class': 'form-control rich-text-editor', 'rows': 15, 'placeholder': 'Describe the problem, input/output format, constraints, and examples...'}),
            'time_limit_ms': forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'step': 50, 'placeholder': 'e.g., 2000'}),
            'memory_limit_kb': forms.NumberInput(attrs={'class': 'form-control', 'min': 32768, 'step': 1024, 'placeholder': 'e.g., 262144'}),
        }
        help_texts = {
            'slug': 'URL-friendly version of the title (auto-filled from the title).',
            'tags': 'Add relevant topics (e.g., Arrays, Hash Table, Two Pointers).',
            'time_limit_ms': 'Max execution time per test (ms). Default 2000.',
            'memory_limit_kb': 'Max memory per test (KB). Default 262,144 (~256 MB).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        defaults = getattr(Challenge, 'ALLOWED_LANGUAGES_DEFAULT', []) or []
        current = []
        if self.instance and self.instance.pk and isinstance(self.instance.allowed_languages, list):
            current = list(self.instance.allowed_languages)
        options = sorted(set(defaults + current))
        self.fields['allowed_languages'].choices = [(x, x.title()) for x in options]
        self.fields['allowed_languages'].initial = current or defaults
        if not self.instance or not self.instance.pk:
            self.fields['time_limit_ms'].initial = self.fields['time_limit_ms'].initial or 2000
            self.fields['memory_limit_kb'].initial = self.fields['memory_limit_kb'].initial or 262144

    def clean_allowed_languages(self):
        value = self.cleaned_data.get('allowed_languages')
        return list(value or [])

    def clean_time_limit_ms(self):
        val = self.cleaned_data.get('time_limit_ms')
        if val is None or val <= 0:
            raise forms.ValidationError('Time limit must be a positive number of milliseconds.')
        return val

    def clean_memory_limit_kb(self):
        val = self.cleaned_data.get('memory_limit_kb')
        if val is None or val < 32768:
            raise forms.ValidationError('Memory limit should be at least 32,768 KB (32 MB).')
        return val
