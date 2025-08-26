import json
import time
import base64
import requests
import logging
import hashlib
import re
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Count, Q, Sum, Avg, Max
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction

from .models import Challenge, Submission, Tag, Profile
from .forms import SubmissionForm, ChallengeForm

# Configure logging
logger = logging.getLogger(__name__)

# Production constants
MAX_SUBMISSIONS_PER_MINUTE = 5
MAX_SUBMISSIONS_PER_HOUR = 50
JUDGE0_TIMEOUT = 30
MAX_CODE_LENGTH = 50000  # 50KB
MAX_INPUT_LENGTH = 10000  # 10KB


def get_rate_limit_key(user_id, action='submit'):
    """Generate cache key for rate limiting"""
    return f"rate_limit:{action}:{user_id}"


def check_rate_limit(user, action='submit'):
    """Check if user has exceeded rate limits"""
    minute_key = f"{get_rate_limit_key(user.id, action)}:minute"
    hour_key = f"{get_rate_limit_key(user.id, action)}:hour"
    
    minute_count = cache.get(minute_key, 0)
    hour_count = cache.get(hour_key, 0)
    
    if minute_count >= MAX_SUBMISSIONS_PER_MINUTE:
        return False, f"Rate limit exceeded: {MAX_SUBMISSIONS_PER_MINUTE} submissions per minute"
    
    if hour_count >= MAX_SUBMISSIONS_PER_HOUR:
        return False, f"Rate limit exceeded: {MAX_SUBMISSIONS_PER_HOUR} submissions per hour"
    
    return True, None


def increment_rate_limit(user, action='submit'):
    """Increment rate limit counters"""
    minute_key = f"{get_rate_limit_key(user.id, action)}:minute"
    hour_key = f"{get_rate_limit_key(user.id, action)}:hour"
    
    # Increment minute counter
    try:
        cache.add(minute_key, 0, 60)  # 1 minute TTL
        cache.incr(minute_key)
    except ValueError:
        cache.set(minute_key, 1, 60)
    
    # Increment hour counter
    try:
        cache.add(hour_key, 0, 3600)  # 1 hour TTL
        cache.incr(hour_key)
    except ValueError:
        cache.set(hour_key, 1, 3600)


def validate_submission_data(code, language, stdin=''):
    """Validate submission data for security and limits"""
    errors = []
    
    if not code or not code.strip():
        errors.append("Code cannot be empty")
    
    if len(code) > MAX_CODE_LENGTH:
        errors.append(f"Code too long (max {MAX_CODE_LENGTH} characters)")
    
    if len(stdin) > MAX_INPUT_LENGTH:
        errors.append(f"Input too long (max {MAX_INPUT_LENGTH} characters)")
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        'import os', 'import subprocess', 'import sys',
        'exec(', 'eval(', '__import__',
        'open(', 'file(', 'input(',
        'raw_input(', 'compile(',
    ]
    
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            logger.warning(f"Potentially dangerous code pattern detected: {pattern}")
            # Don't block, but log for monitoring
    
    return errors


def check_rate_limit(user, action_type='submission'):
    """Check if user has exceeded rate limits"""
    cache_key_minute = f"rate_limit_{action_type}_{user.id}_minute"
    cache_key_hour = f"rate_limit_{action_type}_{user.id}_hour"
    
    # Get current counts
    minute_count = cache.get(cache_key_minute, 0)
    hour_count = cache.get(cache_key_hour, 0)
    
    # Define limits based on action type
    if action_type == 'api_run':
        minute_limit, hour_limit = 10, 100  # Higher limits for API calls
    else:
        minute_limit, hour_limit = 5, 50   # Standard submission limits
    
    # Check limits
    if minute_count >= minute_limit:
        return False, f"Rate limit exceeded: max {minute_limit} {action_type}s per minute"
    if hour_count >= hour_limit:
        return False, f"Rate limit exceeded: max {hour_limit} {action_type}s per hour"
    
    return True, None


