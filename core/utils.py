import os
import re
import mimetypes
from io import BytesIO
from urllib.parse import urlparse

import PyPDF2
from django.core.files import File
from django.core.exceptions import ValidationError

def extract_text_from_pdf(file):
    """Extract text content from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValidationError(f"Error extracting text from PDF: {str(e)}")

def validate_video_url(url):
    """Validate if the URL is from a supported video platform."""
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    
    # List of supported video platforms
    supported_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com',
        'dailymotion.com', 'facebook.com', 'vimeo.com'
    ]
    
    if not any(domain in netloc for domain in supported_domains):
        raise ValidationError(
            "Unsupported video platform. Supported platforms: "
            "YouTube, Vimeo, Dailymotion, Facebook"
        )
    return url

def get_video_embed_code(url):
    """Generate embed code for the video URL."""
    try:
        from urllib.parse import parse_qs, urlparse
        
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc.lower()
        
        # YouTube
        if 'youtube.com' in netloc or 'youtu.be' in netloc:
            if 'youtube.com' in netloc:
                video_id = parse_qs(parsed_url.query).get('v', [''])[0]
            else:  # youtu.be
                video_id = parsed_url.path[1:]
            return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        
        # Vimeo
        elif 'vimeo.com' in netloc:
            video_id = parsed_url.path.split('/')[-1]
            return f'<iframe src="https://player.vimeo.com/video/{video_id}" width="560" height="315" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'
        
        # Add more platforms as needed
        
        return f'<a href="{url}" target="_blank">Watch Video</a>'
    except Exception as e:
        return f'<a href="{url}" target="_blank">Watch Video</a>'
