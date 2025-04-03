from django.contrib import admin
from .models import UserRadioWatch, Product, Wishlist, Cart, Customer, PurchaseHistory

admin.site.register(UserRadioWatch)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(PurchaseHistory)