def increment_rate_limit(user, action_type='submission'):
    """Increment rate limit counters"""
    cache_key_minute = f"rate_limit_{action_type}_{user.id}_minute"
    cache_key_hour = f"rate_limit_{action_type}_{user.id}_hour"
    
    # Increment counters with appropriate timeouts
    try:
        cache.set(cache_key_minute, cache.get(cache_key_minute, 0) + 1, 60)
        cache.set(cache_key_hour, cache.get(cache_key_hour, 0) + 1, 3600)
    except Exception as e:
        logger.error(f"Failed to increment rate limit for user {user.id}: {str(e)}")


def dashboard(request):
    # Filters
    difficulty = request.GET.get('difficulty')
    tag_slug = request.GET.get('tag')
    search = request.GET.get('q')

    qs = Challenge.objects.all().order_by('-created_at')
    if difficulty in {'easy', 'medium', 'hard'}:
        qs = qs.filter(difficulty=difficulty)
    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(problem_statement__icontains=search))

    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    challenges = paginator.get_page(page)

    tags = Tag.objects.annotate(count=Count('challenges')).order_by('-count')[:20]

    # User progress
    solved_ids = []
    if request.user.is_authenticated:
        solved_ids = set(
            Submission.objects.filter(user=request.user, status='passed')
            .values_list('challenge_id', flat=True)
        )

    context = {
        'challenges': challenges,
        'tags': tags,
        'difficulty': difficulty,
        'tag_slug': tag_slug,
        'search': search,
        'solved_ids': solved_ids,
    }
    return render(request, 'coding_challenges/dashboard.html', context)


def challenge_list(request, slug=None):
    return dashboard(request)


def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    form = SubmissionForm()
    recent_submissions = []
    if request.user.is_authenticated:
        recent_submissions = Submission.objects.filter(user=request.user, challenge=challenge)[:5]
    return render(request, 'coding_challenges/challenge_detail.html', {
        'challenge': challenge,
        'form': form,
        'recent_submissions': recent_submissions,
        'default_theme': getattr(settings, 'DEFAULT_THEME', 'light'),
    })


@login_required
@require_http_methods(["POST"])
def submit_solution(request, slug):
    """Handle code submission with production-ready validation and processing"""
    challenge = get_object_or_404(Challenge, slug=slug)
    
    # Rate limiting check
    rate_ok, rate_error = check_rate_limit(request.user)
    if not rate_ok:
        messages.error(request, rate_error)
        return redirect('coding_challenges:challenge_detail', slug=challenge.slug)
    
    form = SubmissionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the form errors.")
        return render(request, 'coding_challenges/challenge_detail.html', {
            'challenge': challenge,
            'form': form,
        })

    language = form.cleaned_data['language']
    code = form.cleaned_data['code']
    
    # Validate submission data
    validation_errors = validate_submission_data(code, language)
    if validation_errors:
        for error in validation_errors:
            messages.error(request, error)
        return redirect('coding_challenges:challenge_detail', slug=challenge.slug)
    
    # Check if language is allowed for this challenge
    if language not in challenge.allowed_languages:
        messages.error(request, f"Language '{language}' is not allowed for this challenge.")
        return redirect('coding_challenges:challenge_detail', slug=challenge.slug)
    
    try:
        with transaction.atomic():
            # Create submission record
            submission = Submission.objects.create(
                challenge=challenge,
                user=request.user,
                language=language,
                code=code,
                status='queued'
            )
            
            # Increment rate limit counters
            increment_rate_limit(request.user)
            
            # Log submission
            logger.info(
                f"Submission created: user={request.user.id}, challenge={challenge.id}, "
                f"language={language}, submission_id={submission.id}"
            )
            
            # Process submission asynchronously
            try:
                process_submission_async(submission)
                messages.success(request, "Code submitted successfully! Processing...")
            except Exception as e:
                logger.error(f"Failed to process submission {submission.id}: {str(e)}")
                submission.status = 'error'
                submission.save()
                messages.error(request, "Failed to process submission. Please try again.")
    
    except Exception as e:
        logger.error(f"Failed to create submission: {str(e)}")
        messages.error(request, "Failed to submit code. Please try again.")
    
    return redirect('coding_challenges:challenge_detail', slug=challenge.slug)


