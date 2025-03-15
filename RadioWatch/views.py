from django import forms
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth import authenticate, login
#from django.contrib.auth.decorators import login_required
from django.contrib import messages

from RadioWatch.forms import UserRadioWatchForm
from .models import UserRadioWatch, Product, Bargain, Customer
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password


# Home Page
#@login_required
def home_view(request):
    return render(request, 'home.html')

#signup view
def signup_view(request):
    if request.method == "POST":
        form = UserRadioWatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # Redirect to login page after signup
    else:
        form = UserRadioWatchForm()
    
    return render(request, "loginpage.html", {"form": form, "is_signup": True})

#login view
class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

def login_view(request):
    error = None
    form = LoginForm()  # Create an instance of the login form

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data["username_or_email"]
            password = form.cleaned_data["password"]

            try:
                user = UserRadioWatch.objects.get(user_name=username_or_email) or UserRadioWatch.objects.get(email_id=username_or_email)
                
                if user.password == password:  # Check password (no hashing)
                    request.session["user_id"] = user.user_id  # Create session
                    return redirect("home")  # Redirect after login
                else:
                    error = "Invalid credentials"
            except UserRadioWatch.DoesNotExist:
                error = "User not found"

    return render(request, "loginpage.html", {"login_form": form, "is_signup": False, "error": error})

# Logout View
def logout_view(request):
    request.session.flush()  # Clear session data
    return redirect('login')
# Cart View
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Check if user has an associated Customer profile
    user_id = request.session.get('user_id')
    customer = Customer.objects.filter(user_id=user_id).first()
    
    # Ensure customer_id is fetched correctly
    customer_id = customer.customer_id if customer else None

    for product_id, quantity in cart.items():
        if not product_id:
            continue  # Skip invalid entries

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
        'customer_id': customer_id  # Ensure this is a valid integer
    })

# Add to Cart
def add_to_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        messages.success(request, "Item added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Remove from Cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Removed from cart!")
    return redirect('cart')

# Clear Cart
def clear_cart(request):
    request.session['cart'] = {}
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

def bargain_product(request, customer_id, product_id):
    # Fix: Use `user_id` instead of `id`
    
    customer = get_object_or_404(Customer, customer_id=customer_id)
    product = get_object_or_404(Product, product_id=product_id)  # Fix product lookup
    print(product)
    # Retrieve or create bargain instance
    bargain, created = Bargain.objects.get_or_create(customer=customer, product=product)

    actual_price = product.price  # Fetch the product's actual price
    discount = 0  # Initialize discount

    # Apply discount logic based on customer history
    if customer.total_purchases == 0:
        discount = 5  # First-time customer gets 5%
    elif customer.total_purchases > 5:
        discount = 10  # More than 5 purchases → 10%
    if customer.total_spent >= 200000:  # Fix: Threshold should be ₹2,00,000
        discount = min(discount, 20)  # High-value customer gets 20%

    # Calculate final price after discount
    final_price = round(Decimal(actual_price) * Decimal(1 - discount / 100), 2)
    
    # Save final price in Bargain model
    bargain.final_price = final_price
    bargain.save()

    # Render bargain summary on cart page
    return render(request, 'bargain.html', {
        'bargain': bargain,
        'discount': discount,
        'actual_price': actual_price,
        'final_price': final_price,
        'customer_id': customer_id,  # Helpful for debugging
    })


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
