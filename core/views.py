from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Case, When, Value, IntegerField, F, Sum
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.urls import reverse_lazy
import google.generativeai as genai
import os
import json
from datetime import timedelta
from .models import Contact, Project, Article,LearningResource
from .forms import ProjectForm, ProjectFilterForm, ArticleForm

def get_gemini_chat():
    try:
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            print("GEMINI_API_KEY not found in settings")
            return None
            
        genai.configure(api_key="AIzaSyD4IVtZuOp8k2wwN7O5Ao5-0FGS7CaU0dA")
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat(history=[])
        
        CHAT_INSTRUCTIONS = """
        You are OnPoint Software's AI assistant. You help users with information about OnPoint Software's services.
        
        About OnPoint Software:
        - Custom software development
        - Website design & development
        - Mobile app development
        - GitHub README writing & editing
        - 7+ years of experience
        
        Company Information:
        - Email: onpointinfo635@gmail.com
        - Phone: +254 702 502 952
        
        Be helpful, professional, and concise in your responses.
        If you don't know an answer, say you'll have someone from the team contact them.
        """
        
        # Initialize chat with instructions
        chat.send_message(CHAT_INSTRUCTIONS)
        return chat
        
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save to database
        contact = Contact(name=name, email=email, message=message)
        contact.save()
        
        # Send email
        try:
            send_mail(
                f'New Contact Form Submission from {name}',
                f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        except Exception as e:
            print(f"Error sending email: {e}")
            messages.error(request, 'There was an error sending your message. Please try again later.')
        
        return redirect('home')
    
    # Get featured projects for portfolio section
    featured_projects = Project.objects.filter(featured=False, status__in=['completed', 'launched']).order_by('-created_at')[:6]
    
    # Get all completed/launched projects for stats
    all_projects = Project.objects.filter(status__in=['completed', 'launched'])
    
    # Get the 3 most recent articles for blog section
    latest_articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    
    # Calculate dynamic stats
    stats = {
        'years_experience': 5,  # You can make this dynamic based on your start date
        'projects_delivered': all_projects.count(),
        'client_satisfaction': 98,  # You can calculate this from testimonials/ratings
        'team_members': 8,  # Update based on your actual team size
    }
    
    context = {
        'projects': featured_projects,
        'stats': stats,
        'latest_articles': latest_articles,
    }
    for project in featured_projects:
        print(project)
    return render(request, 'core/home.html', context)
def about(request):
    return render(request, 'core/about-us.html')
def mobile_development(request):
    return render(request, 'core/mobile-development.html')
def custom_software_development(request):
    return render(request, 'core/custom-software-development.html')
def web_development(request):
    return render(request, 'core/web-development.html')
def github_readme(request):
    return render(request, 'core/github-readme.html')
def contact_us(request):
    return render(request, 'core/contact-us.html')
from django.views.decorators.csrf import ensure_csrf_cookie

@require_http_methods(["POST"])
@ensure_csrf_cookie
def chat_api(request):
    if not request.body:
        return JsonResponse({'error': 'No data provided'}, status=400)
    
    try:
        # Get the message from the request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
        else:
            user_message = request.POST.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Get or create chat session
        chat = get_gemini_chat()
        if not chat:
            return JsonResponse({
                'response': 'Chat service is currently unavailable. Please contact us directly at onpointinfo635@gmail.com',
                'error': 'Gemini not initialized',
                'status': 'error'
            }, status=503)
        
        # Get response from Gemini
        response = chat.send_message(user_message)
        
        return JsonResponse({
            'response': response.text,
            'status': 'success',
            'csrf_token': request.META.get('CSRF_COOKIE', '')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        error_message = str(e)
        print(f"Error in chat_api: {error_message}")
        
        # Handle specific Gemini API errors
        if "quota" in error_message.lower():
            return JsonResponse({
                'response': 'Our chat service is currently experiencing high demand. Please try again later or contact us directly at onpointinfo635@gmail.com',
                'error': 'API quota exceeded',
                'status': 'error'
            }, status=429)
            
        return JsonResponse({
            'response': 'Sorry, I encountered an error. Please try again later or contact us directly at onpointinfo635@gmail.com',
            'error': error_message,
            'status': 'error'
        }, status=500)

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyBXVv3tklwuNRpH82WbP-bLyNAVQA-kvYo")
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    CHAT_INSTRUCTIONS = """
    You are OnPoint Software's AI assistant. You help users with information about OnPoint Software's services and pricing.
    
    About OnPoint Software:
    - Custom software development
    - Website design & development
    - Mobile app development
    - GitHub README writing & editing
    - 7+ years of experience
    
    Service Pricing (in Kenyan Shillings):
    
    Base Project Prices:
    - Basic Website: KES 5,000 (1-5 pages)
    - Web Application: Starting from KES 25,000
    - Mobile App: Starting from KES 40,000
    - E-commerce: Starting from KES 60,000
    - Custom Software: Starting from KES 75,000
    
    Design Complexity Multipliers:
    - Basic (Template-based): 1x base price
    - Standard (Semi-custom): 1.5x base price
    - Premium (Fully Custom): 2.5x base price
    
    Additional Features (Add-ons):
    - SEO Optimization: +KES 5,000
    - Responsive Design: +KES 3,000
    - Content Management System: +KES 10,000
    - E-commerce Functionality: +KES 15,000
    
    Note: All prices are in Kenyan Shillings (KES) and include a 15% startup discount.
    
    Be helpful, professional, and concise in your responses.
    If you don't know an answer, say you'll have someone from the team contact them.
    When discussing pricing, always mention that final quotes may vary based on specific project requirements.
    """
    
    # Initialize chat with instructions
    chat.send_message(CHAT_INSTRUCTIONS)
    
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    model = None
    chat = None

# Duplicate home function removed - using the first home function with projects


# Admin Views
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is staff member"""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseForbidden("You don't have permission to access this page.")


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """Admin dashboard view showing project statistics and recent activities"""
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Project statistics
        projects = Project.objects.all()
        total_projects = projects.count()
        active_projects = projects.filter(status__in=['in_progress', 'on_hold']).count()
        completed_projects = projects.filter(status__in=['completed', 'launched']).count()
        planning_projects = projects.filter(status='planning').count()
        
        # Project status distribution with proper formatting
        status_stats = {}
        for status_code, status_label in Project.STATUS_CHOICES:
            count = projects.filter(status=status_code).count()
            percentage = (count * 100.0 / total_projects) if total_projects > 0 else 0
            status_stats[status_code] = {
                'count': count,
                'percentage': percentage,
                'label': status_label
            }
        
        # Article statistics
        articles = Article.objects.all()
        total_articles = articles.count()
        published_articles = articles.filter(status='published').count()
        draft_articles = articles.filter(status='draft').count()
        total_views = articles.aggregate(total_views=Sum('view_count'))['total_views'] or 0
        
        # Recent activities
        recent_projects = projects.order_by('-created_at')[:5]
        recent_articles = articles.order_by('-created_at')[:5]
        
        # Monthly statistics (last 30 days)
        from datetime import datetime, timedelta
        last_month = datetime.now() - timedelta(days=30)
        
        new_projects_month = projects.filter(created_at__gte=last_month).count()
        new_articles_month = articles.filter(created_at__gte=last_month).count()
        
        # Growth calculations
        projects_growth = 0
        articles_growth = 0
        if total_projects > 0:
            projects_growth = (new_projects_month * 100.0 / total_projects)
        if total_articles > 0:
            articles_growth = (new_articles_month * 100.0 / total_articles)
        
        context.update({
            # Project stats
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'planning_projects': planning_projects,
            'status_stats': status_stats,
            'recent_projects': recent_projects,
            
            # Article stats
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'recent_articles': recent_articles,
            
            # Growth stats
            'new_projects_month': new_projects_month,
            'new_articles_month': new_articles_month,
            'projects_growth': round(projects_growth, 1),
            'articles_growth': round(articles_growth, 1),
            
            'title': 'Dashboard',
        })
        
        return context


class ProjectListView(StaffRequiredMixin, ListView):
    """List all projects with filtering and pagination"""
    model = Project
    template_name = 'admin/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Project.objects.all().order_by('-created_at')
        
        # Apply filters
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        featured = self.request.GET.get('featured')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if featured == 'on':
            queryset = queryset.filter(featured=True)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(client__icontains=search) |
                Q(technologies__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProjectFilterForm(self.request.GET or None)
        context['title'] = 'Projects'
        return context


class ProjectCreateView(StaffRequiredMixin, CreateView):
    """Create a new project"""
    model = Project
    form_class = ProjectForm
    template_name = 'admin/project_form.html'
    success_url = reverse_lazy('project_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Project'
        return context
    
    def form_valid(self, form):
        # Auto-generate slug if not provided or empty
        if not form.instance.slug or form.instance.slug.strip() == '':
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(form.instance.title)
            # Ensure uniqueness by checking existing slugs
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            form.instance.slug = slug
        
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProjectDetailView(StaffRequiredMixin, DetailView):
    """View project details"""
    model = Project
    template_name = 'admin/project_detail.html'
    context_object_name = 'project'
    slug_field = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class ProjectUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing project"""
    model = Project
    form_class = ProjectForm
    template_name = 'admin/project_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.object.title}'
        context['project'] = self.object
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Project updated successfully!')
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Debug: Check featured field
        print(f"DEBUG UPDATE: Featured field in form.cleaned_data: {form.cleaned_data.get('featured')}")
        print(f"DEBUG UPDATE: Featured field in form.instance: {form.instance.featured}")
        print(f"DEBUG UPDATE: Featured field in POST data: {self.request.POST.get('featured')}")
        
        # Note: Project model doesn't have updated_by field, using updated_at auto field
        result = super().form_valid(form)
        
        # Debug: Check if it was saved
        print(f"DEBUG UPDATE: Featured field after save: {self.object.featured}")
        return result


class ProjectDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a project"""
    model = Project
    template_name = 'admin/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ProjectStatusUpdateView(StaffRequiredMixin, View):
    """Update project status via AJAX"""
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({'error': 'Invalid request'}, status=400)
            
        project = get_object_or_404(Project, pk=kwargs['pk'])
        new_status = request.POST.get('status')
        
        if new_status in dict(Project.STATUS_CHOICES).keys():
            project.status = new_status
            project.save()
            return JsonResponse({
                'status': 'success',
                'message': f'Status updated to {project.get_status_display()}',
                'status_display': project.get_status_display(),
                'status_class': project.status
            })
        
        return JsonResponse({'error': 'Invalid status'}, status=400)


# API Views
class ProjectStatsAPIView(StaffRequiredMixin, View):
    """API endpoint for project statistics"""
    def get(self, request, *args, **kwargs):
        # Get counts for different statuses
        status_counts = Project.objects.aggregate(
            total=Count('id'),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            in_progress=Count(Case(When(status='in_progress', then=1), output_field=IntegerField())),
            on_hold=Count(Case(When(status='on_hold', then=1), output_field=IntegerField())),
            cancelled=Count(Case(When(status='cancelled', then=1), output_field=IntegerField())),
        )
        
        # Get monthly project counts for the last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_counts = Project.objects.filter(
            created_at__gte=six_months_ago
        ).extra({
            'month': "date_trunc('month', created_at)"
        }).values('month').annotate(count=Count('id')).order_by('month')
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'status_counts': status_counts,
                'monthly_counts': list(monthly_counts)
            }
        })


class RecentProjectsAPIView(StaffRequiredMixin, ListView):
    """API endpoint for recent projects"""
    model = Project
    context_object_name = 'projects'
    template_name = 'admin/includes/recent_projects.html'
    
    def get_queryset(self):
        return Project.objects.order_by('-created_at')[:5]
    
    def render_to_response(self, context, **response_kwargs):
        projects = []
        for project in context['projects']:
            projects.append({
                'id': project.id,
                'title': project.title,
                'status': project.status,
                'status_display': project.get_status_display(),
                'created_at': project.created_at.strftime('%b %d, %Y'),
                'url': reverse_lazy('project_detail', kwargs={'pk': project.pk})
            })
        
        return JsonResponse({
            'status': 'success',
            'data': projects
        })
def public_article_list(request):
    """
    Public view for displaying published articles with pagination and featured article.
    """
    # Get all published articles, ordered by creation date (newest first)
    articles_list = Article.objects.filter(status='published').order_by('-created_at')
    
    # Get the featured article (most recent published article)
    featured_article = articles_list.first()
    
    # If we have a featured article, exclude it from the main articles list
    if featured_article:
        articles_list = articles_list.exclude(pk=featured_article.pk)
    
    # Pagination - 9 articles per page
    page = request.GET.get('page', 1)
    paginator = Paginator(articles_list, 9)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    return render(request, 'core/article_list.html', {
        'featured_article': featured_article,
        'articles': articles,
        'page_obj': articles,  # For pagination controls
        'is_admin': False
    })

def admin_article_list(request):
    """
    Admin view for managing all articles (both published and unpublished).
    """
    # Get all articles, ordered by creation date (newest first)
    articles = Article.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_articles = articles.count()
    published_articles = articles.filter(status='published').count()
    draft_articles = articles.filter(status='draft').count()
    total_views = articles.aggregate(total_views=Sum('view_count'))['total_views'] or 0
    
    return render(request, 'admin/article_list_modern.html', {
        'articles': articles,
        'is_admin': True,
        # Individual statistics for template
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'total_views': total_views,
        # Also keep stats dict for potential future use
        'stats': {
            'total': total_articles,
            'published': published_articles,
            'drafts': draft_articles,
            'total_views': total_views,
        }
    })
def admin_article_detail(request, pk):
    """
    Admin view for displaying article details with admin controls.
    """
    article = get_object_or_404(Article, pk=pk)
    
    # Get related articles (excluding current article)
    related_articles = Article.objects.filter(
        status='published'
    ).exclude(pk=article.pk).order_by('-created_at')[:3]
    
    # Get next and previous articles for navigation
    next_article = Article.objects.filter(
        created_at__gt=article.created_at
    ).order_by('created_at').first()
    
    prev_article = Article.objects.filter(
        created_at__lt=article.created_at
    ).order_by('-created_at').first()
    
    # Get comments for the article
    comments = article.comments.all().order_by('created_at')
    
    # Increment view count
    article.view_count = F('view_count') + 1
    article.save(update_fields=['view_count'])
    article.refresh_from_db()
    
    return render(request, 'admin/article_detail.html', {
        'article': article,
        'related_articles': related_articles,
        'next_article': next_article,
        'prev_article': prev_article,
        'comments': comments,
        'is_admin': True
    })

def article_detail(request, slug=None, pk=None):
    """
    Public view for displaying a single article. Can be accessed by either slug or primary key.
    If both are provided, slug takes precedence.
    """
    article = None
    
    # Try to get article by slug first (preferred method for public URLs)
    if slug:
        article = get_object_or_404(Article, slug=slug, status='published')
    # Fall back to primary key if slug is not provided
    elif pk:
        article = get_object_or_404(Article, pk=pk)
    else:
        raise Http404("Article not found")
    
    # For admin views, check permissions
    is_admin_view = request.path.startswith('/admin/')
    if is_admin_view and not request.user.is_staff:
        raise PermissionDenied
    
    # Get related articles (exclude current article)
    related_articles = Article.objects.filter(
    ).exclude(
        pk=article.pk
    ).order_by('-created_at')[:3]
    
    # Get next and previous articles for navigation
    next_article = Article.objects.filter(
        created_at__gt=article.created_at
    ).order_by('created_at').first()
    
    prev_article = Article.objects.filter(
        created_at__lt=article.created_at
    ).order_by('-created_at').first()
    
    # Increment view count (only for non-admin views)
    if not is_admin_view:
        article.view_count = F('view_count') + 1
        article.save(update_fields=['view_count'])
        article.refresh_from_db()  # Refresh to get the updated view_count
    
    # Determine which template to use
    template = 'admin/article_detail.html' if is_admin_view else 'core/article_detail.html'
    
    context = {
        'article': article,
        'is_admin': is_admin_view,
        'related_articles': related_articles,
        'next_article': next_article,
        'prev_article': prev_article,
        'page_title': article.title,
        'meta_description': article.short_description,
        'meta_keywords': article.tags.all() if hasattr(article, 'tags') else [],
    }
    
    # Add Open Graph and Twitter card meta tags for public views
    if not is_admin_view:
        context.update({
            'og_title': article.title,
            'og_description': article.short_description,
            'og_type': 'article',
            'twitter_card': 'summary_large_image',
        })
        
        # Add article image if available
        if hasattr(article, 'image') and article.image:
            context.update({
                'og_image': request.build_absolute_uri(article.image.url),
                'twitter_image': request.build_absolute_uri(article.image.url),
            })
    
    return render(request, template, context)
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            if not article.author:
                article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('admin_article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    
    return render(request, 'admin/article_form.html', {
        'form': form,
        'title': 'Create New Article',
        'article': None,
    })
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('admin_article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'admin/article_form.html', {
        'form': form,
        'title': f'Edit Article: {article.title}',
        'article': article
    })
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        try:
            article_title = article.title
            article.delete()
            messages.success(request, f'Article "{article_title}" was deleted successfully.')
            return redirect('admin_article_list')
        except Exception as e:
            messages.error(request, f'Error deleting article: {str(e)}')
            return redirect('admin_article_detail', pk=article.pk)
    
    # For GET request, show confirmation page
    return render(request, 'core/article_confirm_delete.html', {
        'article': article,
        'is_admin': request.path.startswith('/admin/')
    })
def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = CommentForm()
    
    return render(request, 'core/article_detail.html', {
        'article': article,
        'form': form,
        'comments': article.comment_set.all(),
    })
    
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def learning_resource_list(request):
    # Get published resources by default
    resources_list = LearningResource.objects.filter(status='published').order_by('-published_at', '-created_at')
    
    # Get filter parameters
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Apply filters
    if status:
        resources_list = resources_list.filter(status=status)
    if search:
        resources_list = resources_list.filter(
            Q(title__icontains=search) | 
            Q(short_description__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(resources_list, 9)  # Show 9 resources per page
    
    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(1)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)
    
    context = {
        'learning_resources': resources,
        'is_paginated': resources.has_other_pages(),
        'page_obj': resources,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'core/learning_resource_list.html', context)

def learning_resource_detail(request, slug):
    """View for displaying a single learning resource."""
    resource = get_object_or_404(LearningResource, slug=slug, status='published')
    
    # Increment view count
    resource.increment_view_count()
    
    # Get related resources (excluding current resource)
    related_resources = LearningResource.objects.filter(
        status='published'
    ).exclude(id=resource.id).order_by('?')[:3]  # Get 3 random related resources
    
    context = {
        'resource': resource,
        'related_resources': related_resources,
    }
    
    return render(request, 'core/learning_resource_detail.html', context)