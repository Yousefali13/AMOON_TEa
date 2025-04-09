from django import template

register = template.Library()

@register.filter
def split_list(value):
    """
    تقسيم النص إلى قائمة باستخدام الفاصلة كفاصل
    """
    if value:
        return [item.strip() for item in value.split(',') if item.strip()]
    return [] 