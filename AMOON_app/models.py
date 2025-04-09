from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission 
import random 
import string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse  # تأكد من استيراد الدالة reverse



def generate_company_code():
    length = 8
    characters = string.ascii_uppercase + string.digits 
    return ''.join(random.choice(characters) for _ in range(length))

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True, default=generate_company_code)
    company_username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    company_password = models.CharField(max_length=100)
    address = models.TextField()
    max_employee_count = models.PositiveIntegerField()
    min_employee_count = models.PositiveIntegerField(default=1, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    employee_count = models.PositiveIntegerField(default=0)  # هذا الحقل سيتم تحديثه

    def __str__(self):
        return self.name

    def update_employee_count(self):
        """
        تحديث عدد الموظفين استنادًا إلى عدد الموظفين المرتبطين بهذه الشركة.
        تأكد من ضبط related_name في علاقة ForeignKey بنموذج Employee.
        """
        # لاحظ أننا نستخدم related_name الصحيح للعلاقة (في نموذج CustomUser اخترت "users")
        self.employee_count = self.users.count()
        self.save(update_fields=['employee_count'])

STATE_CHOICES = [
    ('draft', 'مسودة'),
    ('posted', 'مرحل'),
]

DEPARTMENTS = [
    ('HR', 'Human Resources'),
    ('IT', 'Information Technology'),
    ('Finance', 'Finance'),
    ('Sales', 'Sales'),
    ('Other', 'Other'),
]

JOB_TITLES = [
    ('Manager', 'Manager'),
    ('Accountant', 'Accountant'),
    ('Developer', 'Developer'),
    ('HR', 'HR'),
    ('Sales', 'Sales'),
    ('Other', 'Other'),
]

DEPARTMENT_CHOICES = [
    ('HR', 'Human Resources'),
    ('IT', 'Information Technology'),
    ('Finance', 'Finance'),
    ('Sales', 'Sales'),
    ('Other', 'Other'),
]
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    hire_date = models.DateField(default=now)  # تاريخ التوظيف
    last_seen = models.DateTimeField(auto_now=True )  # يتم تحديثه تلقائيًا عند آخر نشاط
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="users"
    )
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENTS,
        default='Other',
        blank=True
    )
    job_title = models.CharField(
        max_length=50,
        choices=JOB_TITLES,
        default='Other',
        blank=True
    )
    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)
    USER_TYPE_CHOICES = (
        ('company', 'Company'),
        ('employee', 'Employee'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')
    position = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.username
    def get_cv_url(self):
        try:
            return reverse('view_user_cv', args=[self.id])  # تم إصلاح الأقواس هنا
        except Exception as e:  # تحديد نوع الاستثناء
            print(f"Error generating CV URL: {e}")  # طباعة الخطأ للتصحيح
            return None
    
    def has_cv(self):
        return hasattr(self, 'cv')

def update_employee_count_on_save(sender, instance, created, **kwargs):
    if created:
        company = instance.company
        # تحديث العدد بناءً على عدد الموظفين الحاليين
        company.employee_count = company.employees.count()
        # استخدم update_fields لتحديث الحقل المطلوب فقط
        company.save(update_fields=['employee_count'])

# عند حذف موظف، نقوم بتحديث employee_count في الشركة
@receiver(post_delete, sender=CustomUser)
def update_employee_count_on_delete(sender, instance, **kwargs):
    company = instance.company
    company.employee_count = company.employees.count()
    company.save(update_fields=['employee_count'])
class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        verbose_name="اسم الإدارة"
    )
    location = models.CharField(max_length=100, verbose_name="المكان")

    # الربط مع نموذج CustomUser للحصول على المدير الذي job_title = 'Manager'
    manager = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'user_type': 'employee', 'job_title': 'Manager'},
        related_name='managed_department'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="departments",
        verbose_name="الشركة"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "إدارة"
        verbose_name_plural = "الإدارات"

    def __str__(self):
        return f"{self.get_name_display()} - مدير: {self.manager} - {self.company.name}"
    

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee", null=True, blank=True)

    def __str__(self):
        return self.name


    @property
    def classification(self):
        # الحسابات من نوع "أصل" و"مصروف" تكون مدينة، 
        # أما "خصم" و"دخل" فتكون دائنة.
        if self.type in ['asset', 'expense']:
            return "مدين"
        elif self.type in ['liability', 'income']:
            return "دائن"
        else:
            return ""