def process_submission_async(submission):
    """Process submission with Judge0 API - can be moved to Celery task later"""
    try:
        # Prepare Judge0 submission
        language_id = LANGUAGE_MAP.get(submission.language)
        if not language_id:
            raise ValueError(f"Unsupported language: {submission.language}")
        
        # Get test cases (for now, use example input/output)
        test_input = submission.challenge.example_input or ""
        expected_output = submission.challenge.example_output or ""
        
        # Submit to Judge0
        data = {
            "language_id": language_id,
            "source_code": base64.b64encode(submission.code.encode()).decode(),
            "stdin": base64.b64encode(test_input.encode()).decode(),
            "expected_output": base64.b64encode(expected_output.encode()).decode(),
            "redirect_stderr_to_stdout": True,
        }
        
        headers = _judge0_headers()
        response = requests.post(
            f"{settings.JUDGE0_API_URL}/submissions?base64_encoded=true&wait=false",
            headers=headers,
            data=json.dumps(data),
            timeout=JUDGE0_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        token = result.get('token')
        
        if token:
            submission.external_token = token
            submission.status = 'running'
            submission.save()
            
            logger.info(f"Submission {submission.id} sent to Judge0 with token {token}")
        else:
            raise ValueError("No token received from Judge0")
    
    except Exception as e:
        logger.error(f"Failed to process submission {submission.id}: {str(e)}")
        submission.status = 'error'
        submission.result_raw = {'error': str(e)}
        submission.save()


def _judge0_headers():
    headers = {"Content-Type": "application/json"}
    if settings.JUDGE0_API_HOST and settings.JUDGE0_API_KEY:
        headers.update({
            "X-RapidAPI-Host": settings.JUDGE0_API_HOST,
            "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        })
    return headers


LANGUAGE_MAP = {
    # Judge0 language IDs (CE version). These may change; adjust as needed.
    'python': 71,       # Python (3.8.1)
    'cpp': 54,          # C++ (GCC 9.2.0)
    'java': 62,         # Java (OpenJDK 13.0.1)
    'javascript': 63,   # JavaScript (Node.js 12.14.0)
}


@login_required
@require_http_methods(["POST"])
def api_run_code(request):
    """API endpoint for running code with Judge0 - production ready"""
    # Rate limiting for API calls
    rate_ok, rate_error = check_rate_limit(request.user, 'api_run')
    if not rate_ok:
        return JsonResponse({'ok': False, 'error': rate_error}, status=429)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
        code = payload.get('code', '')
        language = payload.get('language', 'python')
        stdin = payload.get('stdin', '')
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.warning(f"Invalid JSON in api_run_code from user {request.user.id}: {str(e)}")
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload'}, status=400)
    
    # Validate input data
    validation_errors = validate_submission_data(code, language, stdin)
    if validation_errors:
        return JsonResponse({
            'ok': False, 
            'error': 'Validation failed', 
            'details': validation_errors
        }, status=400)
    
    language_id = LANGUAGE_MAP.get(language)
    if not language_id:
        return JsonResponse({
            'ok': False, 
            'error': f'Unsupported language: {language}',
            'supported_languages': list(LANGUAGE_MAP.keys())
        }, status=400)

    data = {
        "language_id": language_id,
        "source_code": base64.b64encode(code.encode()).decode(),
        "stdin": base64.b64encode(stdin.encode()).decode(),
        "redirect_stderr_to_stdout": True,
    }

    try:
        r = requests.post(f"{settings.JUDGE0_API_URL}/submissions?base64_encoded=true&wait=false", headers=_judge0_headers(), data=json.dumps(data), timeout=20)
        r.raise_for_status()
        res = r.json()
        token = res.get('token')
        return JsonResponse({'ok': True, 'token': token})
    except requests.RequestException as e:
        # Provide richer diagnostics to the client
        status_code = None
        response_text = None
        try:
            status_code = getattr(e.response, 'status_code', None)
            if getattr(e, 'response', None) is not None:
                response_text = e.response.text
        except Exception:
            response_text = None

        error_payload = {
            'ok': False,
            'message': 'Runner unavailable',
            'detail': str(e),
        }
        if status_code is not None:
            error_payload['status_code'] = status_code
        if response_text:
            # Limit size to avoid huge payloads
            error_payload['response'] = response_text[:2000]
        return JsonResponse(error_payload, status=503)


@login_required
@require_http_methods(["GET"])
def api_submission_status(request, token: str):
    """Get submission status from Judge0 with enhanced error handling and result processing"""
    try:
        # Validate token format
        if not token or len(token) > 64:
            return JsonResponse({
                'ok': False, 
                'error': 'Invalid token format'
            }, status=400)
        
        # Make request to Judge0
        response = requests.get(
            f"{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=true",
            headers=_judge0_headers(),
            timeout=JUDGE0_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        # Decode base64 outputs safely
        decoded = {}
        for field in ['stdout', 'stderr', 'compile_output']:
            value = data.get(field)
            if value:
                try:
                    decoded[field] = base64.b64decode(value).decode('utf-8', errors='replace')
                except Exception as e:
                    logger.warning(f"Failed to decode {field} for token {token}: {str(e)}")
                    decoded[field] = f"[Error decoding {field}]"
            else:
                decoded[field] = ''
        
        # Process status information
        status_info = data.get('status', {})
        status_id = status_info.get('id')
        description = (status_info.get('description', '')).lower()
        
        # Enhanced status mapping with better error categorization
        status_mapping = {
            1: 'queued',     # In Queue
            2: 'running',    # Processing
            3: 'passed',     # Accepted
            4: 'failed',     # Wrong Answer
            5: 'timeout',    # Time Limit Exceeded
            6: 'error',      # Compilation Error
            7: 'error',      # Runtime Error (SIGSEGV)
            8: 'error',      # Runtime Error (SIGXFSZ)
            9: 'error',      # Runtime Error (SIGFPE)
            10: 'error',     # Runtime Error (SIGABRT)
            11: 'error',     # Runtime Error (NZEC)
            12: 'error',     # Runtime Error (Other)
            13: 'error',     # Internal Error
            14: 'error',     # Exec Format Error
        }
        
        simple_status = status_mapping.get(status_id, 'running')
        
        # Merge compile output into stderr for better error reporting
        stderr = decoded.get('stderr', '')
        compile_output = decoded.get('compile_output', '')
        if compile_output:
            stderr = (stderr + ('\n' if stderr else '') + compile_output).strip()
        
        # Calculate score based on status
        score = 0
        if simple_status == 'passed':
            score = 100
        elif simple_status == 'failed':
            score = 0
        
        # Prepare response with comprehensive information
        response_data = {
            'ok': True,
            'status': simple_status,
            'status_id': status_id,
            'status_description': status_info.get('description', ''),
            'stdout': decoded.get('stdout', ''),
            'stderr': stderr,
            'time': data.get('time'),
            'memory': data.get('memory'),
            'score': score,
            'token': token
        }
        
        # Update submission record if it exists
        try:
            submission = Submission.objects.filter(external_token=token).first()
            if submission and simple_status in ['passed', 'failed', 'error', 'timeout']:
                submission.status = simple_status
                submission.score = score
                submission.runtime_ms = data.get('time', 0) or 0
                submission.memory_kb = data.get('memory', 0) or 0
                submission.result_raw = data
                submission.save()
                
                # Update user profile if passed
                if simple_status == 'passed':
                    profile, created = Profile.objects.get_or_create(user=submission.user)
                    profile.points += 10  # Base points for solving
                    profile.solved_count += 1
                    profile.last_activity = timezone.now()
                    profile.save()
                    
                logger.info(f"Updated submission {submission.id} with status {simple_status}")
        except Exception as e:
            logger.error(f"Failed to update submission for token {token}: {str(e)}")
        
        return JsonResponse(response_data)
        
    except requests.RequestException as e:
        logger.error(f"Judge0 API error for token {token}: {str(e)}")
        
        # Enhanced error response with diagnostics
        error_data = {
            'ok': False,
            'error': 'Judge0 API unavailable',
            'message': 'Unable to fetch submission status',
            'token': token
        }
        
        # Add diagnostic information if available
        if hasattr(e, 'response') and e.response is not None:
            error_data['status_code'] = e.response.status_code
            try:
                error_data['response_text'] = e.response.text[:1000]  # Limit size
            except Exception:
                pass
        
        return JsonResponse(error_data, status=503)
    
    except Exception as e:
        logger.error(f"Unexpected error in api_submission_status for token {token}: {str(e)}")
        return JsonResponse({
            'ok': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'token': token
        }, status=500)


@login_required
@require_http_methods(["POST"])
def check_submission_result(request, submission_id):
    """Check and update a specific submission's result from Judge0"""
    try:
        submission = get_object_or_404(Submission, id=submission_id, user=request.user)
        
        if not submission.external_token:
            return JsonResponse({
                'ok': False,
                'error': 'No external token found for this submission'
            }, status=400)
        
        # Check if submission is already completed
        if submission.status in ['passed', 'failed', 'error', 'timeout']:
            return JsonResponse({
                'ok': True,
                'status': submission.status,
                'score': submission.score,
                'message': 'Submission already completed'
            })
        
        # Fetch result from Judge0
        updated = update_submission_from_judge0(submission)
        
        if updated:
            return JsonResponse({
                'ok': True,
                'status': submission.status,
                'score': submission.score,
                'runtime_ms': submission.runtime_ms,
                'memory_kb': submission.memory_kb,
                'message': 'Submission updated successfully'
            })
        else:
            return JsonResponse({
                'ok': True,
                'status': submission.status,
                'message': 'Submission still processing'
            })
    
    except Exception as e:
        logger.error(f"Error checking submission {submission_id}: {str(e)}")
        return JsonResponse({
            'ok': False,
            'error': 'Failed to check submission result'
        }, status=500)


def update_submission_from_judge0(submission):
    """Update a submission's result from Judge0 API"""
    if not submission.external_token:
        return False
    
    try:
        # Fetch result from Judge0
        response = requests.get(
            f"{settings.JUDGE0_API_URL}/submissions/{submission.external_token}?base64_encoded=true",
            headers=_judge0_headers(),
            timeout=JUDGE0_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        # Process status
        status_info = data.get('status', {})
        status_id = status_info.get('id')
        
        # Enhanced status mapping
        status_mapping = {
            1: 'queued',     # In Queue
            2: 'running',    # Processing
            3: 'passed',     # Accepted
            4: 'failed',     # Wrong Answer
            5: 'timeout',    # Time Limit Exceeded
            6: 'error',      # Compilation Error
            7: 'error',      # Runtime Error (SIGSEGV)
            8: 'error',      # Runtime Error (SIGXFSZ)
            9: 'error',      # Runtime Error (SIGFPE)
            10: 'error',     # Runtime Error (SIGABRT)
            11: 'error',     # Runtime Error (NZEC)
            12: 'error',     # Runtime Error (Other)
            13: 'error',     # Internal Error
            14: 'error',     # Exec Format Error
        }
        
        new_status = status_mapping.get(status_id, 'running')
        
        # Only update if status has changed or is final
        if new_status != submission.status or new_status in ['passed', 'failed', 'error', 'timeout']:
            # Calculate score
            score = 100 if new_status == 'passed' else 0
            
            # Update submission
            submission.status = new_status
            submission.score = score
            submission.runtime_ms = data.get('time', 0) or 0
            submission.memory_kb = data.get('memory', 0) or 0
            submission.result_raw = data
            submission.save()
            
            # Update user profile if passed
            if new_status == 'passed':
                # Check if this challenge was already solved by this user
                already_solved = Submission.objects.filter(
                    user=submission.user,
                    challenge=submission.challenge,
                    status='passed'
                ).exclude(id=submission.id).exists()
                
                if not already_solved:
                    profile, created = Profile.objects.get_or_create(user=submission.user)
                    profile.points += 10  # Base points for solving
                    profile.solved_count += 1
                    profile.last_activity = timezone.now()
                    profile.save()
                    
                    logger.info(f"User {submission.user.id} earned points for solving challenge {submission.challenge.id}")
            
            logger.info(f"Updated submission {submission.id} with status {new_status}, score {score}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Failed to update submission {submission.id} from Judge0: {str(e)}")
        return False


@login_required
def update_pending_submissions(request):
    """Update all pending submissions for the current user"""
    pending_submissions = Submission.objects.filter(
        user=request.user,
        status__in=['queued', 'running'],
        external_token__isnull=False
    ).exclude(external_token='')
    
    updated_count = 0
    for submission in pending_submissions:
        if update_submission_from_judge0(submission):
            updated_count += 1
    
    return JsonResponse({
        'ok': True,
        'updated_count': updated_count,
        'total_pending': pending_submissions.count()
    })


def leaderboard(request):
    top_profiles = Profile.objects.order_by('-points', '-solved_count')[:50]
    return render(request, 'coding_challenges/leaderboard.html', {'top_profiles': top_profiles})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Update any pending submissions before showing profile
    pending_submissions = Submission.objects.filter(
        user=request.user,
        status__in=['queued', 'running'],
        external_token__isnull=False
    ).exclude(external_token='')
    
    updated_count = 0
    for submission in pending_submissions[:5]:  # Limit to avoid timeout
        if update_submission_from_judge0(submission):
            updated_count += 1
    
    if updated_count > 0:
        # Refresh profile stats after updates
        profile.refresh_from_db()
    
    # Calculate detailed statistics
    solved = Submission.objects.filter(user=request.user, status='passed').values('challenge').distinct().count()
    total = Challenge.objects.count()
    total_submissions = Submission.objects.filter(user=request.user).count()
    passed_submissions = Submission.objects.filter(user=request.user, status='passed').count()
    failed_submissions = Submission.objects.filter(user=request.user, status='failed').count()
    error_submissions = Submission.objects.filter(user=request.user, status='error').count()
    pending_submissions_count = Submission.objects.filter(
        user=request.user, 
        status__in=['queued', 'running']
    ).count()
    
    # Calculate success rate
    success_rate = 0
    if total_submissions > 0:
        success_rate = round((passed_submissions / total_submissions) * 100, 1)
    
    # Get recent submissions with more details
    recent = Submission.objects.filter(user=request.user).select_related('challenge').order_by('-created_at')[:10]
    
    # Get solved challenges
    solved_challenges = Submission.objects.filter(
        user=request.user, 
        status='passed'
    ).values('challenge__title', 'challenge__slug', 'challenge__difficulty').distinct()
    
    return render(request, 'coding_challenges/profile.html', {
        'profile': profile,
        'solved': solved,
        'total': total,
        'recent': recent,
        'total_submissions': total_submissions,
        'passed_submissions': passed_submissions,
        'failed_submissions': failed_submissions,
        'error_submissions': error_submissions,
        'pending_submissions': pending_submissions_count,
        'success_rate': success_rate,
        'solved_challenges': solved_challenges,
        'updated_count': updated_count,
    })

class StaffAddChallengeRequired(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_staff or u.has_perm('coding_challenges.add_challenge')


class ChallengeCreateView(LoginRequiredMixin, StaffAddChallengeRequired, CreateView):
    model = Challenge
    form_class = ChallengeForm
    template_name = 'coding_challenges/challenge_form.html'
    success_url = reverse_lazy('coding_challenges:dashboard')

    def form_valid(self, form):
        # Auto-fill slug if left blank
        if not form.instance.slug:
            from django.utils.text import slugify
            form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, 'Challenge created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

# Create your views here.
