from urllib import request
from django.shortcuts import render, redirect
#from django.http import HttpResponse
from django.db.models import Q ,Max
from django.contrib.auth import login
from .models import CustomUser as User
from .form import PurchaseOrderWithItemForm ,SupplierForm
from decimal import Decimal

from django.contrib.auth.decorators import login_required


from .form import RegisterUserForm,SubCategoryForm,CategoryForm, CompanyRegistrationForm ,EmployeeEditForm,JournalEntryLineForm ,AccountForm ,JournalEntryForm, JournalEntryLineFormSet,ProductForm ,CompanyLoginForm ,DepartmentForm
from .models import Company
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Company, Employee, Department, JOB_TITLES, DEPARTMENTS,Category,SubCategory ,CustomUser ,Account, JournalEntry, JournalEntryLine 
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password ,make_password
from .models import Company, Employee, Department, JOB_TITLES, DEPARTMENTS, CustomUser, Account, JournalEntry, JournalEntryLine
from django.forms import ModelForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import activate
from django.shortcuts import redirect
from .models import  EmployeeActivity, Training ,Message, Notification, User ,Product
from django.shortcuts import render, redirect
from .form import ActivityForm, TrainingForm

@login_required
def chat_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    # ✅ جلب كل المستخدمين الذين قام المستخدم بمحادثتهم أو تم محادثته منهم
    conversations = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct().exclude(id=request.user.id)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)

    return render(request, 'chat.html', {
        'receiver': receiver,
        'messages': messages,
        'conversations': conversations  # ✅ إرسال قائمة المحادثات إلى القالب
    })

def set_language(request):
    lang = request.POST.get('language')
    if lang:
        activate(lang)  # تفعيل اللغة المختارة
        request.session['django_language'] = lang  # حفظها في الجلسة
    return redirect(request.META.get('HTTP_REFERER', '/'))

def add_journal_entry(request):
    # منطق الدالة هنا
    return render(request, 'add_journal_entry.html')



from django.apps import apps

import AMOON_app.models as models
employee = models.Employee.objects.all()

Employee = apps.get_model('AMOON_app', 'Employee')

def say_hello(request):
    return render(request, 'hello.html')

