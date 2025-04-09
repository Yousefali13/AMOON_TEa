import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.db.models import Q, Max
from .models import Order, OrderItem
from .form import OrderItemForm
from AMOON_app.models import Notification  # نموذج الإشعارات من التطبيق العام

# عرض قائمة الطلبات للمستخدم الحالي (باعتباره عميل أو بائع)
@login_required
def order_list(request):
    orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})

# عرض تفاصيل الطلب (إذا كان المستخدم بائع أو عميل)
@login_required
def order_detail(request, order_id):
    # نحاول جلب الطلب كبائع أولاً
    order = Order.objects.filter(pk=order_id, seller=request.user).first()
    if not order:
        order = Order.objects.filter(pk=order_id, customer=request.user).first()
    if not order:
        raise Http404("لا يوجد طلب يطابق المعطيات.")
    return render(request, 'order_detail.html', {'order': order})

# إضافة عنصر للطلب (يعمل البائع فقط)
@login_required
def add_order_item(request, order_id):
    order = get_object_or_404(Order, pk=order_id, seller=request.user)
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            order.update_total_cost()
            messages.success(request, "تم إضافة عنصر إلى الطلب.")
            return redirect('order_detail', order_id=order.id)
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        form = OrderItemForm()
    return render(request, 'add_order_item.html', {'form': form, 'order': order})

# تحديث حالة الطلب (يعمل البائع)
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id, seller=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ['accepted', 'rejected']:
            order.status = new_status
            order.save()
            Notification.objects.create(
                user=order.customer,
                message=f"تم {order.get_status_display()} طلبك رقم #{order.id}",
                link=f"/orders/{order.id}/"
            )
            if new_status == 'accepted':
                messages.success(request, "تم قبول الطلب.")
            else:
                messages.error(request, "تم رفض الطلب.")
        return redirect('order_detail', order_id=order.id)
    return redirect('order_detail', order_id=order.id)

# إرسال عرض سعر (يعمل البائع)
@login_required
def send_price_offer(request, order_id):
    order = get_object_or_404(Order, pk=order_id, seller=request.user)
    if request.method == "POST":
        price_offer = request.POST.get("price_offer")
        if not price_offer:
            messages.error(request, "الرجاء إدخال السعر المقترح.")
            return redirect('order_detail', order_id=order.id)
        try:
            price_offer_decimal = Decimal(price_offer)
        except Exception:
            messages.error(request, "قيمة السعر غير صحيحة.")
            return redirect('order_detail', order_id=order.id)
        order.price_offer = price_offer_decimal
        order.status = "offer_sent"
        order.save()
        Notification.objects.create(
            user=order.customer,
            message=f"تم إرسال عرض سعر جديد للطلب رقم #{order.id} بقيمة {price_offer}",
            link=f"/orders/{order.id}/"
        )
        messages.success(request, "تم إرسال عرض السعر بنجاح.")
        return redirect('order_detail', order_id=order.id)
    return redirect('order_detail', order_id=order.id)

# الموافقة على عرض السعر (يعمل العميل)
@login_required
def approve_price_offer(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    if request.method == "POST":
        approval = request.POST.get("approval")
        if order.price_offer:
            if approval == "approved":
                order.total_cost = order.price_offer
                order.status = "offer_accepted"
                order.save()
                messages.success(request, "تمت الموافقة على عرض السعر وتحديث إجمالي الطلب.")
            elif approval == "rejected":
                order.status = "offer_rejected"
                order.save()
                messages.error(request, "تم رفض عرض السعر.")
        else:
            messages.error(request, "لا يوجد عرض سعر مُحدد لهذا الطلب.")
        return redirect('order_detail', order_id=order.id)
    return render(request, 'order_detail.html', {'order': order})

# عرض الطلبات الخاصة بالمستخدم الذي يعمل كعميل
@login_required
def purchase_order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'purchase_order_list.html', {'orders': orders})

# دالة لإظهار الطلبات التي تخص البائع (مثلاً صفحة "customer_orders")
@login_required
def customer_orders(request):
    orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'customer_orders.html', {'orders': orders})
@login_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, pk=order_id, seller=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, "تم تحديث الطلب بنجاح.")
            return redirect('order_detail', order_id=order.id)
    return render(request, 'order_edit.html', {'order': order})
@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, pk=order_id, seller=request.user)
    if request.method == "POST":
        order.status = "cancelled"  # تغيير الحالة إلى "ملغي"
        order.save()
        messages.success(request, "تم إلغاء الطلب بنجاح.")
        return redirect('order_detail', order_id=order.id)
    return render(request, 'order_cancel_confirm.html', {'order': order})
