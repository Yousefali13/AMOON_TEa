from django import template
from django.utils.timezone import now
import datetime

register = template.Library()

@register.filter
def active_status(last_seen):
    """ تحديد حالة النشاط بناءً على آخر مرة كان المستخدم نشطًا فيها """
    if not last_seen:
        return "غير معروف"
    
    delta = now() - last_seen
    if delta < datetime.timedelta(minutes=5):
        return "متصل الآن ✅"
    elif delta < datetime.timedelta(hours=1):
        return f"آخر ظهور منذ {delta.seconds // 60} دقيقة"
    else:
        return f"آخر ظهور {last_seen.strftime('%H:%M - %d/%m/%Y')}"
