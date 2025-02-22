from django.db import models
from decimal import Decimal

class User(models.Model):
    ADMIN = 'admin'
    USER = 'user'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    email_id = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user_id} - {self.product.product_id}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user_id} - {self.product.product_id} (x{self.quantity})"

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_purchases = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00")) 


    def __str__(self):
        return f"Customer {self.customer_id} (User {self.user.user_id})"

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
