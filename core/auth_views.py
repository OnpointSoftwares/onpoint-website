from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

class CustomLogoutView(LogoutView):
    """Custom logout view that adds a success message and redirects to home."""
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        # Add a success message
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

def custom_login_required(view_func):
    """Decorator that checks if the user is logged in and is staff."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
