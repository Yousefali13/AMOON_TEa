from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from AMOON_app.models import Notification  # نفترض أن نموذج Notification موجود في AMOON_app

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created and instance.seller:
        # الحصول على أول مستخدم مرتبط بشركة البائع (إذا كانت الشركة معرفة)
        supplier_user = instance.seller.company.users.first() if instance.seller.company else None
        if supplier_user:
            Notification.objects.create(
                user=supplier_user,
                message=f"طلب شراء جديد رقم #{instance.id} من {instance.customer.get_full_name()}",
                link=f"/orders/{instance.id}/"
            )
