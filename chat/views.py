from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Message, Notification
User = get_user_model()

@login_required
def messages_list(request):
    """
    عرض قائمة المحادثات السابقة للمستخدم الحالي.
    يتم جلب المستخدمين الذين قام المستخدم بمحادثتهم أو تلقى رسائل منهم.
    """
    user = request.user
    conversations = User.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct().exclude(id=user.id)
    return render(request, 'chat/messages_list.html', {'conversations': conversations})

@login_required
def chat_view(request, user_id):
    """
    عرض المحادثة بين المستخدم الحالي والمستلم المحدد.
    عند إرسال رسالة، يتم إنشاء إشعار للمستلم.
    """
    receiver = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            # إنشاء إشعار للمستلم عند وصول رسالة جديدة
            Notification.objects.create(
                user=receiver,
                message=f"📩 رسالة جديدة من {request.user.get_full_name()}",
                link=f"/chat/messages/{request.user.id}/"  # اضبط الرابط حسب نظامك
            )
            return redirect('chat_view', user_id=receiver.id)

    return render(request, 'chat.html', {'receiver': receiver, 'messages': messages})

@login_required
def get_notifications(request):
    """
    جلب الإشعارات غير المقروءة للمستخدم الحالي على هيئة JSON.
    """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        data = [
            {
                'id': n.id,
                'message': n.message,
                'timestamp': n.timestamp.strftime("%H:%M - %d/%m/%Y"),
                'link': n.link,
            }
            for n in notifications
        ]
        return JsonResponse({'notifications': data, 'count': notifications.count()})
    return JsonResponse({'notifications': [], 'count': 0})

@login_required
def mark_notifications_as_read(request):
    """
    تعيين جميع الإشعارات غير المقروءة للمستخدم الحالي كمقروءة.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


