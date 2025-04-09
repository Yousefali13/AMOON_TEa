from django.db import models
from django.utils import timezone
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sent_messages",  # تغيير related_name لتكون فريدة
        verbose_name="المرسل"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_received_messages",  # تغيير related_name لتكون فريدة
        verbose_name="المستقبل"
    )
    content = models.TextField(verbose_name="المحتوى")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="وقت الإرسال")

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_notifications",  # تغيير related_name لتكون فريدة
        verbose_name="المستخدم"
    )
    message = models.CharField(max_length=255, verbose_name="الرسالة")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="الرابط")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="وقت الإنشاء")

    def __str__(self):
        return f"{self.user.username} - {self.message}"
