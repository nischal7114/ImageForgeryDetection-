from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve a key from a dictionary in a template."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''