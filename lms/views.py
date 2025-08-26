from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Course, Enrollment, InstructorProfile, Category, LessonProgress, Lesson, Module
from .forms import CourseForm, LessonForm, ResourceForm, ModuleForm


def is_instructor(user):
    return hasattr(user, 'instructor_profile')


def course_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category')
    price = request.GET.get('price')
    difficulty = request.GET.get('difficulty')
    sort = request.GET.get('sort', 'newest')

    courses = Course.objects.filter(published=True)
    if q:
        courses = courses.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        courses = courses.filter(category__slug=category)
    if price == 'free':
        courses = courses.filter(is_paid=False)
    elif price == 'paid':
        courses = courses.filter(is_paid=True)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    # Sorting
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'price',
        'price_high': '-price',
        'rating': '-rating_avg',
    }
    order_by = sort_map.get(sort, '-created_at')
    courses = courses.order_by(order_by)

    # Pagination
    paginator = Paginator(courses.select_related('instructor', 'category'), 9)
    page_param = request.GET.get('page', None)
    # Sanitize page: ensure positive integer, else None (defaults to 1)
    if page_param is not None:
        try:
            page_int = int(page_param)
            if page_int < 1:
                page_param = None
        except (TypeError, ValueError):
            page_param = None
    page_obj = paginator.get_page(page_param)

    categories = Category.objects.all()
    return render(request, 'lms/course_list.html', {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
        'categories': categories,
        'title': 'Courses',
        'sort': sort,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related('instructor', 'category'), slug=slug, published=True)
    return render(request, 'lms/course_detail.html', {
        'course': course,
        'title': course.title,
    })


@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    instructor = request.user.instructor_profile
    courses = Course.objects.filter(instructor=instructor).select_related('category').prefetch_related('enrollments')
    
    # Calculate dashboard statistics
    total_courses = courses.count()
    published_courses = courses.filter(status='published').count()
    draft_courses = courses.filter(status='draft').count()
    total_students = instructor.total_students
    total_revenue = sum(course.price * course.enrollment_count for course in courses if course.is_paid)
    
    # Recent enrollments (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=instructor,
        created_at__gte=thirty_days_ago
    ).count()
    
    # Course performance data
    course_stats = []
    for course in courses:
        course_stats.append({
            'course': course,
            'enrollments': course.enrollment_count,
            'completion_rate': course.completion_rate,
            'average_progress': course.get_average_progress(),
            'revenue': course.price * course.enrollment_count if course.is_paid else 0,
        })
    
    context = {
        'courses': courses,
        'course_stats': course_stats,
        'instructor': instructor,
        'stats': {
            'total_courses': total_courses,
            'published_courses': published_courses,
            'draft_courses': draft_courses,
            'total_students': total_students,
            'total_revenue': total_revenue,
            'recent_enrollments': recent_enrollments,
            'average_rating': instructor.average_rating,
        },
        'title': 'Instructor Dashboard'
    }
    
    return render(request, 'lms/instructor_dashboard.html', context)


@login_required
@user_passes_test(is_instructor)
def instructor_course_create(request):
    """Allow instructors to create a new course."""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        # Hide/ignore instructor field from form, set from current user
        form.fields.pop('instructor', None)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user.instructor_profile
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('lms:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
        form.fields.pop('instructor', None)

    return render(request, 'lms/course_form.html', {
        'form': form,
        'title': 'Create Course'
    })


@login_required
@user_passes_test(is_instructor)
def instructor_course_manage(request, slug):
    """Instructor-only management page for a course: add lessons, modules, and resources."""
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user.instructor_profile:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('lms:instructor_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_module':
            # Handle module creation
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            order = request.POST.get('order', 1)
            duration_minutes = request.POST.get('duration_minutes', 0)
            is_published = request.POST.get('is_published') == 'on'
            
            if title:
                try:
                    module = Module.objects.create(
                        course=course,
                        title=title,
                        description=description,
                        order=int(order) if order else 1,
                        duration_minutes=int(duration_minutes) if duration_minutes else 0,
                        is_published=is_published
                    )
                    messages.success(request, f'Module "{title}" created successfully!')
                except Exception as e:
                    messages.error(request, f'Error creating module: {str(e)}')
            else:
                messages.error(request, 'Module title is required.')
            return redirect('lms:instructor_course_manage', slug=course.slug)
            
        elif action == 'add_lesson':
            # Handle lesson creation
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            video_url = request.POST.get('video_url', '').strip()
            lesson_type = request.POST.get('lesson_type', 'video')
            module_id = request.POST.get('module')
            order = request.POST.get('order', 1)
            duration_minutes = request.POST.get('duration_minutes', 0)
            is_preview = request.POST.get('is_preview') == 'on'
            is_published = request.POST.get('is_published') == 'on'
            
            if title:
                try:
                    lesson_data = {
                        'course': course,
                        'title': title,
                        'content': content,
                        'video_url': video_url,
                        'lesson_type': lesson_type,
                        'order': int(order) if order else 1,
                        'duration_minutes': int(duration_minutes) if duration_minutes else 0,
                        'is_preview': is_preview,
                        'is_published': is_published
                    }
                    
                    # Add module if specified
                    if module_id:
                        try:
                            module = Module.objects.get(id=module_id, course=course)
                            lesson_data['module'] = module
                        except Module.DoesNotExist:
                            pass
                    
                    lesson = Lesson.objects.create(**lesson_data)
                    messages.success(request, f'Lesson "{title}" created successfully!')
                except Exception as e:
                    messages.error(request, f'Error creating lesson: {str(e)}')
            else:
                messages.error(request, 'Lesson title is required.')
            return redirect('lms:instructor_course_manage', slug=course.slug)
            
        elif action == 'add_resource':
            # Handle resource creation
            title = request.POST.get('title', '').strip()
            file = request.FILES.get('file')
            
            if title and file:
                try:
                    from .models import Resource
                    resource = Resource.objects.create(
                        course=course,
                        title=title,
                        file=file
                    )
                    messages.success(request, f'Resource "{title}" uploaded successfully!')
                except Exception as e:
                    messages.error(request, f'Error uploading resource: {str(e)}')
            else:
                messages.error(request, 'Resource title and file are required.')
            return redirect('lms:instructor_course_manage', slug=course.slug)
            
        elif action == 'delete_module':
            # Handle module deletion
            module_id = request.POST.get('module_id')
            if module_id:
                try:
                    module = Module.objects.get(id=module_id, course=course)
                    module_title = module.title
                    module.delete()
                    messages.success(request, f'Module "{module_title}" deleted successfully!')
                except Module.DoesNotExist:
                    messages.error(request, 'Module not found.')
                except Exception as e:
                    messages.error(request, f'Error deleting module: {str(e)}')
            return redirect('lms:instructor_course_manage', slug=course.slug)
            
        elif action == 'delete_lesson':
            # Handle lesson deletion
            lesson_id = request.POST.get('lesson_id')
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id, course=course)
                    lesson_title = lesson.title
                    lesson.delete()
                    messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
                except Lesson.DoesNotExist:
                    messages.error(request, 'Lesson not found.')
                except Exception as e:
                    messages.error(request, f'Error deleting lesson: {str(e)}')
            return redirect('lms:instructor_course_manage', slug=course.slug)

    # Get course data for template
    modules = course.modules.all().prefetch_related('lessons')
    unorganized_lessons = course.lessons.filter(module__isnull=True)
    resources = course.resources.all() if hasattr(course, 'resources') else []
    
    # Calculate course statistics
    total_lessons = course.lessons.count()
    total_modules = modules.count()
    total_duration = sum(lesson.duration_minutes for lesson in course.lessons.all())
    
    return render(request, 'lms/instructor_course_manage.html', {
        'course': course,
        'modules': modules,
        'unorganized_lessons': unorganized_lessons,
        'resources': resources,
        'total_lessons': total_lessons,
        'total_modules': total_modules,
        'total_duration': total_duration,
        'title': f"Manage: {course.title}"
    })


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'lms/student_dashboard.html', {'enrollments': enrollments, 'title': 'My Learning'})


