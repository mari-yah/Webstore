from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Product, Bargain, Customer
from decimal import Decimal

# Home Page
@login_required
def home_view(request):
    template = loader.get_template('home.html')  
    context = {}  
    return HttpResponse(template.render(context, request))

# Signup View
def signup_view(request):
    from .forms import UserSignupForm
    if request.method == 'POST':
        form = UserSignupForm(request.POST)  
        if form.is_valid():
            user = form.save()  
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)  
                return redirect('home')  
            else:
                return render(request, 'loginpage.html', {'form': form, 'error': 'Authentication failed.'})
    else:
        form = UserSignupForm()

    return render(request, 'loginpage.html', {'form': form, 'is_signup': True})

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username_or_email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  
            return redirect('home')  
        else:
            return render(request, 'loginpage.html', {'error': 'Invalid credentials'})
    return render(request, 'loginpage.html', {'is_signup': False})

# Cart View (Updated)
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        if not product_id:
            continue
        product = get_object_or_404(Product, product_id=product_id)  # Fixed id issue
        cart_items.append({
            'product_id': product.product_id,
            'name': product.product_name,
            'price': product.price,
            'quantity': quantity,
            'image': product.image.url if product.image else '',
        })
        total_price += product.price * quantity

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Add to Cart View (Updated)
from django.shortcuts import redirect
from django.contrib import messages

def add_to_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
        messages.success(request, "Item added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Remove from Cart View (Updated)
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id and product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Removed from cart!")
    else:
        messages.error(request, "Invalid product.")
    return redirect('cart')

# Clear Cart View
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

# Wishlist View (Updated)
def wishlist_view(request):
    return render(request, 'wishlist.html')

# Product Detail View (Updated)
def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)  # Fixed id issue
    return render(request, 'product_detail.html', {'product': product})

# View for Products by Brand (Updated)
def product_by_brand(request, brand_name):
    products = Product.objects.filter(brand_name=brand_name)
    return render(request, 'product_brand.html', {'products': products, 'brand_name': brand_name})

# View for Products by type (Updated)
def product_by_type(request, type):
    products = Product.objects.filter(type=type)
    return render(request, 'product_type.html', {'products': products, 'type': type})

# Product List View
def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

# Bargain Product View (Updated)
def bargain_product(request, customer_id, product_id):
    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, product_id=product_id)  # Fixed id issue

    bargain, created = Bargain.objects.get_or_create(customer=customer, product=product)
    actual_price = product.price
    discount = 0  

    if customer.total_purchases > 5:
        discount = max(discount, 10)
    if customer.total_spent >= 20000:
        discount = max(discount, 20)
    if customer.total_purchases == 0:
        discount = max(discount, 5)

    final_price = round(Decimal(actual_price) * Decimal(1 - (discount) / 100), 2)
    
    bargain.final_price = final_price
    bargain.save()

    return render(request, 'bargain.html', {'bargain': bargain, 'discount': discount})
