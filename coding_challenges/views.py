import json
import time
import base64
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Challenge, Submission, Tag, Profile
from .forms import SubmissionForm, ChallengeForm


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
def submit_solution(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    form = SubmissionForm(request.POST)
    if not form.is_valid():
        return render(request, 'coding_challenges/challenge_detail.html', {
            'challenge': challenge,
            'form': form,
        })

    language = form.cleaned_data['language']
    code = form.cleaned_data['code']

    sub = Submission.objects.create(
        challenge=challenge,
        user=request.user,
        language=language,
        code=code,
        status='queued'
    )

    # Kick off Judge0 submission (async via API endpoint consumed by JS)
    return redirect('coding_challenges:challenge_detail', slug=challenge.slug)


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
def api_run_code(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        code = payload.get('code', '')
        language = payload.get('language', 'python')
        stdin = payload.get('stdin', '')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    language_id = LANGUAGE_MAP.get(language)
    if not language_id:
        return JsonResponse({'error': 'Unsupported language'}, status=400)

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
def api_submission_status(request, token: str):
    try:
        r = requests.get(f"{settings.JUDGE0_API_URL}/submissions/{token}?base64_encoded=true", headers=_judge0_headers(), timeout=20)
        r.raise_for_status()
        data = r.json()
        # decode outputs
        decoded = {}
        for k in ['stdout', 'stderr', 'compile_output']:
            v = data.get(k)
            if v:
                try:
                    decoded[k] = base64.b64decode(v).decode('utf-8', errors='replace')
                except Exception:
                    decoded[k] = ''
            else:
                decoded[k] = ''

        status_info = data.get('status') or {}
        status_id = status_info.get('id')
        description = (status_info.get('description') or '').lower()

        # Map Judge0 status to simplified statuses expected by the UI
        if status_id in {1} or 'queue' in description:
            simple = 'queued'
        elif status_id in {2} or 'process' in description:
            simple = 'running'
        elif status_id in {3} or 'accepted' in description:
            simple = 'passed'
        elif status_id in {5} or 'time limit' in description:
            simple = 'timeout'
        elif status_id in {4}:
            simple = 'failed'
        elif status_id in {6, 7, 8, 9, 10, 11, 12, 13}:
            simple = 'error'
        else:
            simple = 'running'

        # Merge compile output into stderr if present
        stderr = decoded.get('stderr', '')
        if decoded.get('compile_output'):
            stderr = (stderr + ('\n' if stderr else '') + decoded['compile_output']).strip()

        resp = {
            'ok': True,
            'status': simple,
            'stdout': decoded.get('stdout', ''),
            'stderr': stderr,
            'time': data.get('time'),
            'memory': data.get('memory'),
        }
        return JsonResponse(resp)
    except requests.RequestException as e:
        # Include upstream HTTP diagnostics when available
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
            'message': 'Unable to fetch status',
            'detail': str(e),
        }
        if status_code is not None:
            error_payload['status_code'] = status_code
        if response_text:
            error_payload['response'] = response_text[:2000]
        return JsonResponse(error_payload, status=503)


def leaderboard(request):
    top_profiles = Profile.objects.order_by('-points', '-solved_count')[:50]
    return render(request, 'coding_challenges/leaderboard.html', {'top_profiles': top_profiles})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    solved = Submission.objects.filter(user=request.user, status='passed').values('challenge').distinct().count()
    total = Challenge.objects.count()
    recent = Submission.objects.filter(user=request.user)[:10]
    return render(request, 'coding_challenges/profile.html', {
        'profile': profile,
        'solved': solved,
        'total': total,
        'recent': recent,
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
