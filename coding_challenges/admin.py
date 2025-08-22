from django.contrib import admin
from django import forms
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from .models import Challenge, Submission, Tag, Badge, Profile


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ChallengeAdminForm(forms.ModelForm):
    # Expose JSON allowed_languages as multiple checkboxes for convenience
    allowed_languages = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),  # populated in __init__
        label="Allowed languages",
        help_text="Select languages participants can use."
    )

    class Meta:
        model = Challenge
        fields = "__all__"
        widgets = {
            # Apply class for TinyMCE to problem_statement only
            'problem_statement': forms.Textarea(attrs={'class': 'rich-text-editor', 'rows': 15, 'placeholder': 'Describe the problem, input/output format, constraints, and examples...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Two Sum'}),
            'slug': forms.TextInput(attrs={'placeholder': 'auto-generated from title if blank'}),
            'time_limit_ms': forms.NumberInput(attrs={'min': 100, 'step': 50, 'placeholder': 'e.g., 2000'}),
            'memory_limit_kb': forms.NumberInput(attrs={'min': 32768, 'step': 1024, 'placeholder': 'e.g., 262144'}),
        }
        help_texts = {
            'title': 'A clear, concise problem title.',
            'slug': 'URL-friendly version of the title (auto-filled from the title).',
            'difficulty': 'Select the difficulty level for this challenge.',
            'tags': 'Add relevant topics (e.g., Arrays, Hash Table, Two Pointers).',
            'problem_statement': 'Use headings, lists, and code formatting. Include input/output format and examples.',
            'time_limit_ms': 'Maximum execution time per test in milliseconds. Default 2000 ms.',
            'memory_limit_kb': 'Maximum memory per test in KB. Default 262,144 KB (~256 MB).',
            'allowed_languages': 'Select the programming languages participants can use.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        defaults = getattr(Challenge, 'ALLOWED_LANGUAGES_DEFAULT', []) or []
        current = []
        if self.instance and self.instance.pk and isinstance(self.instance.allowed_languages, list):
            current = list(self.instance.allowed_languages)
        # Build options from defaults + any current values
        options = sorted(set(defaults + current))
        self.fields['allowed_languages'].choices = [(x, x.title()) for x in options]
        self.fields['allowed_languages'].initial = current or defaults
        # Sensible defaults for new objects
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


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    fields = ("user", "language", "status", "score", "runtime_ms", "created_at")
    readonly_fields = ("user", "language", "status", "score", "runtime_ms", "created_at")
    can_delete = False
    ordering = ("-created_at",)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    form = ChallengeAdminForm
    inlines = [SubmissionInline]

    # List view
    list_display = ("title", "difficulty", "submissions_count", "created_at", "view_on_site")
    list_display_links = ("title",)
    list_editable = ("difficulty",)
    list_filter = ("difficulty", "tags")
    search_fields = ("title", "problem_statement")
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)

    # Form layout
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            'fields': ("title", "slug", "difficulty", "tags"),
        }),
        ("Problem", {
            'fields': ("problem_statement",),
            'description': "Use the rich text editor to format the problem statement.",
        }),
        ("Constraints & Settings", {
            'fields': ("time_limit_ms", "memory_limit_kb", "allowed_languages"),
            'description': 'Execution constraints and language availability.',
        }),
        ("Timestamps", {
            'fields': ("created_at", "updated_at"),
        }),
    )
    save_as = True
    list_per_page = 25

    # Admin actions
    actions = [
        "make_easy", "make_medium", "make_hard",
        "reset_limits_default",
    ]

    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = "Submissions"

    def view_on_site(self, obj):
        url = reverse('coding_challenges:challenge_detail', kwargs={'slug': obj.slug})
        return format_html('<a href="{}" target="_blank">View</a>', url)
    view_on_site.short_description = "View"

    # Bulk actions implementations
    def make_easy(self, request, queryset):
        updated = queryset.update(difficulty='easy')
        self.message_user(request, f"Updated {updated} challenges to Easy.")
    make_easy.short_description = "Set difficulty to Easy"

    def make_medium(self, request, queryset):
        updated = queryset.update(difficulty='medium')
        self.message_user(request, f"Updated {updated} challenges to Medium.")
    make_medium.short_description = "Set difficulty to Medium"

    def make_hard(self, request, queryset):
        updated = queryset.update(difficulty='hard')
        self.message_user(request, f"Updated {updated} challenges to Hard.")
    make_hard.short_description = "Set difficulty to Hard"

    def reset_limits_default(self, request, queryset):
        updated = queryset.update(time_limit_ms=2000, memory_limit_kb=262144)
        self.message_user(request, f"Reset limits for {updated} challenges.")
    reset_limits_default.short_description = "Reset time/memory limits to defaults"

    # Load TinyMCE from CDN and local init script
    class Media:
        js = (
            "https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js",
            "admin/js/tinymce_init.js",
        )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "challenge", "language", "status", "score", "created_at")
    list_filter = ("status", "language")
    search_fields = ("user__username", "challenge__title")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "points_threshold", "icon")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "solved_count", "last_activity")

# Register your models here.
