from django import template
import re

register = template.Library()

YOUTUBE_WATCH_RE = re.compile(r"https?://(www\.)?youtube\.com/watch\?v=([\w-]+)")
YOUTUBE_SHORT_RE = re.compile(r"https?://youtu\.be/([\w-]+)")
VIMEO_RE = re.compile(r"https?://(www\.)?vimeo\.com/(\d+)")

@register.filter
def to_embed(url: str) -> str:
    """Convert common video watch URLs to embeddable iframe URLs.
    - YouTube watch -> /embed/<id>
    - youtu.be short -> /embed/<id>
    - Vimeo -> https://player.vimeo.com/video/<id>
    Returns original URL if no match.
    """
    if not url:
        return url
    m = YOUTUBE_WATCH_RE.match(url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(2)}"
    m = YOUTUBE_SHORT_RE.match(url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    m = VIMEO_RE.match(url)
    if m:
        return f"https://player.vimeo.com/video/{m.group(2)}"
    return url

@register.filter
def is_mp4(url: str) -> bool:
    if not url:
        return False
    return str(url).lower().endswith('.mp4')
