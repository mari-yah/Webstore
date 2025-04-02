from django import forms
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from RadioWatch.forms import UserRadioWatchForm
from .models import Cart,UserRadioWatch, Product, Bargain, Customer
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
import logging  
import random
from django.db.models import Sum


# Home Page
#@login_required
def home_view(request):
    return render(request, 'home.html')

#signup view
from django.contrib.auth.models import User

def signup_view(request):
    if request.method == "POST":
        form = UserRadioWatchForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            
            # Create a corresponding Customer entry
            Customer.objects.create(
                user=user,
                total_purchases=0,  # Default values
                total_spent=0
            )
            
            return redirect("login")  # Redirect to login page after signup
    else:
        form = UserRadioWatchForm()
    
    return render(request, "loginpage.html", {"form": form, "is_signup": True})



# Logout View
# Updated login view
import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    error = None
    if request.method == 'POST':
        # Extract 'username' and 'password' from POST data
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate user using username and password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your home URL name
        else:
            error = "Invalid username or password."
    # For GET requests, instantiate a default form instance.
    form = AuthenticationForm()
    return render(request, 'loginpage.html', {'login_form': form, 'error': error})
    
# Updated Logout View
def logout_view(request):
    request.session.flush()  # Clear session data (updated line)
    return redirect('login')
logger = logging.getLogger(__name__)



def cart(request):
    cart_items = []
    total_price = 0
    customer_id = None  # Default value to prevent empty string errors
    
    if request.user.is_authenticated:
        user = request.user
        user_cart = Cart.objects.filter(user=user)
        
        for item in user_cart:
            cart_items.append({
                'product_id': item.product.product_id,
                'name': item.product.product_name,
                'price': item.product.price,
                'quantity': item.quantity,
                'image': item.product.image.url if item.product.image else '',
            })
            total_price += item.product.price * item.quantity
        
        # Fix: Ensure customer_id is always an integer or None
        customer = Customer.objects.filter(user_id=user.user_id).first()
        customer_id = customer.customer_id if customer else 0  # Use 0 instead of ''
    else:
        cart = request.session.get('cart', {})
        
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, product_id=product_id)
            cart_items.append({
                'product_id': product.product_id,
                'name': product.product_name,
                'price': product.price,
                'quantity': quantity,
                'image': product.image.url if product.image else '',
            })
            total_price += product.price * quantity

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'customer_id': customer_id  # Ensure this is always valid
    })



# Add to Cart
# Updated Add to Cart
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        user = request.user
        product = get_object_or_404(Product, product_id=product_id)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
    
    messages.success(request, "Item added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

from django.shortcuts import redirect
from django.contrib import messages

def remove_from_cart(request, product_id):
    product_id = str(product_id)  # Ensure it's a string for session handling

    if request.user.is_authenticated:
        # Remove from database cart for logged-in users
        Cart.objects.filter(user=request.user, product__product_id=product_id).delete()
    else:
        # Remove from session cart for guests
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]  # Remove item
            request.session['cart'] = cart  # Save updated cart
            request.session.modified = True  # Mark session as modified
    
    messages.success(request, "Removed from cart!")
    return redirect('cart')


# Clear the entire cart
def clear_cart(request):
    if request.user.is_authenticated:
        # Delete all cart items from the database for logged-in users
        Cart.objects.filter(user=request.user).delete()
    else:
        # Clear session cart for guests
        request.session.pop('cart', None)  # Remove cart from session
        request.session.modified = True  # Mark session as modified

    messages.success(request, "Cart cleared successfully!")
    return redirect('cart')

# Wishlist View
def wishlist_view(request):
    return render(request, 'wishlist.html')

