from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import google.generativeai as genai
import os
import json
from .models import Contact, Project
from .forms import ProjectForm, ProjectFilterForm

def get_gemini_chat():
    try:
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            print("GEMINI_API_KEY not found in settings")
            return None
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
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
    
    projects = Project.objects.all()
    return render(request, 'core/home.html', {'projects': projects})

@require_http_methods(["POST"])
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
                'error': 'Gemini not initialized'
            }, status=503)
        
        # Get response from Gemini
        response = chat.send_message(user_message)
        
        return JsonResponse({
            'response': response.text,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        return JsonResponse({
            'response': 'Sorry, I encountered an error. Please try again later or contact us directly.',
            'error': str(e)
        }, status=500)

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyBXVv3tklwuNRpH82WbP-bLyNAVQA-kvYo")
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
    
    Be helpful, professional, and concise in your responses.
    If you don't know an answer, say you'll have someone from the team contact them.
    """
    
    # Initialize chat with instructions
    chat.send_message(CHAT_INSTRUCTIONS)
    
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    model = None
    chat = None

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        subject = f"New Contact from {name}"
        body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], fail_silently=True)
            messages.success(request, 'Thanks! We will get back to you shortly.')
        except Exception:
            messages.success(request, 'Thanks! We will get back to you shortly.')
        return redirect('home')

    stats = {
        'years_experience': 7,
        'projects_delivered': 120,
        'client_satisfaction': 98,
        'team_members': 12,
    }
    return render(request, 'core/home.html', {'stats': stats})
