from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CustomUser, Company ,EmployeeActivity ,Training
from django.contrib.auth import get_user_model



if admin.site.is_registered(User):
    admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'company', 'is_staff')
    search_fields = ('username', 'email', 'company__name')
    list_filter = ('company', 'is_staff', 'is_superuser')

CustomUser = get_user_model()

# ✅ تجنب تسجيل CustomUser مرتين
if not admin.site.is_registered(CustomUser):
    admin.site.register(CustomUser, CustomUserAdmin)

if not admin.site.is_registered(Company):
    admin.site.register(Company)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'employee_count', 'max_employee_count')



    search_fields = ('name', 'code')

#from django.contrib import admin
#from .models import Department, Employee, Activity

#admin.site.register(Department)
#admin.site.register(Employee)
#admin.site.register(Activity)
