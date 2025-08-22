from django.urls import path
from . import admin_views as views

urlpatterns = [
    # Challenges
    path('challenges/', views.admin_challenge_list, name='admin_challenge_list'),
    path('challenges/<int:pk>/', views.admin_challenge_detail, name='admin_challenge_detail'),
    path('challenges/create/', views.admin_challenge_create, name='admin_challenge_create'),
    path('challenges/<int:pk>/update/', views.admin_challenge_update, name='admin_challenge_update'),
    path('challenges/<int:pk>/delete/', views.admin_challenge_delete, name='admin_challenge_delete'),

    # Courses
    path('courses/', views.admin_course_list, name='admin_course_list'),
    path('courses/create/', views.admin_course_create, name='admin_course_create'),
    path('courses/<int:pk>/update/', views.admin_course_update, name='admin_course_update'),
    path('courses/<int:pk>/delete/', views.admin_course_delete, name='admin_course_delete'),

    # Instructors
    path('instructors/', views.admin_instructor_list, name='admin_instructor_list'),
    path('instructors/create/', views.admin_instructor_create, name='admin_instructor_create'),
    path('instructors/<int:pk>/update/', views.admin_instructor_update, name='admin_instructor_update'),
    path('instructors/<int:pk>/delete/', views.admin_instructor_delete, name='admin_instructor_delete'),
]
