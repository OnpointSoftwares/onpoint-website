from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf.urls import handler403

# Custom 403 handler
def custom_permission_denied_view(request, exception=None):
    from django.shortcuts import render
    return render(request, '403.html', status=403)

handler403 = 'onpoint_site.urls.custom_permission_denied_view'

# Admin site settings
admin.site.site_header = 'OnPoint Admin'
admin.site.site_title = 'OnPoint Administration'
admin.site.index_title = 'Welcome to OnPoint Admin'

urlpatterns = [
    # Favicon redirect
    path('favicon.ico', RedirectView.as_view(url='/static/images/logo.png', permanent=True)),
    
    # Core app URLs (includes our custom admin)
    path('', include('core.urls')),
    
    # Auth URLs - Use the built-in auth views
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Redirect admin login to the custom login page
    path('admin/login/', RedirectView.as_view(url='/accounts/login/', permanent=True)),
    
    # Coding challenges app
    path('challenges/', include('coding_challenges.urls')),
    
    # LMS app
    path('lms/', include('lms.urls', namespace='lms')),
    
    # Website Templates app
    path('templates/', include('website_templates.urls', namespace='website_templates')),
    
    # Django admin (enabled for model management)
    path('django-admin/', admin.site.urls),
]

# Serve static files using Django in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, these should be served by your web server (Nginx/Apache)
    from django.views.static import serve
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
