from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import check_password
from django.forms import inlineformset_factory
from .models import Company, Employee, Department,PurchaseOrder, Supplier,JOB_TITLES,Training, PurchaseItem,DEPARTMENTS, Category,SubCategory,CustomUser, Account, JournalEntry, JournalEntryLine ,EmployeeActivity,Product
from django.forms import ModelForm, inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'location', 'manager']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ادخل مكان الإدارة'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'اسم الإدارة',
            'location': 'المكان',
            'manager': 'مدير الإدارة',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تقييد خيارات حقل المدير بحيث تظهر فقط المديرين الذين لديهم job_title = 'Manager'
        # ويمكننا أيضًا استبعاد المديرين المرتبطين بإدارة بالفعل
        assigned_managers = Department.objects.exclude(manager__isnull=True).values_list('manager_id', flat=True)
        qs = CustomUser.objects.filter(job_title='Manager').exclude(id__in=assigned_managers)
        self.fields['manager'].queryset = qs


JournalEntryLineFormSet = inlineformset_factory(
    JournalEntry,
    JournalEntryLine,
    fields=['account', 'partner', 'label', 'debit', 'credit', 'tax_grids'],
    extra=1,
    can_delete=True
)

JournalEntryLineFormSet = inlineformset_factory(
    JournalEntry,
    JournalEntryLine,
    fields=['account', 'partner', 'label', 'debit', 'credit', 'tax_grids'],
    extra=1,
    can_delete=True
)

# نموذج إضافة موظف (AddEmployeeForm)
class AddEmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    # سيتم تعيين خيارات الحقل job_title ديناميكيًا في المُنشئ
    job_title = forms.ChoiceField(choices=[], label="Job Title")

    class Meta:
        model = CustomUser
        # استخدام الحقل الصحيح 'job_title' بدلاً من 'JOB_TITLES'
        fields = ['username', 'password', 'first_name', 'last_name', 'job_title', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # استيراد قائمة المسميات الوظيفية من النماذج وتعيينها كخيارات
       
        self.fields['job_title'].choices = JOB_TITLES

# نموذج تسجيل دخول الشركة (CompanyLoginForm)
class CompanyLoginForm(forms.Form):
    company_username = forms.CharField(label="اسم المستخدم للشركة")
    company_password = forms.CharField(label="كلمة المرور للشركة", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        company_username = cleaned_data.get('company_username')
        company_password = cleaned_data.get('company_password')
        try:
            company = Company.objects.get(company_username=company_username)
            if not check_password(company_password, company.company_password):
                raise forms.ValidationError("كلمة المرور غير صحيحة!")
        except Company.DoesNotExist:
            raise forms.ValidationError("اسم المستخدم غير صحيح!")
        return cleaned_data

# نموذج تسجيل شركة (CompanyRegistrationForm)
class CompanyRegistrationForm(forms.ModelForm):
    max_employee_count = forms.IntegerField(label="عدد الموظفين", min_value=1)
    
    class Meta:
        model = Company
        fields = ['name', 'company_username', 'address', 'company_password', 'max_employee_count']
        widgets = {
            'company_password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

# نموذج تسجيل مستخدم (RegisterUserForm)
class RegisterUserForm(forms.ModelForm):
    # حقل إضافي غير موجود في النموذج
    company_code = forms.CharField(label="Company Code", max_length=10)
    
    # تعريف الحقول بشكل صريح
    first_name = forms.CharField(label="First Name", max_length=30)
    last_name = forms.CharField(label="Last Name", max_length=30)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    
    class Meta:
        model = User  # من المفترض أن يكون CustomUser هو المستخدم النشط
        fields = ['first_name', 'last_name', 'email', 'password', 'department', 'job_title']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }
    
    def clean_company_code(self):
        company_code = self.cleaned_data.get('company_code')
        # التحقق من وجود الشركة
        company = Company.objects.filter(code=company_code).first()
        if not company:
            raise forms.ValidationError("❌ كود الشركة غير صحيح، الرجاء التأكد من الكود.")
        # التحقق من عدم وصول عدد الموظفين للحد الأقصى
        if company.employee_count >= company.max_employee_count:
            raise forms.ValidationError("❌ تم الوصول إلى الحد الأقصى لعدد الموظفين في هذه الشركة.")
        return company_code

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email 

    def save(self, commit=True):
        user = super().save(commit=False)
        # تشفير كلمة المرور
        user.set_password(self.cleaned_data['password'])
        
        # ربط المستخدم مع الشركة باستخدام كود الشركة
        company_code = self.cleaned_data.get('company_code')
        try:
            company = Company.objects.get(code=company_code)
            user.company = company
        except Company.DoesNotExist:
            raise ValueError("❌ كود الشركة غير صحيح، لا يمكن حفظ المستخدم بدون شركة.")
        
        # تعيين المسمي الوظيفي
        user.job_title = self.cleaned_data.get('job_title')
        
        if commit:
            user.save()
        return user

# نموذج تعديل بيانات الموظف (EmployeeEditForm)
class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'job_title', 'department']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

        

# form.py
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

class JournalEntryLineFormSetCustom(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_debit = 0
        total_credit = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total_debit += form.cleaned_data.get('debit', 0)
                total_credit += form.cleaned_data.get('credit', 0)
        if total_debit != total_credit:
            raise ValidationError("يجب أن يتساوى مجموع المدين مع مجموع الدائن.")

        
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'code', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
           'category' : forms.Select(attrs={'class': 'form-control'}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = EmployeeActivity
        fields = [ 'action', 'start_date', 'end_date']
class TrainingForm(forms.ModelForm):
 class Meta:
        model = Training
        fields = ['title', 'start_date', 'end_date', 'hours']
        # forms.py
from django import forms
from .models import JournalEntry, JournalEntryLine

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['reference', 'accounting_date', 'comment']
        widgets = {
            'accounting_date': forms.DateInput(attrs={'type': 'date'}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class JournalEntryLineForm(forms.ModelForm):
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'debit', 'credit']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'subcategory', 
            'name', 
            'description', 
            'purchase_total_cost', 
            'purchase_quantity', 
            'selling_price', 
            'quantity'
        ]
        
        

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الفئة الفرعية'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'وصف الفئة الفرعية', 'rows': 3}),
        }
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الفئة'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'وصف الفئة', 'rows': 3}),
        }

class PurchaseOrderForm(forms.ModelForm):
    # عرض شركات النظام في القائمة
    supplier = forms.ModelChoiceField(
        queryset=Company.objects.all(),  # نعرض شركات النظام
        empty_label="اختر شركة مورد",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = PurchaseOrder
        fields = ['supplier']
    
    def save(self, commit=True):
        # الحصول على الشركة المختارة
        company = self.cleaned_data.get('supplier')
        # البحث عن كائن المورد المرتبط بالشركة (يفترض أن اسم الشركة في Supplier يطابق company.name)
        supplier_instance = Supplier.objects.filter(company_name=company.name).first()
        if not supplier_instance:
            raise forms.ValidationError("لا يوجد مورد مرتبط بهذه الشركة")
        self.instance.supplier = supplier_instance
        return super().save(commit=commit)
    
class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'unit_price']
        from django import forms
from .models import Company, Category, SubCategory, Product  # تأكد من استيراد النماذج الصحيحة

class PurchaseOrderWithItemForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        empty_label="اختر المورد",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'supplier-select'})
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),  # سيتم تحديثه عبر AJAX
        empty_label="اختر المنتج",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'product-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'الكمية المطلوبة'})
    )

