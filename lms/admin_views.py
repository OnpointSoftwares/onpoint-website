from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.contrib import messages

from core.urls import staff_required  # reuse existing decorator
from .models import Course, InstructorProfile, Challenge
from .forms import CourseForm, InstructorProfileForm, ChallengeForm


# Challenges
@staff_required
def admin_challenge_list(request):
    q = request.GET.get('q', '')
    challenges = Challenge.objects.all()
    if q:
        challenges = challenges.filter(title__icontains=q)
    challenges = challenges.order_by('-created_at')
    page_obj = Paginator(challenges, 12).get_page(request.GET.get('page'))
    return render(request, 'admin/lms/challenge_list.html', {
        'page_obj': page_obj,
        'q': q,
    })


@staff_required
def admin_challenge_detail(request, pk):
    """Admin detail view for a single challenge with quick actions."""
    challenge = get_object_or_404(Challenge, pk=pk)
    # Quick toggle active via ?action=toggle
    action = request.GET.get('action')
    if action == 'toggle':
        challenge.active = not challenge.active
        challenge.save(update_fields=['active'])
        messages.success(request, f"Challenge marked as {'Active' if challenge.active else 'Inactive'}.")
        return redirect('admin_challenge_detail', pk=challenge.pk)

    return render(request, 'admin/lms/challenge_detail.html', {
        'challenge': challenge,
    })


@staff_required
def admin_challenge_create(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Challenge created successfully.')
            return redirect('admin_challenge_list')
    else:
        form = ChallengeForm()
    return render(request, 'admin/lms/challenge_form.html', {'form': form, 'title': 'Create Challenge'})


@staff_required
def admin_challenge_update(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Challenge updated successfully.')
            return redirect('admin_challenge_list')
    else:
        form = ChallengeForm(instance=challenge)
    return render(request, 'admin/lms/challenge_form.html', {'form': form, 'title': 'Update Challenge'})


@staff_required
def admin_challenge_delete(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == 'POST':
        challenge.delete()
        messages.success(request, 'Challenge deleted successfully.')
        return redirect('admin_challenge_list')
    return render(request, 'admin/confirm_delete.html', {
        'object': challenge,
        'cancel_url': 'admin_challenge_list',
        'title': 'Delete Challenge'
    })


# Courses
@staff_required
def admin_course_list(request):
    q = request.GET.get('q', '')
    courses = Course.objects.select_related('instructor', 'category')
    if q:
        courses = courses.filter(title__icontains=q)
    page_obj = Paginator(courses.order_by('-created_at'), 12).get_page(request.GET.get('page'))
    return render(request, 'admin/lms/course_list.html', {'page_obj': page_obj, 'q': q})


@staff_required
def admin_course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('admin_course_list')
    else:
        form = CourseForm()
    return render(request, 'admin/lms/course_form.html', {'form': form, 'title': 'Create Course'})


@staff_required
def admin_course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('admin_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin/lms/course_form.html', {'form': form, 'title': 'Update Course'})


# Delete Course
@staff_required
def admin_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('admin_course_list')
    return render(request, 'admin/confirm_delete.html', {
        'object': course,
        'cancel_url': 'admin_course_list',
        'title': 'Delete Course'
    })


# Instructors
@staff_required
def admin_instructor_list(request):
    q = request.GET.get('q', '')
    instructors = InstructorProfile.objects.select_related('user')
    if q:
        instructors = instructors.filter(user__username__icontains=q)
    page_obj = Paginator(instructors.order_by('user__username'), 12).get_page(request.GET.get('page'))
    return render(request, 'admin/lms/instructor_list.html', {'page_obj': page_obj, 'q': q})


@staff_required
def admin_instructor_create(request):
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instructor created successfully.')
            return redirect('admin_instructor_list')
    else:
        form = InstructorProfileForm()
    return render(request, 'admin/lms/instructor_form.html', {'form': form, 'title': 'Create Instructor'})


@staff_required
def admin_instructor_update(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, request.FILES, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instructor updated successfully.')
            return redirect('admin_instructor_list')
    else:
        form = InstructorProfileForm(instance=instructor)
    return render(request, 'admin/lms/instructor_form.html', {'form': form, 'title': 'Update Instructor'})


# Delete Instructor
@staff_required
def admin_instructor_delete(request, pk):
    instructor = get_object_or_404(InstructorProfile, pk=pk)
    if request.method == 'POST':
        instructor.delete()
        messages.success(request, 'Instructor deleted successfully.')
        return redirect('admin_instructor_list')
    return render(request, 'admin/confirm_delete.html', {
        'object': instructor,
        'cancel_url': 'admin_instructor_list',
        'title': 'Delete Instructor'
    })