def company_success(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    user, created = CustomUser.objects.get_or_create(
        company=company,
        defaults={
            'username': company.company_username,
            'password': company.company_password,
            'user_type': 'company',
        }
    )
    # تسجيل الدخول تلقائيًا بعد إنشاء الحساب
    login(request, user)
    # إعادة التوجيه إلى لوحة التحكم الخاصة بالشركة
    return redirect('company_dashboard', company_id=company.id)


def about_view(request):
    return render(request, 'about.html')

    user, created = CustomUser.objects.get_or_create(
        company=company,
        defaults={
            'username': company.company_username,
            'password': company.company_password,
            'user_type': 'company',
        }
    )

    # تسجيل الدخول تلقائيًا بعد إنشاء الحساب
    login(request, user)

    # إعادة التوجيه إلى لوحة التحكم الخاصة بالشركة
    return redirect('company_dashboard', company_id=company.id)

 # تسجيل الخروج
def logout_company(request):
    logout(request)  
    messages.success(request, "تم تسجيل الخروج بنجاح.") 
    return redirect('company_login')

User = get_user_model()
@login_required
def home(request):
    employee = Employee.objects.filter(user=request.user).first()
    return render(request, 'home.html', {'employee': employee})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_company(request):
    return render(request, 'register_company.html')

def login_view(request):
    return render(request, 'login.html')



def home_user(request):
    return render(request, 'home_user.html')

def home_company(request):
    return render(request, 'home_company.html')
home_company
def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            company_code = form.cleaned_data['company_code']
            try:
                company = Company.objects.get(code=company_code)

                # التحقق من الحد الأقصى للموظفين
                if company.employee_count >= company.max_employee_count:
                    messages.error(request, "تم الوصول إلى الحد الأقصى لعدد الموظفين في هذه الشركة.")
                    return render(request, 'register_user.html', {'form': form})

                # إنشاء المستخدم دون حفظه مباشرةً
                user = form.save(commit=False)
                user.username = form.cleaned_data['email']  # استخدام البريد الإلكتروني كاسم مستخدم
                user.set_password(form.cleaned_data['password'])  # تشفير كلمة المرور
                user.company = company  
                user.save()  # حفظ المستخدم في قاعدة البيانات

                # تحديث عدد الموظفين في الشركة وحفظ التحديث في قاعدة البيانات
                company.employee_count += 1
                company.save()

                # تسجيل الدخول بعد نجاح التسجيل
                login(request, user)
                messages.success(request, "تم التسجيل بنجاح، وتم تسجيل الدخول.")
                return redirect('home')

            except Company.DoesNotExist:
                messages.error(request, "كود الشركة غير صحيح.")
                return render(request, 'register_user.html', {'form': form})

    else:
        form = RegisterUserForm()

    return render(request, 'register_user.html', {'form': form})

def register_company(request):
    if request.method == "POST":
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.employee_count = 1
            
            # تشفير كلمة السر قبل الحفظ
            company.company_password = make_password(form.cleaned_data['company_password'])
            
            company.save()  # حفظ بيانات الشركة
            return redirect('company_success', company_id=company.id)  # توجيه لصفحة النجاح
    else:
        form = CompanyRegistrationForm()

    return render(request, 'register_company.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']  # البريد الإلكتروني كاسم مستخدم
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  #اعادة توجيه الي الصفحه الرئسية
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة!")

    return render(request, 'login.html')  # إعادة عرض نموذج تسجيل الدخول

def company_dashboard(request, company_id):
    # التحقق من أن الشركة مسجلة دخول
    if 'company_id' not in request.session or request.session['company_id'] != company_id:
        messages.error(request, "يجب تسجيل الدخول أولاً.")
        return redirect('company_login')

    try:
        company = get_object_or_404(Company, id=company_id)
        employees = CustomUser.objects.filter(company=company)
        departments = Department.objects.filter(company=company)
        
        # تعريف المتغيرات المطلوبة بشكل صحيح
        DEPARTMENTS = (  # افترضنا أن هذا tuple مثال
            ('HR', 'Human Resources'),
            ('IT', 'Information Technology'),
        )
        
        job_title = {  # افترضنا أن هذا dict مثال
            'HR': 'Human Resources',
            'IT': 'Information Technology',
        }

        # إنشاء context واحد يحتوي على جميع المتغيرات
        context = {
            'company': company,
            'employees': employees,
            'departments': departments,
            'DEPARTMENTS': DEPARTMENTS,
            'job_title': JOB_TITLES
        }
        
        return render(request, 'company_dashboard.html', context)

    except Company.DoesNotExist:
        messages.error(request, "الشركة غير موجودة.")
        return redirect('company_login')
    except Exception as e:
        messages.error(request, f"حدث خطأ: {str(e)}")
        return redirect('company_login')
    
def company_login(request):
    if request.method == 'POST':
        form = CompanyLoginForm(request.POST)
        if form.is_valid():
            company_username = form.cleaned_data['company_username']
            company_password = form.cleaned_data['company_password']

            try:
                company = Company.objects.get(company_username=company_username)
                
                # التحقق من كلمة المرور
                if check_password(company_password, company.company_password):
                    request.session['company_id'] = company.id
                    return redirect('company_dashboard', company_id=company.id)
                else:
                    messages.error(request, "كلمة المرور غير صحيحة!")
            except Company.DoesNotExist:
                messages.error(request, "اسم المستخدم غير صحيح!")
    else:
        form = CompanyLoginForm()

    return render(request, 'company_login.html', {'form': form})

def remove_employee(request, company_id, employee_id):
    company = get_object_or_404(Company, id=company_id)
    employee = get_object_or_404(CustomUser, id=employee_id, company=company)
    
    if request.method == 'POST':
        employee.delete()
        company.employee_count -= 1
        company.save()
        messages.success(request, f"تم حذف الموظف {employee.username} بنجاح.")
        return redirect('company_dashboard', company_id=company.id)
    
    return redirect('company_dashboard', company_id=company.id)




def get_departments(request):
    company_code = request.GET.get('company_code', None)
    department = department
    
    if company_code:
        company = Company.objects.filter(code=company_code).first()
        if company:
            department = DEPARTMENTS

    return JsonResponse({"departments": department})
#register------>django--> css-html-js(java script)
def my_view(request):
    from .models import Employee
    employees = Employee.objects.all()
    return render(request, "template.html", {"employees": employees})

def edit_employee(request, company_id, employee_id):
    company = get_object_or_404(Company, id=company_id)
    employee = get_object_or_404(CustomUser, id=employee_id, company=company)
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()  # سيتم تحديث بيانات الموظف في قاعدة البيانات هنا
            messages.success(request, "تم تحديث بيانات الموظف بنجاح.")
            return redirect('company_dashboard', company_id=company.id)
    else:
        form = EmployeeEditForm(instance=employee)
    return render(request, 'company_dashboard.html', {
        'form': form,
        'employee': employee,
        'company': company,
    })


def add_employee(request, company_id):
    company = get_object_or_404(Company, id=company_id)  # جلب الشركة أو إظهار خطأ 404 إذا لم توجد
    
    if request.method == 'POST':
        try:
            # جلب البيانات من الفورم
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            job_title = request.POST.get('job_title')
            department = request.POST.get('department') 
            username = request.POST.get('username')  # اسم المستخدم
            password = request.POST.get('password')  # كلمة المرور
            
            # التحقق من أن الحقول المطلوبة غير فارغة
            if not all([first_name, last_name, job_title, department, username, password]):
                messages.error(request, "جميع الحقول مطلوبة.")
                return redirect('company_dashboard', company_id=company.id)
            
   
            
            
            # إنشاء مستخدم جديد
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                job_title=job_title,
                department=department,
                company=company
            )
            
            # تحديث عدد الموظفين في الشركة
            company.employee_count += 1
            company.save()
            
            messages.success(request, f"تم إضافة الموظف {first_name} {last_name} بنجاح.")
            return redirect('company_dashboard', company_id=company.id)
        
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة الموظف: {str(e)}")
            return redirect('company_dashboard', company_id=company.id)
    
    # إذا لم يكن الطلب POST، إعادة التوجيه إلى لوحة التحكم
    return redirect('company_dashboard', company_id=company.id)


def dashboard(request):
    # عرض جميع الحسابات والقيود اليومية
    accounts = Account.objects.all()
    journal_entries = JournalEntry.objects.all().order_by('-accounting_date')
    context = {
        'accounts': accounts,
        'journal_entries': journal_entries,
    }
    return render(request, 'accounting/dashboard.html', context)
# views.py


