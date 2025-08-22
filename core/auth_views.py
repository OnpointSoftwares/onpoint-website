from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy, reverse
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

class CustomLoginView(LoginView):
    """Custom login view with role-based redirects."""
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # Admins (superuser or staff) -> Admin dashboard
        if user.is_superuser or user.is_staff:
            return reverse('admin_dashboard')
        # Instructors -> Instructor dashboard
        try:
            if hasattr(user, 'instructor_profile') and user.instructor_profile is not None:
                return reverse('lms:instructor_dashboard')
        except Exception:
            pass
        # Normal users -> Home
        return reverse('home')
