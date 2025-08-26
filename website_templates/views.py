from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import WebsiteTemplate, TemplateCategory


def template_list(request):
    """Display list of website templates with filtering and search"""
    templates = WebsiteTemplate.objects.filter(is_active=True)
    categories = TemplateCategory.objects.filter(is_active=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    template_type = request.GET.get('type')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')
    
    if category_slug:
        templates = templates.filter(category__slug=category_slug)
    
    if template_type:
        templates = templates.filter(template_type=template_type)
    
    if difficulty:
        templates = templates.filter(difficulty_level=difficulty)
    
    if search_query:
        templates = templates.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(technologies__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        templates = templates.order_by('-view_count', '-created_at')
    elif sort_by == 'downloads':
        templates = templates.order_by('-download_count', '-created_at')
    elif sort_by == 'oldest':
        templates = templates.order_by('created_at')
    else:  # newest
        templates = templates.order_by('-created_at')
    
    # Featured templates
    featured_templates = templates.filter(is_featured=True)[:6]
    
    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'templates': page_obj,
        'featured_templates': featured_templates,
        'categories': categories,
        'current_category': category_slug,
        'current_type': template_type,
        'current_difficulty': difficulty,
        'search_query': search_query,
        'sort_by': sort_by,
        'template_types': WebsiteTemplate.TEMPLATE_TYPES,
        'difficulty_levels': [('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        'title': 'Website Templates'
    }
    
    return render(request, 'website_templates/template_list.html', context)


def template_detail(request, slug):
    """Display template details with GitHub Pages iframe"""
    template = get_object_or_404(WebsiteTemplate, slug=slug, is_active=True)
    
    # Increment view count
    template.increment_view_count()
    
    # Related templates
    related_templates = WebsiteTemplate.objects.filter(
        category=template.category,
        is_active=True
    ).exclude(id=template.id)[:4]
    
    context = {
        'template': template,
        'related_templates': related_templates,
        'title': template.title
    }
    
    return render(request, 'website_templates/template_detail.html', context)


def category_detail(request, slug):
    """Display templates in a specific category"""
    category = get_object_or_404(TemplateCategory, slug=slug, is_active=True)
    templates = WebsiteTemplate.objects.filter(category=category, is_active=True)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        templates = templates.order_by('-view_count', '-created_at')
    elif sort_by == 'downloads':
        templates = templates.order_by('-download_count', '-created_at')
    elif sort_by == 'oldest':
        templates = templates.order_by('created_at')
    else:  # newest
        templates = templates.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'templates': page_obj,
        'sort_by': sort_by,
        'title': f'{category.name} Templates'
    }
    
    return render(request, 'website_templates/category_detail.html', context)


@require_POST
def increment_download(request, slug):
    """Increment download count for a template"""
    template = get_object_or_404(WebsiteTemplate, slug=slug, is_active=True)
    template.increment_download_count()
    
    return JsonResponse({
        'success': True,
        'download_count': template.download_count
    })


@require_POST
def toggle_featured(request, slug):
    """Toggle featured status of a template (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    template = get_object_or_404(WebsiteTemplate, slug=slug)
    
    try:
        import json
        data = json.loads(request.body)
        template.is_featured = data.get('featured', False)
        template.save()
        
        return JsonResponse({
            'success': True,
            'is_featured': template.is_featured
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def toggle_active(request, slug):
    """Toggle active status of a template (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    template = get_object_or_404(WebsiteTemplate, slug=slug)
    
    try:
        import json
        data = json.loads(request.body)
        template.is_active = data.get('active', True)
        template.save()
        
        return JsonResponse({
            'success': True,
            'is_active': template.is_active
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
