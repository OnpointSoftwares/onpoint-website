from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('chat/', views.chat_api, name='chat_api'),
    
    # Authentication URLs
    path('admin/login/', auth_views.LoginView.as_view(
        template_name='admin/login.html',
        redirect_authenticated_user=True,
        extra_context={'title': 'Login'}
    ), name='admin_login'),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='home'), name='admin_logout'),
    
    # Admin Dashboard URLs
    path('admin/', login_required(views.AdminDashboardView.as_view()), name='admin_dashboard'),
    
    # Project Management URLs
    path('admin/projects/', login_required(views.ProjectListView.as_view()), name='project_list'),
    path('admin/projects/create/', login_required(views.ProjectCreateView.as_view()), name='project_create'),
    path('admin/projects/<int:pk>/', login_required(views.ProjectDetailView.as_view()), name='project_detail'),
    path('admin/projects/<int:pk>/update/', login_required(views.ProjectUpdateView.as_view()), name='project_update'),
    path('admin/projects/<int:pk>/delete/', login_required(views.ProjectDeleteView.as_view()), name='project_delete'),
    path('admin/projects/<int:pk>/update-status/', login_required(views.ProjectStatusUpdateView.as_view()), 
         name='project_update_status'),
    
    # AJAX/API Endpoints
    path('admin/api/project-stats/', login_required(views.ProjectStatsAPIView.as_view()), name='api_project_stats'),
    path('admin/api/recent-projects/', login_required(views.RecentProjectsAPIView.as_view()), name='api_recent_projects'),
]
