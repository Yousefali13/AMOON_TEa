# middleware.py
from django.utils import timezone

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # لتجنب حفظ المستخدم على كل طلب بشكل مفرط، يمكنك تعديلها لتحديثها مرة كل 5 دقائق مثلاً
            request.user.last_seen = timezone.now()
            request.user.save(update_fields=['last_seen'])
        return response
