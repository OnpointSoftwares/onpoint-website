from django.contrib import admin
from .models import Category, InstructorProfile, Course, Lesson, Resource, Enrollment, Quiz, Question, Submission, Review, Certificate, Badge, UserBadge, Challenge

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "instructor", "is_paid", "price", "published")
    list_filter = ("category", "is_paid", "published", "difficulty")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline, ResourceInline]

admin.site.register(Enrollment)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Submission)
admin.site.register(Review)
admin.site.register(Certificate)
admin.site.register(Badge)
admin.site.register(UserBadge)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "points", "active", "start_at", "end_at")
    list_filter = ("difficulty", "active")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
