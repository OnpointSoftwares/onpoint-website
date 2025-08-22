from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from lms.models import Category, InstructorProfile, Course, Lesson, Resource, Enrollment
from django.core.files.base import ContentFile
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dummy LMS data: instructors, categories, courses, lessons, and a student enrollment"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding LMS data..."))

        # Create users
        instructor1, created = User.objects.get_or_create(
            username="instructor1",
            defaults={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "instructor1@example.com",
            },
        )
        if created:
            instructor1.set_password("password123")
            instructor1.save()
            self.stdout.write(self.style.SUCCESS("Created user: instructor1 / password123"))
        else:
            self.stdout.write("User exists: instructor1")

        instructor2, created = User.objects.get_or_create(
            username="instructor2",
            defaults={
                "first_name": "Alan",
                "last_name": "Turing",
                "email": "instructor2@example.com",
            },
        )
        if created:
            instructor2.set_password("password123")
            instructor2.save()
            self.stdout.write(self.style.SUCCESS("Created user: instructor2 / password123"))
        else:
            self.stdout.write("User exists: instructor2")

        student1, created = User.objects.get_or_create(
            username="student1",
            defaults={
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "student1@example.com",
            },
        )
        if created:
            student1.set_password("password123")
            student1.save()
            self.stdout.write(self.style.SUCCESS("Created user: student1 / password123"))
        else:
            self.stdout.write("User exists: student1")

        # Create instructor profiles
        ip1, _ = InstructorProfile.objects.get_or_create(
            user=instructor1,
            defaults={
                "bio": "Ada is passionate about algorithms and education.",
            },
        )
        ip2, _ = InstructorProfile.objects.get_or_create(
            user=instructor2,
            defaults={
                "bio": "Alan teaches foundations of computer science.",
            },
        )
        self.stdout.write("Instructor profiles ensured.")

        # Categories
        cat_prog, _ = Category.objects.get_or_create(
            name="Programming",
            defaults={"slug": "programming"},
        )
        cat_data, _ = Category.objects.get_or_create(
            name="Data Science",
            defaults={"slug": "data-science"},
        )
        self.stdout.write("Categories ensured: Programming, Data Science")

        # Courses
        course_specs = [
            {
                "title": "Python for Beginners",
                "category": cat_prog,
                "instructor": ip1,
                "description": "Learn Python from scratch: syntax, data types, control flow, functions, and basic projects.",
                "is_paid": False,
                "price": 0,
                "difficulty": "beginner",
                "published": True,
                "rating_avg": 4.6,
            },
            {
                "title": "Intro to Machine Learning",
                "category": cat_data,
                "instructor": ip2,
                "description": "Fundamentals of ML: supervised learning, model evaluation, and hands-on with scikit-learn.",
                "is_paid": True,
                "price": 49.0,
                "difficulty": "intermediate",
                "published": True,
                "rating_avg": 4.8,
            },
        ]

        created_courses = []
        for spec in course_specs:
            slug = slugify(spec["title"])
            course, created_flag = Course.objects.get_or_create(
                title=spec["title"],
                defaults={
                    "slug": slug,
                    "category": spec["category"],
                    "instructor": spec["instructor"],
                    "description": spec["description"],
                    "is_paid": spec["is_paid"],
                    "price": spec["price"],
                    "difficulty": spec["difficulty"],
                    "published": spec["published"],
                    "rating_avg": spec.get("rating_avg", 4.5),
                },
            )
            created_courses.append(course)
            self.stdout.write(self.style.SUCCESS(f"Ensured course: {course.title} (created={created_flag})"))

            # Lessons
            if not course.lessons.exists():
                lessons = [
                    {
                        "title": "Welcome and Setup",
                        "order": 1,
                        "content": "Setting up your environment and tools.",
                        "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
                    },
                    {
                        "title": "Core Concepts",
                        "order": 2,
                        "content": "Core concepts explained with examples.",
                        "video_url": "https://www.youtube.com/embed/8ExtU3t4R8Y",
                    },
                    {
                        "title": "Project: Build Something",
                        "order": 3,
                        "content": "Apply what you've learned to a mini-project.",
                        "video_url": "https://www.youtube.com/embed/7eh4d6sabA0",
                    },
                ]
                for l in lessons:
                    lesson = Lesson.objects.create(
                        course=course,
                        title=l["title"],
                        order=l["order"],
                        content=l["content"],
                        video_url=l["video_url"],
                    )
                    # Course-level resources (since Resource is linked to Course)
                    # Create small placeholder files in memory
                    res1 = Resource.objects.create(
                        course=course,
                        title="Slides (PDF)",
                    )
                    res1.file.save(
                        f"slides-{course.slug}.pdf",
                        ContentFile(b"Dummy PDF content for slides."),
                        save=True,
                    )
                    res2 = Resource.objects.create(
                        course=course,
                        title="Source Code (zip)",
                    )
                    res2.file.save(
                        f"source-{course.slug}.zip",
                        ContentFile(b"Dummy zip content for source code."),
                        save=True,
                    )
                self.stdout.write(self.style.SUCCESS(f"Added lessons/resources to: {course.title}"))
            else:
                self.stdout.write(f"Lessons already exist for: {course.title}")

        # Enroll student into first course
        if created_courses:
            course0 = created_courses[0]
            Enrollment.objects.get_or_create(
                user=student1,
                course=course0,
                defaults={
                    "progress": random.randint(10, 60),
                    "created_at": timezone.now(),
                },
            )
            self.stdout.write(self.style.SUCCESS(f"Enrolled student1 into {course0.title}"))

        self.stdout.write(self.style.SUCCESS("LMS seed complete."))
