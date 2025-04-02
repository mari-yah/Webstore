from django.db import models
from decimal import Decimal

from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserRadioWatchManager(BaseUserManager):
    def create_user(self, user_name, email_id, password=None):
        if not user_name:
            raise ValueError("Users must have a username")
        if not email_id:
            raise ValueError("Users must have an email address")
        user = self.model(user_name=user_name, email_id=self.normalize_email(email_id))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, email_id, password=None):
        user = self.create_user(user_name, email_id, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class UserRadioWatch(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100, unique=True)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True, default=now)
    total_purchases = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Set the username field to be 'user_name'
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = ["email_id"]

    objects = UserRadioWatchManager()

    def __str__(self):
        return self.user_name



class Product(models.Model):
    product_id = models.CharField(max_length=25, primary_key=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20)
    brand_name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.product_name


class Wishlist(models.Model):
    user = models.ForeignKey('RadioWatch.UserRadioWatch', on_delete=models.CASCADE)  # ✅ Fixed Reference
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} - {self.product.product_id}"


class Cart(models.Model):
    user = models.ForeignKey('RadioWatch.UserRadioWatch', on_delete=models.CASCADE)  # ✅ Fixed Reference
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} - {self.product.product_id} (x{self.quantity})"


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('RadioWatch.UserRadioWatch', on_delete=models.CASCADE, related_name="customer_profile")  # ✅ Fixed Reference
    total_purchases = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Customer {self.customer_id} (User {self.user.pk})"


class PurchaseHistory(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase {self.purchase_id}: Customer {self.customer.customer_id} - Product {self.product.product_id}"


class Bargain(models.Model):
    bargain_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calculate_discounted_price(self):
        actual_price = self.product.price
        discount = 0

        if self.customer.total_purchases > 5:
            discount = max(discount, 10)

        if self.customer.total_spent >= 20000:
            discount = max(discount, 20)

        if self.customer.total_purchases == 0:
            discount = max(discount, 5)

        self.final_price = (actual_price * (1 - Decimal(discount) / 100)).quantize(Decimal("0.00"))
        self.save()
        return self.final_price

    def __str__(self):
        return f"Bargain {self.bargain_id}: Customer {self.customer.customer_id} - Product {self.product.product_id} - Final Price {self.final_price}"
