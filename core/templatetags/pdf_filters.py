from django import template
import math

register = template.Library()

@register.filter(name='split_pages')
def split_pages(text, lines_per_page=40):
    """
    Split text into pages with a specified number of lines per page.
    """
    if not text:
        return []
    
    lines = text.split('\n')
    total_lines = len(lines)
    total_pages = math.ceil(total_lines / lines_per_page)
    
    pages = []
    for i in range(total_pages):
        start = i * lines_per_page
        end = start + lines_per_page
        page_text = '\n'.join(lines[start:end])
        pages.append(page_text)
    
    return pages

@register.filter(name='split')
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list.
    Usage: {{ "apple,banana,orange"|split:"," }}
    """
    if not value:
        return []
    return value.split(delimiter)

@register.filter(name='trim')
def trim(value):
    """
    Remove leading and trailing whitespace from a string.
    Usage: {{ " hello world "|trim }}
    """
    if not value:
        return value
    return str(value).strip()
