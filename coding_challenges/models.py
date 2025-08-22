from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Challenge(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    ALLOWED_LANGUAGES_DEFAULT = ['python', 'java', 'cpp', 'javascript']

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    problem_statement = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    example_input = models.TextField(blank=True)
    example_output = models.TextField(blank=True)
    time_limit_ms = models.PositiveIntegerField(default=2000)
    memory_limit_kb = models.PositiveIntegerField(default=262144)  # 256MB
    tags = models.ManyToManyField(Tag, blank=True, related_name='challenges')
    allowed_languages = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Code Challenge'
        verbose_name_plural = 'Code Challenges'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            i = 1
            while Challenge.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        if not self.allowed_languages:
            self.allowed_languages = self.ALLOWED_LANGUAGES_DEFAULT
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"


class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Bootstrap icon name or emoji")
    points_threshold = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cc_profile')
    points = models.IntegerField(default=0)
    badges = models.ManyToManyField(Badge, blank=True, related_name='profiles')
    solved_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Submission(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    )

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_submissions')
    language = models.CharField(max_length=20)
    code = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    score = models.FloatField(default=0.0)
    runtime_ms = models.PositiveIntegerField(default=0)
    memory_kb = models.PositiveIntegerField(default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    total_tests = models.PositiveIntegerField(default=0)
    result_raw = models.JSONField(default=dict, blank=True)
    external_token = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} -> {self.challenge} [{self.language}] {self.status}"


# Signals to auto-create Profile
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Submission)
def update_profile_stats_on_submission(sender, instance: Submission, created, **kwargs):
    if not created and instance.status in ['passed', 'failed', 'error'] or created:
        # update stats
        profile, _ = Profile.objects.get_or_create(user=instance.user)
        # simple points scheme: pass = +10, fail = +1, error = 0
        if instance.status == 'passed':
            profile.points += 10
        elif instance.status == 'failed':
            profile.points += 1
        profile.last_activity = timezone.now()
        # recompute solved_count
        solved_ids = (
            Submission.objects.filter(user=instance.user, status='passed')
            .values_list('challenge_id', flat=True)
            .distinct()
        )
        profile.solved_count = len(solved_ids)
        profile.save()

        # Auto-award badges based on thresholds
        for badge in Badge.objects.all():
            if profile.points >= badge.points_threshold and badge not in profile.badges.all():
                profile.badges.add(badge)

# Create your models here.
