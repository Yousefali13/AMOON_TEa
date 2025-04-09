from django.utils.timezone import now
from chat.models import User

class UpdateLastSeenMiddleware:
    """ يقوم بتحديث آخر وقت كان المستخدم نشطًا فيه """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            User.objects.filter(id=request.user.id).update(last_seen=now())
        return self.get_response(request)