class Journal(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def __str__(self):
        return f"{self.reference} - {self.journal.name}"
class Account(models.Model):
    CATEGORY_CHOICES = [
        ('asset', 'أصول'),
        ('liability', 'خصوم'),
        ('equity', 'حقوق ملكية'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="اسم الحساب")
    code = models.CharField(max_length=20, unique=True, verbose_name="كود الحساب")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        null=True,      # السماح بأن يكون فارغًا
        blank=True,     # السماح بتقديمه كخيار فارغ في النماذج
        verbose_name="تصنيف الحساب"
    )    # السماح بتقديمه كخيار فارغ في النماذج
    def __str__(self):
        return f"{self.code} - {self.name}"

class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey('AMOON_app.JournalEntry', related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    partner = models.CharField(max_length=100, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_grids = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.account.name} | مدين: {self.debit} | دائن: {self.credit}"



class EmployeeActivity(models.Model):
    """ جدول خاص بأنشطة الموظفين """
    id = models.AutoField(primary_key=True)  # معرف النشاط
    employee  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="activities")  # ربط بالنموذج Employee
    action = models.CharField(max_length=255)  # وصف النشاط
    start_date = models.DateField(default=now)  # تاريخ البداية
    end_date = models.DateField(null=True, blank=True)  # تاريخ النهاية (اختياري)
    timestamp = models.DateTimeField(default=now)  # وقت الإدخال
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.employee.user.username} - {self.action} ({self.start_date} - {self.end_date or 'جاري'})"

class Training(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="employee_trainings")
    title = models.CharField(max_length=200)
    hours = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(CustomUser, related_name='participant_trainings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.title} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "تدريب"
        verbose_name_plural = "التدريبات"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.employee and not self.participants.filter(id=self.employee.id).exists():
            self.participants.add(self.employee)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"من {self.sender.username} إلى {self.receiver.username} - {self.timestamp.strftime('%Y-%m-%d %I:%M %p')}"
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="المستخدم"
    )
    message = models.CharField(max_length=255, verbose_name="الرسالة")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="الرابط")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="وقت الإنشاء")

    def __str__(self):
        return f"{self.user.username} - {self.message}"
class JournalEntry(models.Model):
    reference = models.CharField(max_length=50, unique=True, verbose_name="رقم القيد")
    accounting_date = models.DateField(default=timezone.now, verbose_name="تاريخ القيد")
    comment = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='draft', verbose_name="الحالة")
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT, verbose_name="الدورية")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="أُنشئ بواسطة")
    

    def __str__(self):
        return self.reference


    
from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="categories")

    name = models.CharField(max_length=255, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الفئة")

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="الفئة الرئيسية")
    name = models.CharField(max_length=255, verbose_name="اسم الفئة الفرعية")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الفئة الفرعية")

    def __str__(self):
        return f"{self.category.name} - {self.name}"
