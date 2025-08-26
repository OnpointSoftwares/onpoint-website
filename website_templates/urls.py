from django.urls import path
from . import views

app_name = 'website_templates'

urlpatterns = [
    path('', views.template_list, name='template_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:slug>/', views.template_detail, name='template_detail'),
    path('<slug:slug>/download/', views.increment_download, name='increment_download'),
    path('<slug:slug>/toggle-featured/', views.toggle_featured, name='toggle_featured'),
    path('<slug:slug>/toggle-active/', views.toggle_active, name='toggle_active'),
]