def journal_entry_create_view(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        formset = JournalEntryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # إنشاء القيد الأساسي
            journal_entry = form.save(commit=False)
            # ربط القيد بالمستخدم الحالي
            if request.user.is_authenticated:
                journal_entry.created_by = request.user
            journal_entry.save()

            # ربط الأسطر بالقيد
            lines = formset.save(commit=False)
            total_debit = 0
            total_credit = 0

            for line in lines:
                line.journal_entry = journal_entry
                # حساب المجاميع
                total_debit += line.debit
                total_credit += line.credit
                line.save()

            # التحقق من تساوي المدين والدائن
            if total_debit != total_credit:
                messages.error(request, "يجب أن يتساوى مجموع المدين مع مجموع الدائن.")
                journal_entry.delete()  # حذف القيد إذا لم تتساوى القيم
                return redirect('journal_entry_create')

            # حذف الأسطر التي تم تعليمها للحذف
            for deleted_line in formset.deleted_objects:
                deleted_line.delete()

            messages.success(request, f"تم إنشاء القيد {journal_entry.reference} بنجاح.")
            return redirect('journal_entry_detail', pk=journal_entry.pk)
        else:
            messages.error(request, "حدثت أخطاء في البيانات المدخلة.")
    else:
        form = JournalEntryForm()
        formset = JournalEntryLineFormSet()

    return render(request, 'journal_entry_form.html', {
        'form': form,
        'formset': formset,
    })


def accounting_dashboard(request):
    accounts = Account.objects.all()
    journal_entries = JournalEntry.objects.all().order_by('-accounting_date')
    context = {
        'accounts': accounts,
        'journal_entries': journal_entries,
    }
    return render(request, 'accounting_dashboard.html', context)

def add_account(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تمت إضافة الحساب بنجاح.")
            return redirect('add_account')
        else:
            messages.error(request, "حدث خطأ، يرجى التحقق من البيانات.")
    else:
        form = AccountForm()
    accounts = Account.objects.all()
    return render(request, 'add_account.html', {'form': form, 'accounts': accounts})

class JournalEntryForm(ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['reference', 'accounting_date', 'journal', 'state', 'comment']

from django.forms import inlineformset_factory

JournalEntryLineFormSet = inlineformset_factory(
    JournalEntry,
    JournalEntryLine,
    fields=['account', 'partner', 'label', 'debit', 'credit', 'tax_grids'],
    extra=1,
    can_delete=True
)


def add_department_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.company = company
            department.save()
            messages.success(request, "تمت إضافة الإدارة بنجاح.")
            return redirect('company_dashboard', company_id=company.id)
        else:
            messages.error(request, "حدث خطأ في البيانات المدخلة.")
    else:
        form = DepartmentForm()
        
    return render(request, 'add_department.html', {'form': form, 'company': company})

def settings_view(request):
    user = request.user
    if request.method == "POST":
        # الحصول على البيانات من النموذج
        full_name = request.POST.get("full_name")
        profile_image = request.FILES.get("profile_image")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        # تحديث الاسم (يمكنك تعديل هذا الجزء حسب بنية نموذج المستخدم لديك)
 
        
        # تحديث الاسم (يتم تقسيمه إلى الاسم الأول والاسم الأخير)
        if full_name:
            name_parts = full_name.split()
            user.first_name = name_parts[0]  # الاسم الأول
            user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""  # الاسم الأخير
        
        # تحديث الصورة الشخصية إذا تم رفعها
        if profile_image:
            user.profile_image = profile_image  # تأكد من وجود هذا الحقل في نموذج المستخدم
        
        # تحديث كلمة المرور إذا تم إدخالها
        if password or confirm_password:
            if password != confirm_password:
                messages.error(request, "كلمة المرور غير متطابقة!")
                return redirect('settings')
            else:
                user.set_password(password)
                # تحديث الجلسة لتبقى مسجلاً بعد تغيير كلمة المرور
                update_session_auth_hash(request, user)
        
        user.save()
        messages.success(request, "تم تحديث الإعدادات بنجاح.")
        return redirect('settings')
    
    return render(request, 'settings.html', {'user': user})


def profile_view(request):
    """ عرض صفحة البروفايل للموظف """
    user = get_object_or_404(CustomUser, id=request.user.id)  
    activities = EmployeeActivity.objects.filter(employee=request.user)
    trainings = Training.objects.filter(employee=request.user)
    
    context = {
        'employee': user,
        'activities': activities,
        'trainings': trainings,
    }
    
    return render(request, 'profile.html', context)



def add_activity(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.employee = request.user  # تأكد أن الحقل صحيح
            activity.save()
            return redirect('profile')
    else:
        form = ActivityForm()
    
    return render(request, 'add_activity.html', {'form': form})



def add_training(request):
    if request.method == "POST":
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.user = request.user
            training.save()
            return redirect('profile')
    else:
        form = TrainingForm()
    return render(request, 'add_training.html', {'form': form})


def user_list(request):
    """ عرض جميع الموظفين داخل نفس الشركة """
    if not request.user.is_authenticated:
        return redirect('login') 

    employees = CustomUser.objects.filter(company=request.user.company).exclude(id=request.user.id)  # استبعاد المستخدم الحالي
    return render(request, 'user_list.html', {'employees': employees})

def user_profile(request, user_id):
    """ عرض ملف موظف معين """
    employee = get_object_or_404(CustomUser, id=user_id, company=request.user.company)


    profile_image = employee.profile_image.url if employee.profile_image else '/static/images/default_user.png'

    
    return render(request, 'user_profile.html', {'employee': employee, 'profile_image': profile_image})

@login_required
def messages_list(request):
    """ عرض جميع المستخدمين الذين تم التحدث معهم سابقًا """
    conversations = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()
    return render(request, 'messages_list.html', {'conversations': conversations})

@login_required


def chat_view(request, user_id):
    """ عرض المحادثة بين المستخدم والمستلم المحدد """
    receiver = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=receiver, content=content)

            # ✅ إنشاء إشعار بعد إرسال الرسالة
            Notification.objects.create(
                user=receiver,
                message=f"📩 رسالة جديدة من {request.user.get_full_name()}",
                link=f"/messages/{request.user.id}/"  # الرابط إلى المحادثة
            )

            return redirect('chat:chat', user_id=receiver.id)  # ✅ إعادة التوجيه بعد الإشعار

    return render(request, 'chat.html', {'receiver': receiver, 'messages': messages})


@login_required

def get_notifications(request):
    """ إرجاع الإشعارات غير المقروءة على هيئة JSON """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        data = [
            {'id': n.id, 'message': n.message, 'timestamp': n.timestamp.strftime("%H:%M - %d/%m/%Y")}
            for n in notifications
        ]
        return JsonResponse({'notifications': data, 'count': notifications.count()})
    return JsonResponse({'notifications': [], 'count': 0})
def notifications_view(request):
    """ إرجاع الإشعارات على هيئة JSON """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        data = [
            {'id': n.id, 'message': n.message, 'timestamp': n.timestamp.strftime("%H:%M - %d/%m/%Y")}
            for n in notifications
        ]
        return JsonResponse({'notifications': data, 'count': notifications.count()})
    return JsonResponse({'notifications': [], 'count': 0})

def messages_list(request):
    """ إحضار جميع المحادثات السابقة مع الصور وآخر رسالة """
    user = request.user  # المستخدم الحالي
    
    # جلب جميع المستخدمين الذين تحدث معهم المستخدم
    conversations = User.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct().exclude(id=user.id).annotate(
        last_message_time=Max('sent_messages__timestamp')  # جلب أحدث رسالة تم إرسالها
    ).order_by('-last_message_time')  # ترتيب حسب آخر رسالة

    conversations_data = []
    for conversation in conversations:
        last_message = Message.objects.filter(
            Q(sender=conversation, receiver=user) | Q(sender=user, receiver=conversation)
        ).order_by('-timestamp').first()

        conversations_data.append({
            'user': conversation,
            'last_message': last_message.content if last_message else "لا توجد رسائل بعد",
            'last_message_time': last_message.timestamp if last_message else None,
            'profile_picture': conversation.profile_image.url if conversation.profile_image else 'images/default_profile.png'
        })
    
    return render(request, 'messages_list.html', {'conversations': conversations_data})
def mark_notifications_as_read(request):
    """ تعيين جميع الإشعارات كمقروءة """
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def mark_notifications_as_read(request):
    """
    تعيين جميع الإشعارات غير المقروءة للمستخدم الحالي كمقروءة.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

def journal_entry_create_view(request):
    JournalEntryLineFormSet = inlineformset_factory(
        JournalEntry,
        JournalEntryLine,
        form=JournalEntryLineForm,
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        form = JournalEntryForm(request.POST)
        formset = JournalEntryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            journal_entry = form.save(commit=False)
            # ربط القيد بالمستخدم الحالي أو أي منطق آخر
            journal_entry.created_by = request.user
            journal_entry.save()

            # حفظ الأسطر
            lines = formset.save(commit=False)
            for line in lines:
                line.journal_entry = journal_entry
                line.save()
            # حذف الأسطر المعلّمة للحذف
            for deleted_line in formset.deleted_objects:
                deleted_line.delete()

            return redirect('journal_entries_list')  # إعادة التوجيه بعد الحفظ
    else:
        form = JournalEntryForm()
        formset = JournalEntryLineFormSet()

    return render(request, 'journal_entry_form.html', {
        'form': form,
        'formset': formset
    })


def journal_entry_create_view(request):
    JournalEntryLineFormSet = inlineformset_factory(
        JournalEntry,
        JournalEntryLine,
        form=JournalEntryLineForm,
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        form = JournalEntryForm(request.POST)
        formset = JournalEntryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            total_debit = 0
            total_credit = 0
            for line_form in formset:
                if line_form.cleaned_data and not line_form.cleaned_data.get('DELETE', False):
                    total_debit += line_form.cleaned_data.get('debit', 0)
                    total_credit += line_form.cleaned_data.get('credit', 0)

            if total_debit != total_credit:
                messages.error(request, "يجب أن يتساوى إجمالي المدين مع إجمالي الدائن قبل حفظ القيد.")
            else:
                journal_entry = form.save(commit=False)
                journal_entry.created_by = request.user
                journal_entry.save()
                for line in formset.save(commit=False):
                    line.journal_entry = journal_entry
                    line.save()
                for deleted_line in formset.deleted_objects:
                    deleted_line.delete()

                messages.success(request, f"تم إنشاء القيد {journal_entry.reference} بنجاح.")
                return redirect('journal_entries_list')
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        form = JournalEntryForm()
        formset = JournalEntryLineFormSet()

    return render(request, 'journal_entry_form.html', {'form': form, 'formset': formset})

from django.db.models import Sum

@login_required
def balance_sheet_view(request):
    # حساب رصيد كل فئة
    assets = Account.objects.filter(category='asset').annotate(
        total_debit=Sum('journalentryline__debit'),
        total_credit=Sum('journalentryline__credit')
    )
    liabilities = Account.objects.filter(category='liability').annotate(
        total_debit=Sum('journalentryline__debit'),
        total_credit=Sum('journalentryline__credit')
    )
    equity = Account.objects.filter(category='equity').annotate(
        total_debit=Sum('journalentryline__debit'),
        total_credit=Sum('journalentryline__credit')
    )
    
    context = {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
    }
    return render(request, 'financial/balance_sheet.html', context)

# مثال على استخدام الخصائص في View:
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'unit_cost': product.unit_purchase_cost(),
        'suggested_price': product.suggested_selling_price(markup_percentage=30)
    }

    return render(request, 'product_detail.html', context)


def product_create(request):
    if not request.user.is_authenticated or not request.user.company:
        messages.error(request, "يجب أن تكون مسجلاً ولديك شركة لإضافة المنتجات.")
        return redirect('login')

    if request.method == "POST":
        form = ProductForm(request.POST)
        # تأكد من تقييد حقل الفئة الفرعية ليختار فقط الفئات التابعة لشركة المستخدم
        form.fields['subcategory'].queryset = SubCategory.objects.filter(category__company=request.user.company)
        if form.is_valid():
            product = form.save(commit=False)
            # يمكنك هنا تعيين أي قيمة إضافية إذا احتجت مثلًا ربط المنتج تلقائيًا بالشركة
            product.save()
            messages.success(request, "تم إضافة المنتج بنجاح.")
            return redirect('product_list')
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        form = ProductForm()
        form.fields['subcategory'].queryset = SubCategory.objects.filter(category__company=request.user.company)
    return render(request, 'product_form.html', {'form': form})

def product_list(request):
    if request.user.is_authenticated and request.user.company:
        products = Product.objects.filter(subcategory__category__company=request.user.company)
        subcategories = SubCategory.objects.filter(category__company=request.user.company)


    else:
        products = Product.objects.none()
    return render(request, 'product_list.html', {'products': products, 'subcategories': subcategories
                                                 })

def AddSub_Category(request):
    if request.method == "POST":
        subcategory_form = SubCategoryForm(request.POST)
        if request.user.is_authenticated and request.user.company:
            subcategory_form.fields['category'].queryset = Category.objects.filter(company=request.user.company)
        else:
            subcategory_form.fields['category'].queryset = Category.objects.none()
        
        if subcategory_form.is_valid():
            subcategory_form.save()
            messages.success(request, "تم إضافة الفئة الفرعية بنجاح.")
            return redirect('Sub_Category')
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        subcategory_form = SubCategoryForm()
        if request.user.is_authenticated and request.user.company:
            subcategory_form.fields['category'].queryset = Category.objects.filter(company=request.user.company)
        else:
            subcategory_form.fields['category'].queryset = Category.objects.none()
    
    context = {
        'subcategory_form': subcategory_form,
    }
    return render(request, 'Sub_Category.html', context)

def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        # تأكد أن المستخدم مسجل ولديه شركة، ثم قم بتعيين الشركة للنموذج
        if request.user.is_authenticated and request.user.company:
            form.instance.company = request.user.company
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة الفئة بنجاح.")
            return redirect('Sub_Category')  # استبدل 'Sub_Category' بالمسار المناسب إذا لزم الأمر
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

def subcategory_list(request):
    if request.user.is_authenticated and request.user.company:
        categories = Category.objects.filter(company=request.user.company)
        subcategories = SubCategory.objects.filter(category__company=request.user.company)
    else:
        categories = Category.objects.none()
        subcategories = SubCategory.objects.none()
    return render(request, 'view_Sub_category.html', {
        'categories': categories,
        'subcategories': subcategories,
    })

def subcategory_edit(request, pk):
    # التأكد من أن الفئة الفرعية تنتمي لشركة المستخدم الحالي
    subcategory = get_object_or_404(SubCategory, pk=pk, category__company=request.user.company)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الفئة الفرعية بنجاح.")
            return redirect('subcategory_list')
        else:
            messages.error(request, "يرجى التأكد من صحة البيانات المدخلة.")
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'view_Sub_category.html', {'form': form})

def subcategory_delete(request, pk):
    # التأكد من أن الفئة الفرعية تنتمي لشركة المستخدم الحالي
    subcategory = get_object_or_404(SubCategory, pk=pk, category__company=request.user.company)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, "تم حذف الفئة الفرعية بنجاح.")
        return redirect('subcategory_list')
    return render(request, 'view_Sub_category.html', {'subcategory': subcategory})
import json
from django.shortcuts import render
from .models import Category, Product
import json
from django.shortcuts import render
from .models import Category, SubCategory, Product
def dashboardview(request):
    # التأكد من أن المستخدم مسجل وله شركة
    if request.user.is_authenticated and request.user.company:
        company = request.user.company
    else:
        # إذا لم يكن المستخدم مسجلاً أو ليس لديه شركة، يمكن إرجاع صفحة فارغة أو رسالة توضيحية
        return render(request, 'over_view_pro.html', {})

    # الإحصائيات الخاصة بالشركة
    total_categories = Category.objects.filter(company=company).count()
    total_subcategories = SubCategory.objects.filter(category__company=company).count()
    all_products = Product.objects.filter(subcategory__category__company=company)
    total_products = all_products.count()
    total_stock = sum([p.quantity for p in all_products])

    # حساب نسبة المنتجات المتوفرة
    available_products = Product.objects.filter(quantity__gt=0, subcategory__category__company=company).count()
    available_percentage = (available_products / total_products * 100) if total_products > 0 else 0

    # بيانات الرسم البياني للفئات الرئيسية الخاصة بالشركة
    categories = Category.objects.filter(company=company)
    category_names = []
    product_counts = []
    stock_counts = []
    for cat in categories:
        products_in_cat = Product.objects.filter(subcategory__category=cat)
        category_names.append(cat.name)
        product_counts.append(products_in_cat.count())
        stock_counts.append(sum([p.quantity for p in products_in_cat]))

    context = {
        'total_categories': total_categories,
        'total_subcategories': total_subcategories,
        'total_products': total_products,
        'total_stock': total_stock,
        'available_percentage': round(available_percentage, 2),
        'category_names': json.dumps(category_names),
        'product_counts': json.dumps(product_counts),
        'stock_counts': json.dumps(stock_counts),
    }
    return render(request, 'over_view_pro.html', context)
def product_edit(request, product_id):
    """
    معالجة تعديل المنتج عبر POST وإرجاع المستخدم إلى صفحة المنتجات.
    """
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح.')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء الموجودة في النموذج.')
    return redirect('product_list')


def product_delete(request, product_id):
    """
    معالجة حذف المنتج عبر POST وإرجاع المستخدم إلى صفحة المنتجات.
    """
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'تم حذف المنتج بنجاح.')
    return redirect('product_list')
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Supplier, PurchaseOrder, PurchaseItem, Product, Inventory,
    Company, Category, SubCategory
)
from .form import (
    PurchaseOrderForm, PurchaseItemForm, 
    PurchaseOrderWithItemForm, SupplierForm
)

# -------------------------------------------
# إدارة الموردين وطلبات الشراء
# -------------------------------------------

# عرض قائمة الموردين (الشركات المسجلة في النظام)
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


# AMOON_app/views.py

from django.shortcuts import render, get_object_or_404
from .models import Supplier, Company, Category

def supplier_categories_view(request, supplier_id):
    """
    تعرض جميع الفئات والفئات الفرعية الخاصة بالشركة المرتبطة بهذا المورد.
    """
    # جلب المورد المطلوب
    supplier = get_object_or_404(Supplier, pk=supplier_id)

    # جلب كائن الشركة حسب الاسم المحفوظ في company_name
    company = Company.objects.filter(name=supplier.company_name).first()

    # في حال لم توجد شركة بنفس الاسم، لن تظهر فئات
    if company:
        # جلب جميع الفئات المرتبطة بالشركة، مع الفئات الفرعية (subcategories) بشكل مسبق
        categories = Category.objects.filter(company=company).prefetch_related('subcategories')
    else:
        categories = []

    return render(request, 'supplier_categories.html', {
        'supplier': supplier,
        'categories': categories,
    })
def get_categories_by_company(request):
    """
    دالة لإرجاع قائمة الفئات المرتبطة بشركة معينة.
    """
    # نفترض أنك ترسل company_id كـ GET parameter: ?company_id=123
    company_id = request.GET.get('company_id')
    if not company_id:
        return JsonResponse({'error': 'No company_id provided'}, status=400)
    
    company = get_object_or_404(Company, pk=company_id)
    categories = Category.objects.filter(company=company)
    
    # تحويل بيانات الفئات إلى صيغة JSON
    data = []
    for cat in categories:
        data.append({
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
        })
    
    return JsonResponse({'categories': data}, safe=False)
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المورد بنجاح.")
            return redirect('supplier_list')  # أو أي صفحة مناسبة بعد الإضافة
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        form = SupplierForm()
    return render(request, 'add_supplier.html', {'form': form})
@login_required
def purchase_order_create(request, supplier_id, subcategory_id):
    # جلب المورد والفئة الفرعية
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
    # جلب جميع المنتجات التي تنتمي للفئة الفرعية
    products = Product.objects.filter(subcategory=subcategory)
    
    # البحث عن الشركة بناءً على اسم الشركة المحفوظ في المورد
    company = Company.objects.filter(name=supplier.company_name).first()
    if not company:
        messages.error(request, "لا يوجد شركة مرتبطة بهذا المورد.")
        return redirect(request.path)
    
    # إنشاء inline formset لعناصر الطلب بدون حقل "unit_price"
    OrderItemFormSet = inlineformset_factory(
        PurchaseOrder, PurchaseItem,
        fields=('product', 'quantity'),  # حذف الحقل unit_price من النموذج
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        # إنشاء طلب شراء جديد مع إجمالي مؤقت صفر
        purchase_order = PurchaseOrder.objects.create(
            supplier=company,
            total_cost=Decimal("0.00"),
            status='pending'
        )
        formset = OrderItemFormSet(request.POST, instance=purchase_order)
        # تقييد خيارات حقل المنتج لتكون المنتجات من الفئة الفرعية المحددة
        for form in formset.forms:
            form.fields['product'].queryset = products
        if formset.is_valid():
            order_items = formset.save(commit=False)
            for item in order_items:
                # تعيين سعر الوحدة تلقائيًا ليكون سعر المنتج الحالي
                item.unit_price = item.product.selling_price
                item.save()
            for deleted in formset.deleted_objects:
                deleted.delete()
            # تحديث إجمالي تكلفة الطلب بناءً على عناصره
            purchase_order.update_total_cost()
            messages.success(request, "تم إنشاء طلب الشراء بنجاح.")
            return redirect('purchase_order_detail', order_id=purchase_order.id)
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        formset = OrderItemFormSet()
        for form in formset.forms:
            form.fields['product'].queryset = products
    
    context = {
        'supplier': supplier,
        'subcategory': subcategory,
        'products': products,
        'formset': formset,
    }
    return render(request, 'add_purchase_order.html', context)
from decimal import Decimal

@login_required
def purchase_order_detail(request, order_id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=order_id)
    items = purchase_order.items.all()
    
    # حساب إجمالي المبلغ من عناصر الطلب
    total_amount = sum(item.total_price() for item in items)  # إذا كان total_price دالة، تأكد من استدعائها
    # نفترض خصم ضريبي بنسبة 10%
    tax_discount = total_amount * Decimal("0.10")
    net_total = total_amount + tax_discount
    
    context = {
        'purchase_order': purchase_order,
        'items': items,
        'total_amount': total_amount,
        'tax_discount': tax_discount,
        'net_total': net_total,
        'employee': request.user,  # الموظف الذي قام بالطلب
        'order_date': purchase_order.date,
    }
    return render(request, 'purchase_order_detail.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Product  # نموذج المنتج
from order_management.models import Order, OrderItem 
from AMOON_app.models import Notification  # نموذج الإشعارات
from order_management.models import Order
@login_required
def send_order(request, product_id):
    # جلب المنتج الأساسي لتحديد الفئة الفرعية والشركة
    product = get_object_or_404(Product, pk=product_id)
    subcategory = product.subcategory
    company = subcategory.category.company

    # جلب المورد بناءً على اسم الشركة المحفوظ في المورد (company_name)
    supplier = get_object_or_404(Supplier, company_name=company.name)
    
    # جلب جميع المنتجات التي تنتمي للفئة الفرعية المحددة
    products = Product.objects.filter(subcategory=subcategory)
    
    # إنشاء inline formset لعناصر الطلب، مع الحقول (product, quantity)
    OrderItemFormSet = inlineformset_factory(
        Order, OrderItem,
        fields=('product', 'quantity'),
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        # جلب أول ممثل (مستخدم) مرتبط بالشركة؛ يُفترض أن الشركة لديها علاقة (users)
        supplier_user = company.users.first()
        if not supplier_user:
            messages.error(request, "لا يوجد ممثل مسجل لهذه الشركة.")
            return redirect(request.path)
        
        # إنشاء طلب شراء جديد مع إجمالي مؤقت صفر
        order = Order.objects.create(
            customer=request.user,   # العميل هو المستخدم الحالي
            seller=supplier_user,      # البائع هو ممثل الشركة
            status='pending',
            total_cost=Decimal("0.00")
        )
        
        # ربط الـ formset بالطلب الذي تم إنشاؤه
        formset = OrderItemFormSet(request.POST, instance=order)
        # تحديد خيارات حقل المنتج لتقتصر على المنتجات من هذه الفئة الفرعية
        for form in formset.forms:
            form.fields['product'].queryset = products
        
        if formset.is_valid():
            order_items = formset.save(commit=False)
            for item in order_items:
                # تعيين سعر الوحدة تلقائيًا من سعر بيع المنتج
                item.unit_price = item.product.selling_price
                item.save()
            for deleted in formset.deleted_objects:
                deleted.delete()
            # تحديث إجمالي تكلفة الطلب بناءً على العناصر المضافة
            order.update_total_cost()
            messages.success(request, "تم إرسال الطلب بنجاح.")
            return redirect('order_detail', order_id=order.id)
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة.")
    else:
        formset = OrderItemFormSet()
        for form in formset.forms:
            form.fields['product'].queryset = products

    context = {
        'supplier': supplier,
        'subcategory': subcategory,
        'products': products,
        'formset': formset,
    }
    return render(request, 'send_order_form.html', context)

@login_required
@login_required
def purchase_order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    accepted_count = orders.filter(status='accepted').count()
    rejected_count = orders.filter(status='rejected').count()
    cancelled_count = orders.filter(status='cancelled').count()
    offer_sent_count = orders.filter(status='offer_sent').count()
    
    # إذا كنت تستخدم المتغيرات supplier و subcategory لعرض رابط إنشاء طلب شراء جديد،
    # يمكنك تمريرهم إذا كانت موجودة، مثلاً:
    supplier = None
    subcategory = None
    # يمكنك تعيينهما بناءً على منطق مشروعك، على سبيل المثال:
    if orders.exists():
        supplier = orders.first().seller  # مثال: نأخذ المورد من أول طلب
        # subcategory قد تعتمد على منتج معين أو منطق آخر
        subcategory = orders.first().items.first().product.subcategory if orders.first().items.exists() else None
    
    context = {
        'orders': orders,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
        'offer_sent_count': offer_sent_count,
        'supplier': supplier,
        'subcategory': subcategory,
    }
    return render(request, 'purchase_order_list.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CV, Experience, Education
from django.contrib import messages

@login_required
def cv_dashboard(request):
    try:
        cv = request.user.cv
    except CV.DoesNotExist:
        cv = None
    
    experiences = Experience.objects.filter(cv__user=request.user) if cv else []
    educations = Education.objects.filter(cv__user=request.user) if cv else []
    
    return render(request, 'cv/cv_dashboard.html', {
        'cv': cv,
        'experiences': experiences,
        'educations': educations,
    })
# views.pyfrom django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime
import json

# استيراد النماذج والنماذج المجمعة (FormSets)
from .form import (
    CVForm,
    ExperienceFormSet,
    EducationFormSet,
    LanguageFormSet,
    CertificationFormSet,
    SocialLinkFormSet,
    SkillFormSet
)
from .models import CV, Experience, Education, Skill  # تأكدي من وجود نموذج Skill

# forms.py (تعديل CVForm)


# views.py (تعديل الجزء المتعلق بالمهارات)
@login_required
def create_update_cv(request):
    try:
        cv = CV.objects.get(user=request.user)
    except CV.DoesNotExist:
        cv = None

    if request.method == 'POST':
        cv_form = CVForm(request.POST, request.FILES, instance=cv)
        experience_formset = ExperienceFormSet(request.POST, prefix='experiences', instance=cv)
        education_formset = EducationFormSet(request.POST, prefix='educations', instance=cv)
        language_formset = LanguageFormSet(request.POST, prefix='languages', instance=cv)
        certification_formset = CertificationFormSet(request.POST, prefix='certifications', instance=cv)
        social_link_formset = SocialLinkFormSet(request.POST, prefix='social_links', instance=cv)
        skill_formset = SkillFormSet(request.POST, prefix='skills', instance=cv)

        if all([
            cv_form.is_valid(),
            experience_formset.is_valid(),
            education_formset.is_valid(),
            language_formset.is_valid(),
            certification_formset.is_valid(),
            social_link_formset.is_valid(),
            skill_formset.is_valid()
        ]):
            new_cv = cv_form.save(commit=False)
            new_cv.user = request.user
            new_cv.save()  # حفظ الـ CV أولاً
            
            # حفظ جميع الـ FormSets
            experience_formset.instance = new_cv
            experience_formset.save()
            
            education_formset.instance = new_cv
            education_formset.save()
            
            language_formset.instance = new_cv
            language_formset.save()
            
            certification_formset.instance = new_cv
            certification_formset.save()
            
            social_link_formset.instance = new_cv
            social_link_formset.save()
            
            skill_formset.instance = new_cv
            skill_formset.save()

            messages.success(request, "تم حفظ السيرة الذاتية بنجاح")
            return redirect('cv_dashboard')
        else:
            messages.error(request, "توجد أخطاء في النموذج. الرجاء مراجعة البيانات.")
    else:
        cv_form = CVForm(instance=cv)
        experience_formset = ExperienceFormSet(prefix='experiences', instance=cv)
        education_formset = EducationFormSet(prefix='educations', instance=cv)
        language_formset = LanguageFormSet(prefix='languages', instance=cv)
        certification_formset = CertificationFormSet(prefix='certifications', instance=cv)
        social_link_formset = SocialLinkFormSet(prefix='social_links', instance=cv)
        skill_formset = SkillFormSet(prefix='skills', instance=cv)

    context = {
        'cv_form': cv_form,
        'form_sections': [
            {
                'title': 'اللغات',
                'formset': language_formset,
                'prefix': 'languages'
            },
            {
                'title': 'الشهادات',
                'formset': certification_formset,
                'prefix': 'certifications'
            },
            {
                'title': 'الخبرات العملية',
                'formset': experience_formset,
                'prefix': 'experiences'
            },
            {
                'title': 'التعليم',
                'formset': education_formset,
                'prefix': 'educations'
            },
            {
                'title': 'روابط التواصل',
                'formset': social_link_formset,
                'prefix': 'social_links'
            },
            {
                'title': 'المهارات',
                'formset': skill_formset,
                'prefix': 'skills'
            }
        ]
    }

    return render(request, 'cv/create_update_cv.html', context)

@login_required
def view_cv(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        if not request.user.is_superuser and request.user != user:
            messages.error(request, "ليس لديك صلاحية لعرض هذه السيرة الذاتية")
            return redirect('home')
    else:
        user = request.user
    
    try:
        cv = user.cv
    except CV.DoesNotExist:
        messages.info(request, "ليس لديك سيرة ذاتية بعد. الرجاء إنشاء سيرة ذاتية أولاً.")
        return redirect('cv_dashboard')
    
    experiences = Experience.objects.filter(cv=cv)
    educations = Education.objects.filter(cv=cv)
    # بالنسبة للمهارات، يتم الحصول على القائمة من علاقة ManyToMany
    skills = [skill.name for skill in cv.skills.all()]
    
    return render(request, 'cv/view_cv.html', {
        'cv': cv,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
        'viewing_user': user,
    })
from django import template

register = template.Library()

@register.filter
def split_list(value):
    """
    تقسيم النص إلى قائمة باستخدام الفاصلة كفاصل
    """
    if value:
        return [item.strip() for item in value.split(',') if item.strip()]
    return []

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CV
from .form import CVForm

from django.shortcuts import render, redirect
from .form import CVForm, LanguageFormSet, CertificationFormSet, ExperienceFormSet, EducationFormSet, SocialLinkFormSet, SkillFormSet

def create_cv(request):
    if request.method == 'POST':
        cv_form = CVForm(request.POST)
        language_formset = LanguageFormSet(request.POST, prefix='languages')
        certification_formset = CertificationFormSet(request.POST, prefix='certifications')
        experience_formset = ExperienceFormSet(request.POST, prefix='experiences')
        education_formset = EducationFormSet(request.POST, prefix='educations')
        social_link_formset = SocialLinkFormSet(request.POST, prefix='social_links')
        skill_formset = SkillFormSet(request.POST, prefix='skills')

        if all([
            cv_form.is_valid(),
            language_formset.is_valid(),
            certification_formset.is_valid(),
            experience_formset.is_valid(),
            education_formset.is_valid(),
            social_link_formset.is_valid(),
            skill_formset.is_valid()
        ]):
            cv = cv_form.save(commit=False)
            cv.user = request.user
            cv.save()

            # حفظ جميع الـ Formsets
            language_formset.instance = cv
            language_formset.save()

            certification_formset.instance = cv
            certification_formset.save()

            experience_formset.instance = cv
            experience_formset.save()

            education_formset.instance = cv
            education_formset.save()

            social_link_formset.instance = cv
            social_link_formset.save()

            skill_formset.instance = cv
            skill_formset.save()

            return redirect('view_cv')

    else:
        cv_form = CVForm()
        language_formset = LanguageFormSet(prefix='languages')
        certification_formset = CertificationFormSet(prefix='certifications')
        experience_formset = ExperienceFormSet(prefix='experiences')
        education_formset = EducationFormSet(prefix='educations')
        social_link_formset = SocialLinkFormSet(prefix='social_links')
        skill_formset = SkillFormSet(prefix='skills')

    context = {
        'cv_form': cv_form,
        'language_formset': language_formset,
        'certification_formset': certification_formset,
        'experience_formset': experience_formset,
        'education_formset': education_formset,
        'social_link_formset': social_link_formset,
        'skill_formset': skill_formset
    }

    return render(request, 'cv/create_cv.html', context)