class Product(models.Model):

    id = models.AutoField(primary_key=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', verbose_name="الفئة الفرعية")
    name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المنتج")
    
    # تكلفة الشراء الإجمالية للدفعة المشتراة
    purchase_total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="التكلفة الإجمالية للشراء"
    )
    # عدد الوحدات المشتراة في الدفعة
    purchase_quantity = models.PositiveIntegerField(
        default=1, verbose_name="كمية الشراء"
    )
    # سعر البيع الحالي (يمكن أن يتم تعديله يدويًا)
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="سعر البيع"
    )
    # الكمية المتوفرة في المخزن
    quantity = models.PositiveIntegerField(default=0, verbose_name="الكمية المتوفرة")

    def __str__(self):
        return self.name

    @property
    def unit_purchase_cost(self):
        """حساب تكلفة الشراء للوحدة الواحدة"""
        if self.purchase_quantity:
            return self.purchase_total_cost / self.purchase_quantity
        return 0

    def unit_purchase_cost(self):
        """
        تحسب تكلفة الشراء للوحدة الواحدة بناءً على التكلفة الإجمالية وعدد الوحدات.
        """
        if self.purchase_quantity > 0:
            return self.purchase_total_cost / self.purchase_quantity
        return 0

    def suggested_selling_price(self, markup_percentage=30):
        """
        تقترح سعر بيع للوحدة بناءً على هامش ربح محدد (افتراضي 30%).
        يمكن تمرير نسبة هامش الربح كقيمة مئوية.
        """
        unit_cost = self.unit_purchase_cost()
        # حساب الزيادة بناءً على النسبة: (هامش الربح / 100) * تكلفة الوحدة
        suggested_price = unit_cost + (unit_cost * markup_percentage / 100)
        return round(suggested_price, 2)


User = get_user_model()


class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()

    def __str__(self):
        return self.company_name
    
class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('Pending', 'معلق'), ('Accepted', 'مقبول'), ('Rejected', 'مرفوض')], default='Pending')

    def __str__(self):
        return f"طلب شراء من {self.supplier.company_name} - {self.date}"
    
    def update_total_cost(self):
        self.total_cost = sum(item.cost for item in self.purchaseitem_set.all())
        self.save()

class PurchaseItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="purchase_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.unit_price

class Inventory(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="inventories")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.supplier.name}: {self.quantity}"


class CV(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv')
    phone = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=100, verbose_name="المسمى الوظيفي")
    summary = models.TextField(verbose_name="ملخص عنك")
   


    def __str__(self):
        return f"السيرة الذاتية لـ {self.user.get_full_name()}"
class Certification(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=100, verbose_name="عنوان الشهادة")
    institution = models.CharField(max_length=100, verbose_name="المؤسسة المانحة")
    date_obtained = models.DateField(verbose_name="تاريخ الحصول عليها")

    def __str__(self):
        return f"{self.title} من {self.institution}"
class Language(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=50, verbose_name="اللغة")
    proficiency = models.CharField(max_length=20, choices=[
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('native', 'لغة أم'),
    ], verbose_name="مستوى الإتقان")

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"
class Experience(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100, verbose_name="المسمى الوظيفي")
    company = models.CharField(max_length=100, verbose_name="الشركة")
    start_date = models.DateField(verbose_name="تاريخ البدء")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء", null=True, blank=True)
    currently_working = models.BooleanField(default=False, verbose_name="ما زلت أعمل هنا")
    description = models.TextField(verbose_name="الوصف")

class Education(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=100, verbose_name="الدرجة العلمية")
    institution = models.CharField(max_length=100, verbose_name="المؤسسة التعليمية")
    field_of_study = models.CharField(max_length=100, verbose_name="التخصص")
    start_date = models.DateField(verbose_name="تاريخ البدء")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء", null=True, blank=True)
    currently_studying = models.BooleanField(default=False, verbose_name="ما زلت أدرس هنا")

class SocialLink(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField(max_length=100)  # مثل LinkedIn, Facebook, Twitter, ...
    url = models.URLField()

    def __str__(self):
        return f"{self.platform}: {self.url}"
class Skill(models.Model):
    cv = models.ForeignKey(
        CV, 
        on_delete=models.CASCADE, 
        related_name='skills'  # التصحيح هنا
    )
    PROFICIENCY_CHOICES = [
        (20, 'مبتدئ (20%)'),
        (40, 'مبتدئ متقدم (40%)'),
        (60, 'متوسط (60%)'),
        (80, 'متقدم (80%)'),
        (100, 'خبير (100%)'),
    ]

    name = models.CharField(max_length=100, verbose_name="المهارة")
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=30)

    def __str__(self):
        return f"{self.name} ({self.get_proficiency_display()})"