# Add to Wishlist
def add_to_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', set())
    wishlist.add(str(product_id))
    request.session['wishlist'] = list(wishlist)
    messages.success(request, "Item added to wishlist!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Product Detail View
def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# Products by Brand
def product_by_brand(request, brand_name):
    products = Product.objects.filter(brand_name=brand_name)
    return render(request, 'product_brand.html', {'products': products, 'brand_name': brand_name})

# Products by Type
def product_by_type(request, type):
    products = Product.objects.filter(type=type)
    return render(request, 'product_type.html', {'products': products, 'type': type})

# Product List
def product_list(request):
    """Displays the list of products with optional filtering by category and brand."""
    category = request.GET.get('category', 'All')
    brand = request.GET.get('brand', 'All')

    # Start with all products
    products = Product.objects.all()

    # Apply category filter if not 'All'
    if category and category != 'All':
        products = products.filter(category=category)
        print(f"Filtered by category: {category}, Products found: {products.count()}")

    # Apply brand filter if not 'All'
    if brand and brand != 'All':
        products = products.filter(brand_name=brand)
        print(f"Filtered by brand: {brand}, Products found: {products.count()}")

    context = {
        'products': products,
        'selected_category': category,
        'selected_brand': brand,
    }
    
    return render(request, 'product_list.html', context)



<<<<<<< HEAD

def bargain_total(request, user_id):  # Ensure URL and view use the same parameter name
    cart_items = Cart.objects.filter(user_id=user_id)
=======
def bargain_total(request, customer_id):
    # Get Customer instance
    customer = get_object_or_404(Customer, customer_id=customer_id)
    user = customer.user  

    # Get cart items (filter by user, not customer)
    cart_items = Cart.objects.filter(user=user)
>>>>>>> ac1a3bb45bf13160ecba24d233d4a65d72f74360

    if not cart_items.exists():
        return render(request, 'bargain.html', {'message': 'Your cart is empty.'})

<<<<<<< HEAD
    print("DEBUG: Cart Items Found ->", cart_items)  # Debugging statement

    # ✅ Ensure correct price calculation
    original_price = sum(Decimal(str(item.product.price)) * item.quantity for item in cart_items)
    discount_percentage = Decimal(random.randint(5, 20))  # Random discount (5% to 20%)
    discount_amount = (original_price * discount_percentage) / Decimal(100)
    final_price = original_price - discount_amount

    print(f"DEBUG: Original Price: {original_price}, Discount: {discount_percentage}%, Final Price: {final_price}")
=======
    # ✅ Get total price from request (if sent)
    total_price = request.GET.get('total_price')
>>>>>>> ac1a3bb45bf13160ecba24d233d4a65d72f74360

    if total_price is None:
        # ✅ Calculate total price from the cart if not provided
        total_price = cart_items.aggregate(total=Sum('product__price'))['total'] or Decimal(0)
    else:
        total_price = Decimal(total_price)  # Convert to Decimal

    # ✅ Apply discount logic
    discount = Decimal(0)

    if customer.total_purchases == 0:
        discount = Decimal(5)  # First-time customer
    elif customer.total_purchases > 5:
        discount = Decimal(10)  # Loyal customer
    if customer.total_spent >= 1000000:
        discount = max(discount, Decimal(20))  # High-value customer gets 20%

    if discount == 0:
        discount = Decimal(random.randint(5, 20))  # Random discount if no criteria met

    # ✅ Calculate final price after discount
    final_price = total_price - (total_price * discount / Decimal(100))

    # ✅ Ensure proper rounding to 2 decimal places
    context = {
<<<<<<< HEAD
        'original_price': original_price.quantize(Decimal("0.01")),  # Format to 2 decimal places
        'discount': discount_percentage,
        'final_price': final_price.quantize(Decimal("0.01")),  # Format to 2 decimal places
=======
        'total_price': total_price.quantize(Decimal("0.01")),
        'discount': discount,
        'final_price': final_price.quantize(Decimal("0.01")),
        'customer_id': customer_id,
>>>>>>> ac1a3bb45bf13160ecba24d233d4a65d72f74360
    }

    return render(request, 'bargain.html', context)

#quantity update in cart
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_cart_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = str(data.get('product_id'))
            quantity = int(data.get('quantity'))

            cart = request.session.get('cart', {})  # Ensure cart exists

            if quantity < 1:
                cart.pop(product_id, None)  # Remove item if quantity < 1
            else:
                cart[product_id] = quantity

            request.session['cart'] = cart  # Save updated cart

            return JsonResponse({'success': True, 'cart': cart})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