class SupplierForm(forms.ModelForm):
    # حقل لاختيار الشركة من النظام
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        empty_label="اختر شركة من النظام",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Supplier
        # نستبعد حقل company_name لأنه سيتم تعيينه تلقائياً من الشركة المختارة
        fields = [ 'user','company', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم جهة الاتصال'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'العنوان', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # عند الحفظ، نعين اسم الشركة بناءً على الشركة المختارة
        instance.company_name = self.cleaned_data['company'].name
        if commit:
            instance.save()
        return instance
    
        from django import forms
from .models import Company, Category

class CompanyCategoryForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        empty_label="اختر الشركة",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'company-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # سيتم تحديثها عبر AJAX
        empty_label="اختر الفئة الرئيسية",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )


from django import forms
from django.forms import inlineformset_factory
from .models import CV, Language, Certification, Experience, Education, SocialLink, Skill

# Form للسيرة الذاتية الأساسية
class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['title', 'summary', 'phone']  # إزالة 'skills' من هنا
        labels = {
            'title': 'المسمى الوظيفي',
            'summary': 'ملخص عنك',
            'phone': 'رقم الهاتف'
        }

    




# Formsets للنماذج المرتبطة
LanguageFormSet = inlineformset_factory(
    CV,
    Language,
    fields=('name', 'proficiency'),
    extra=1,
    labels={
        'name': 'اللغة',
        'proficiency': 'مستوى الإتقان'
    }
)

CertificationFormSet = inlineformset_factory(
    CV,
    Certification,
    fields=('title', 'institution', 'date_obtained'),
    extra=1,
    labels={
        'title': 'عنوان الشهادة',
        'institution': 'المؤسسة المانحة',
        'date_obtained': 'تاريخ الحصول'
    },
    widgets={
        'date_obtained': forms.DateInput(attrs={'type': 'date'})
    }
)

ExperienceFormSet = inlineformset_factory(
    CV,
    Experience,
    fields=('job_title', 'company', 'start_date', 'end_date', 'currently_working', 'description'),
    extra=1,
    labels={
        'job_title': 'المسمى الوظيفي',
        'company': 'الشركة',
        'start_date': 'تاريخ البدء',
        'end_date': 'تاريخ الانتهاء',
        'currently_working': 'ما زلت أعمل هنا',
        'description': 'الوصف'
    },
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'})
    }
)

EducationFormSet = inlineformset_factory(
    CV,
    Education,
    fields=('degree', 'institution', 'field_of_study', 'start_date', 'end_date', 'currently_studying'),
    extra=1,
    labels={
        'degree': 'الدرجة العلمية',
        'institution': 'المؤسسة التعليمية',
        'field_of_study': 'التخصص',
        'start_date': 'تاريخ البدء',
        'end_date': 'تاريخ الانتهاء',
        'currently_studying': 'ما زلت أدرس هنا'
    },
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'})
    }
)

SocialLinkFormSet = inlineformset_factory(
    CV,
    SocialLink,
    fields=('platform', 'url'),
    extra=1,
    labels={
        'platform': 'المنصة',
        'url': 'الرابط'
    }
)


SkillFormSet = inlineformset_factory(
    CV,
    Skill,
    fields=('name', 'proficiency'),
    extra=1,
    can_delete=True
)
