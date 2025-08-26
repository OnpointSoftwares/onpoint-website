from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    bio = models.TextField(blank=True, help_text="Brief description about the instructor")
    avatar = models.ImageField(upload_to='lms/instructors/', blank=True, null=True)
    expertise = models.CharField(max_length=200, blank=True, help_text="Areas of expertise (comma-separated)")
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of teaching/industry experience")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    website_url = models.URLField(blank=True, help_text="Personal/professional website")
    is_verified = models.BooleanField(default=False, help_text="Verified instructor status")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def total_students(self):
        """Total number of students across all courses"""
        return sum(course.enrollments.count() for course in self.courses.all())
    
    @property
    def total_courses(self):
        """Total number of courses created"""
        return self.courses.count()
    
    @property
    def average_rating(self):
        """Average rating across all courses"""
        courses = self.courses.filter(rating_count__gt=0)
        if courses.exists():
            total_rating = sum(course.rating_avg * course.rating_count for course in courses)
            total_reviews = sum(course.rating_count for course in courses)
            return round(total_rating / total_reviews, 2) if total_reviews > 0 else 0
        return 0


class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, help_text="Brief course summary")
    curriculum = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses')
    image = models.ImageField(upload_to='lms/courses/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField(default=0, help_text="Estimated course duration in hours")
    prerequisites = models.TextField(blank=True, help_text="Course prerequisites")
    learning_outcomes = models.TextField(blank=True, help_text="What students will learn")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, help_text="Featured course")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)  # Keep for backward compatibility
    rating_avg = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['category', 'difficulty']),
        ]

    def __str__(self):
        return self.title
    
    @property
    def total_lessons(self):
        """Total number of lessons in the course"""
        return self.lessons.count()
    
    @property
    def total_duration_minutes(self):
        """Total estimated duration in minutes"""
        return self.duration_hours * 60
    
    @property
    def enrollment_count(self):
        """Total number of enrolled students"""
        return self.enrollments.count()
    
    @property
    def completion_rate(self):
        """Percentage of students who completed the course"""
        total_enrollments = self.enrollments.count()
        if total_enrollments == 0:
            return 0
        completed = self.enrollments.filter(completed=True).count()
        return round((completed / total_enrollments) * 100, 1)
    
    @property
    def is_published(self):
        """Check if course is published"""
        return self.status == 'published' and self.published
    
    def get_average_progress(self):
        """Get average progress across all enrollments"""
        enrollments = self.enrollments.all()
        if not enrollments:
            return 0
        total_progress = sum(enrollment.progress for enrollment in enrollments)
        return round(total_progress / len(enrollments), 1)


class Module(models.Model):
    """Course modules for organizing lessons into sections"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200, help_text="Module title (e.g., 'Introduction to Python')")
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of what this module covers")
    order = models.PositiveIntegerField(default=1, help_text="Order within the course")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Estimated module duration in minutes")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
        verbose_name = "Module"
        verbose_name_plural = "Modules"
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Module.objects.filter(course=self.course, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def total_lessons(self):
        """Total number of lessons in this module"""
        return self.lessons.count()
    
    @property
    def total_duration_minutes(self):
        """Total duration of all lessons in this module"""
        return self.lessons.aggregate(total=models.Sum('duration_minutes'))['total'] or 0
    
    @property
    def completion_rate(self):
        """Percentage of enrolled students who completed this module"""
        total_enrollments = self.course.enrollments.count()
        if total_enrollments == 0:
            return 0
        
        completed_count = 0
        for enrollment in self.course.enrollments.all():
            module_lessons = self.lessons.all()
            completed_lessons = enrollment.lesson_progress.filter(
                lesson__in=module_lessons, 
                completed=True
            ).count()
            if completed_lessons == module_lessons.count() and module_lessons.count() > 0:
                completed_count += 1
        
        return round((completed_count / total_enrollments) * 100, 1)


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = (
        ('video', 'Video'),
        ('text', 'Text/Reading'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True, help_text="Optional: Organize lesson into a module")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=1)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    video_url = models.URLField(blank=True, help_text="YouTube, Vimeo, or direct video URL")
    content = models.TextField(blank=True, help_text="Lesson content/description")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Lesson duration in minutes")
    is_preview = models.BooleanField(default=False, help_text="Allow preview without enrollment")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        # Allow lessons to be ordered within modules or directly in course
        unique_together = [['course', 'order'], ['module', 'order']]

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def completion_rate(self):
        """Percentage of enrolled students who completed this lesson"""
        total_enrollments = self.course.enrollments.count()
        if total_enrollments == 0:
            return 0
        completed = self.progress_records.filter(completed=True).count()
        return round((completed / total_enrollments) * 100, 1)


class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lms/resources/')

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(default=timezone.now)
    progress = models.FloatField(default=0)  # 0-100
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')


class LessonProgress(models.Model):
    """Tracks progress per user per lesson."""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    last_position = models.FloatField(default=0)  # seconds
    seconds_watched = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255, blank=True)
    choice_d = models.CharField(max_length=255, blank=True)
    correct_choice = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])


class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    taken_at = models.DateTimeField(default=timezone.now)


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    issued_at = models.DateTimeField(default=timezone.now)
    certificate_code = models.CharField(max_length=32, unique=True)


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=100, blank=True)  # could be a CSS class or image path


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(default=timezone.now)


class Challenge(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    points = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'LMS Challenge'
        verbose_name_plural = 'LMS Challenges'

    def __str__(self):
        return self.title
