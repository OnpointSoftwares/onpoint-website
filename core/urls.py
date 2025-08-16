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
    path('about/', views.about, name='about'),
    path('mobile-development/', views.mobile_development, name='mobile_development'),
    path('custom-software-development/', views.custom_software_development, name='custom_software_development'),
    path('web-development/', views.web_development, name='web_development'),
    path('github-readme/', views.github_readme, name='github_readme'),
    path('contact-us/', views.contact_us, name='contact_us'),
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
    
    # Public Article URLs
    path('blog/', views.public_article_list, name='article_list'),
    path('blog/<int:pk>/', views.article_detail, name='article_detail'),
    
    # Admin Article URLs
    path('admin/articles/', login_required(views.admin_article_list), name='admin_article_list'),
    path('admin/articles/create/', login_required(views.article_create), name='article_create'),
    path('admin/articles/<int:pk>/', login_required(views.admin_article_detail), name='admin_article_detail'),
    path('admin/articles/<int:pk>/update/', login_required(views.article_update), name='admin_article_update'),
    path('admin/articles/<int:pk>/delete/', login_required(views.article_delete), name='admin_article_delete'),
    path('admin/articles/<int:pk>/add-comment/', login_required(views.add_comment), name='add_comment'),
]
