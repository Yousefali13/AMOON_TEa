from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/add-item/', views.add_order_item, name='add_order_item'),
    path('<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:order_id>/send-offer/', views.send_price_offer, name='send_price_offer'),
    path('<int:order_id>/approve-offer/', views.approve_price_offer, name='approve_price_offer'),
    path('customer_orders/', views.customer_orders, name='customer_orders'),
    path('my-orders/', views.purchase_order_list, name='purchase_order_list'),
        path('<int:order_id>/edit/', views.order_edit, name='order_edit'),
 
    path('<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
]



