from django.urls import path
from . import views

app_name = 'coding_challenges'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.ChallengeCreateView.as_view(), name='challenge_create'),
    path('list/', views.challenge_list, name='challenge_list'),
    path('tags/<slug:slug>/', views.challenge_list, name='challenge_list_by_tag'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('<slug:slug>/', views.challenge_detail, name='challenge_detail'),
    path('<slug:slug>/submit/', views.submit_solution, name='submit_solution'),

    # API endpoints for async execution
    path('api/run/', views.api_run_code, name='api_run_code'),
    path('api/submission/<str:token>/', views.api_submission_status, name='api_submission_status'),
    path('api/check-submission/<int:submission_id>/', views.check_submission_result, name='check_submission_result'),
    path('api/update-pending/', views.update_pending_submissions, name='update_pending_submissions'),
]
