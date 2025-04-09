from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import cv_dashboard, create_update_cv, view_cv

urlpatterns = [
    # صفحات عامة ومستخدمين
    path('', views.say_hello, name='hello'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/company/', views.register_company, name='register_company'),
    path('company/success/<int:company_id>/', views.company_success, name='company_success'),

    # الصفحات الرئيسية ولوحة التحكم
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboardview/', views.dashboardview, name='dashboard_view1'),

    # إدارة المنتجات
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('product/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:product_id>/', views.product_delete, name='product_delete'),

    # إدارة الفئات والفئات الفرعية
    path('category/add/', views.category_create, name='category_create'),
    path('subcategory/', views.subcategory_list, name='subcategory_list'),
    path('subcategory/edit/<int:pk>/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategory/delete/<int:pk>/', views.subcategory_delete, name='subcategory_delete'),
    path('Sub_Category/', views.AddSub_Category, name='Sub_Category'),

    # المحاسبة والقيود اليومية
    path('journal/create/', views.journal_entry_create_view, name='journal_entry_create'),
    path('accounting/', views.accounting_dashboard, name='accounting_dashboard'),
    path('add_account/', views.add_account, name='add_account'),

    # الرسائل والإشعارات
    path('messages/', views.messages_list, name='messages_list'),
    path('chat/<int:user_id>/', views.chat_view, name='chat_view'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/get/', views.get_notifications, name='get_notifications'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('ajax/get_categories/', views.get_categories_by_company, name='get_categories_by_company'),

    # إدارة الموردين (الشركات المسجلة كموردين)
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/categories/', views.supplier_categories_view, name='supplier_categories_view'),
    path('purchases/<int:order_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('create/<int:supplier_id>/<int:subcategory_id>/', views.purchase_order_create, name='add_purchase_order'),
    path('create/<int:supplier_id>/<int:subcategory_id>/', views.purchase_order_create, name='purchase_order_create'),
    path('activity/add/', views.add_activity, name='add_activity'),
    path('activity/add/', views.add_training, name='add_training'),

    # إدارة طلبات الشراء (المشتريات)
    path('purchases/', views.purchase_order_list, name='purchase_order_list'),


    path('send_order/<int:product_id>/', views.send_order, name='send_order'),
    #path('purchases/add/', views.add_purchase_order, name='add_purchase_order'),
    #path('purchases/<int:order_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    #path('purchases/add-item/<int:order_id>/', views.add_purchase_item, name='add_purchase_item'),

    # معالجة الطلبات (قبول/رفض) من قبل المورد
    #path('process-order/<int:order_id>/<str:action>/', views.process_order, name='process_order'),
    # تأكيد استلام الطلب من قبل إدارة المخازن وتحديث المخزون
    #path('confirm-receipt/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),

    # إدارة المخزون
    #path('inventory/', views.inventory_list, name='inventory_list'),

  #  path('purchases/add-with-item/', views.add_purchase_order_with_item, name='add_purchase_order_with_item'),
    #path('ajax/get_subcategories/', views.get_subcategories, name='get_subcategories'),
  #  path('ajax/get_products/', views.get_products, name='get_products'),
    # صفحات إضافية للمستخدم (البروفايل والإعدادات)
    path('users/', views.user_list, name='user_list'),
    path('profile/', views.profile_view, name='profile'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('about/', views.about_view, name='about'),
    path('home_user/', views.home_user, name='home_user'),
    path('home_company/', views.home_company, name='home_company'),
    path('company/login/', views.company_login, name='company_login'),
    path('company/<int:company_id>/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/<int:company_id>/remove_employee/<int:employee_id>/', views.remove_employee, name='remove_employee'),
    path('company/<int:company_id>/add_department/', views.add_department_view, name='add_department'),
    path('company/<int:company_id>/add_employee/', views.add_employee, name='add_employee'),
    path('settings/', views.settings_view, name='settings'),
    path('company/<int:company_id>/edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('send_order/<int:product_id>/', views.send_order, name='send_order'),


    path('cv/', cv_dashboard, name='cv_dashboard'),
    path('cv/create/', views.create_cv, name='create_cv'),
    path('cv/update/', views.create_update_cv, name='update_cv'),
    #path('cv/experience/add/', add_experience, name='add_experience'),
  #  path('cv/education/add/', add_education, name='add_education'),
    path('cv/view/', view_cv, name='view_cv'),
    path('cv/view/<int:user_id>/', view_cv, name='view_user_cv'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
