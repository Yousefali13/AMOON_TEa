from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from AMOON_app.models import Product

STATUS_CHOICES = [
    ('pending', 'قيد المراجعة'),
    ('accepted', 'مقبول'),
    ('rejected', 'مرفوض'),
    ('offer_sent', 'تم إرسال عرض سعر'),
    ('offer_accepted', 'تم قبول عرض السعر'),
    ('offer_rejected', 'تم رفض عرض السعر'),
    ('shipped', 'تم الشحن'),
    ('cancelled', 'ملغي'),
]

class Order(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_orders",
        null=True,       
        blank=True
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_orders",
        null=True,      
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    price_offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        # تأمين عرض اسم العميل والبائع حتى لو كانت غير محددة
        customer_name = self.customer.get_full_name() if self.customer and (self.customer.first_name or self.customer.last_name) else (self.customer.username if self.customer else "غير محدد")
        seller_name = self.seller.get_full_name() if self.seller and (self.seller.first_name or self.seller.last_name) else (self.seller.username if self.seller else "غير محدد")
        return f"طلب #{self.id} من {customer_name} إلى {seller_name}"

    def update_total_cost(self):
        total = sum(item.total_price() for item in self.items.all())
        self.total_cost = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"

    def total_price(self):
        return self.quantity * self.unit_price
