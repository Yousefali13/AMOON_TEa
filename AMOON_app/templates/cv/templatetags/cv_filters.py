from django import template

register = template.Library()

@register.filter
def strip(value):
    """
    Removes leading and trailing whitespace from a string.
    """
    return value.strip() if value else value 