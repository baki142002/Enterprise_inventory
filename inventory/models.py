from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=160)
    contact_person = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=160)
    sku = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    unit = models.CharField(max_length=40, default="piece")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def stock_value(self): return self.quantity * self.purchase_price
    @property
    def is_low_stock(self): return self.quantity <= self.reorder_level
    def __str__(self): return f"{self.name} ({self.sku})"

class StockTransaction(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TYPES = [(IN, "Stock In"), (OUT, "Stock Out"), (ADJUSTMENT, "Adjustment")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=12, choices=TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"{self.product.sku} {self.transaction_type} {self.quantity}"

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    sold_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    @property
    def total(self): return self.quantity * self.unit_price
    def __str__(self): return f"Sale {self.product.sku} x {self.quantity}"
class UserAccessLog(models.Model):
    ACTION_CHOICES = (
        ('LOGIN', 'User Logged In'),
        ('REGISTER', 'Account Created'),
        ('LOGOUT', 'User Logged Out'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically captures YYYY-MM-DD HH:MM:SS
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "User Access Log"
        verbose_name_plural = "User Access Logs"

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=160)
    contact_person = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=160)
    sku = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    unit = models.CharField(max_length=40, default="piece")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def stock_value(self): return self.quantity * self.purchase_price
    @property
    def is_low_stock(self): return self.quantity <= self.reorder_level
    def __str__(self): return f"{self.name} ({self.sku})"

class StockTransaction(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TYPES = [(IN, "Stock In"), (OUT, "Stock Out"), (ADJUSTMENT, "Adjustment")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=12, choices=TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"{self.product.sku} {self.transaction_type} {self.quantity}"

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    sold_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    @property
    def total(self): return self.quantity * self.unit_price
    def __str__(self): return f"Sale {self.product.sku} x {self.quantity}"
class UserAccessLog(models.Model):
    ACTION_CHOICES = (
        ('LOGIN', 'User Logged In'),
        ('REGISTER', 'Account Created'),
        ('LOGOUT', 'User Logged Out'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically captures YYYY-MM-DD HH:MM:SS
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "User Access Log"
        verbose_name_plural = "User Access Logs"

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    phone_number = models.CharField(max_length=20, help_text="e.g. +639856254420")
    is_2fa_enabled = models.BooleanField(default=True, verbose_name="2FA Enabled")

    class Meta:
        verbose_name = "Admin 2FA Security Profile"
        verbose_name_plural = "Admin 2FA Security Profiles"

    def __str__(self):
        return f"{self.user.username} ({self.phone_number})"


class SMSVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        return not self.is_used and (now - self.created_at) < timedelta(minutes=5)

    @classmethod
    def generate_code(cls, user):
        import random
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        otp = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, code=otp)