def _recompute_enrollment_progress(enrollment: Enrollment):
    lessons = Lesson.objects.filter(course=enrollment.course).count()
    if lessons == 0:
        enrollment.progress = 0
        enrollment.completed = False
        enrollment.save(update_fields=['progress', 'completed'])
        return
    completed = LessonProgress.objects.filter(enrollment=enrollment, completed=True).count()
    pct = (completed / lessons) * 100.0
    enrollment.progress = round(pct, 2)
    enrollment.completed = completed == lessons
    enrollment.save(update_fields=['progress', 'completed'])


@login_required
def update_progress(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    course_slug = request.POST.get('course_slug')
    lesson_id = request.POST.get('lesson_id')
    last_position = request.POST.get('last_position')
    watched_delta = request.POST.get('watched_delta', '0')
    completed = request.POST.get('completed') == 'true'

    if not (course_slug and lesson_id and last_position is not None):
        return HttpResponseBadRequest('Missing parameters')

    course = get_object_or_404(Course, slug=course_slug)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    lp, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    try:
        lp.last_position = float(last_position)
        wd = max(0.0, float(watched_delta))
        lp.seconds_watched = max(lp.seconds_watched, lp.seconds_watched + wd)
        if completed:
            lp.completed = True
        lp.save()
    except ValueError:
        return HttpResponseBadRequest('Invalid numeric values')

    _recompute_enrollment_progress(enrollment)
    return JsonResponse({'ok': True, 'progress': enrollment.progress, 'lesson_completed': lp.completed})


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, 'Enrolled successfully!')
    return redirect('lms:course_learn', slug=course.slug)


@login_required
def course_learn(request, slug):
    course = get_object_or_404(Course, slug=slug)
    # Ensure the user is enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You must enroll to access the course.')
        return redirect('lms:course_detail', slug=slug)
    return render(request, 'lms/course_learn.html', {'course': course, 'title': f"Learn: {course.title}"})


# Lesson edit/delete for instructors
@login_required
@user_passes_test(is_instructor)
def instructor_lesson_edit(request, slug, pk):
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user.instructor_profile:
        messages.error(request, 'You do not have permission to edit lessons for this course.')
        return redirect('lms:instructor_dashboard')

    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson, prefix='lesson')
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('lms:instructor_course_manage', slug=course.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LessonForm(instance=lesson, prefix='lesson')

    return render(request, 'lms/lesson_form.html', {
        'title': f"Edit Lesson: {lesson.title}",
        'course': course,
        'form': form,
        'lesson': lesson,
    })


@login_required
@user_passes_test(is_instructor)
def instructor_lesson_delete(request, slug, pk):
    course = get_object_or_404(Course, slug=slug)
    if course.instructor != request.user.instructor_profile:
        messages.error(request, 'You do not have permission to delete lessons for this course.')
        return redirect('lms:instructor_dashboard')

    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('lms:instructor_course_manage', slug=course.slug)

    return render(request, 'lms/lesson_confirm_delete.html', {
        'title': f"Delete Lesson: {lesson.title}",
        'course': course,
        'lesson': lesson,
    })
