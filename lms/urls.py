from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('instructor/courses/<slug:slug>/manage/', views.instructor_course_manage, name='instructor_course_manage'),
    path('instructor/courses/<slug:slug>/lessons/<int:pk>/edit/', views.instructor_lesson_edit, name='instructor_lesson_edit'),
    path('instructor/courses/<slug:slug>/lessons/<int:pk>/delete/', views.instructor_lesson_delete, name='instructor_lesson_delete'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/courses/create/', views.instructor_course_create, name='instructor_course_create'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('api/progress/', views.update_progress, name='update_progress'),
]
