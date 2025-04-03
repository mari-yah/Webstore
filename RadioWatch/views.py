from django import forms
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from RadioWatch.forms import UserRadioWatchForm
from .models import Cart,UserRadioWatch, Product, Customer, PurchaseHistory
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
import logging  
import random
from django.db.models import Sum
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from django.utils.timezone import now




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



from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
from decimal import Decimal
import random
from .models import Customer, Cart, PurchaseHistory

def bargain_total(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    user = customer.user  

    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return render(request, 'bargain.html', {'message': 'Your cart is empty.'})

    # ✅ Calculate total price of the cart
    total_price = cart_items.aggregate(total=Sum('product__price'))['total'] or Decimal(0)

    # ✅ Apply discount logic based on past purchases
    purchase_count = PurchaseHistory.objects.filter(customer=customer).count()
    discount_percentage = Decimal(0)

    if total_price > 1000000:
        discount_percentage = Decimal(20)
    else:
        if purchase_count == 0:
            discount_percentage = Decimal(10)
        elif purchase_count == 1:
            discount_percentage = Decimal(0)
        elif purchase_count == 4:
            discount_percentage = Decimal(15)
        elif purchase_count in [2, 3, 5, 6, 7, 8, 9]:
            discount_percentage = Decimal(5) if random.choice([True, False]) else Decimal(0)

    # ✅ Calculate final price after discount
    discount_amount = (total_price * discount_percentage) / 100
    final_price = total_price - discount_amount

    # ✅ Store discount details in session (cart remains unchanged)
    request.session['bargain_discount'] = {
        'total_price': str(total_price),
        'discount_percentage': str(discount_percentage),
        'final_price': str(final_price)
    }

    # ✅ Ensure proper rounding
    context = {
        'total_price': total_price.quantize(Decimal("0.01")),
        'discount': discount_percentage if discount_percentage > 0 else "No Discount",
        'final_price': final_price.quantize(Decimal("0.01")),
        'customer_id': customer_id,
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



    #checkout view


from django.shortcuts import render, redirect
from django.http import HttpResponse
from decimal import Decimal
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Cart, PurchaseHistory, Customer

def checkout(request):
    user = request.user
    try:
        customer = Customer.objects.get(user=user)  # ✅ Fetch Customer profile
    except Customer.DoesNotExist:
        return HttpResponse("Customer profile not found.", content_type="text/plain")

    cart_items = Cart.objects.filter(user=user)  # ✅ Fetch Cart items
    if not cart_items.exists():
        return HttpResponse("Your cart is empty.", content_type="text/plain")

    purchase_time = datetime.now()
    purchase_records = []

    total_cart_price = Decimal(0)
    total_cart_discount = Decimal(0)
    final_cart_price = Decimal(0)

    # ✅ Retrieve Bargain Discount from Session (if available)
    bargain_discount = request.session.get("bargain_discount", None)
    if bargain_discount:
        total_price = Decimal(bargain_discount["total_price"])
        discount_percentage = Decimal(bargain_discount["discount_percentage"])
        final_price = Decimal(bargain_discount["final_price"])
    else:
        total_price = cart_items.aggregate(total=Sum('product__price'))['total'] or Decimal(0)
        discount_percentage = Decimal(0)
        final_price = total_price

    for item in cart_items:
        item_total = item.product.price * item.quantity
        discount_amount = (item_total * discount_percentage) / 100
        item_final_price = item_total - discount_amount

        # ✅ Store the purchase record
        purchase = PurchaseHistory.objects.create(
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            purchase_price=item.product.price,
            total_price=item_total,
            discount_percentage=discount_percentage,
            final_price=item_final_price
        )
        purchase_records.append(purchase)

        # ✅ Update Totals for Invoice
        total_cart_price += item_total
        total_cart_discount += discount_amount
        final_cart_price += item_final_price

    # ✅ Update Customer Purchase History
    customer.total_purchases += cart_items.count()
    customer.total_spent += final_cart_price
    customer.save()

    # ✅ Clear Cart After Checkout
    cart_items.delete()
    request.session.pop("bargain_discount", None)  # Remove bargain discount after checkout

    # ✅ Generate PDF Invoice
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    y_position = 750  # Start position for text

    # **Header Information**
    pdf.drawString(50, y_position, f"Purchase ID: {purchase_records[0].purchase_id}")
    pdf.drawString(300, y_position, f"Date: {purchase_time.strftime('%Y-%m-%d')}")
    pdf.drawString(50, y_position - 20, f"Customer: {user.user_name}")
    y_position -= 40

    # **Table Header**
    pdf.drawString(50, y_position, "Product Name")
    pdf.drawString(250, y_position, "Price")
    pdf.drawString(350, y_position, "Quantity")
    pdf.drawString(450, y_position, "Subtotal")
    y_position -= 20

    for item in purchase_records:
        pdf.drawString(50, y_position, item.product.product_name)
        pdf.drawString(250, y_position, f"{item.purchase_price:.2f}")
        pdf.drawString(350, y_position, str(item.quantity))
        pdf.drawString(450, y_position, f"{item.total_price:.2f}")
        y_position -= 20

    # **Subtotal & Discount**
    y_position -= 20
    pdf.drawString(50, y_position, f"Subtotal: {total_cart_price:.2f}")
    pdf.drawString(50, y_position - 20, f"Discount: {total_cart_discount:.2f}")
    pdf.drawString(50, y_position - 40, f"Final Price: {final_cart_price:.2f}")

    # **Thank You Message**
    pdf.drawString(50, y_position - 80, "Thank you for shopping with us!")

    pdf.save()
    return response
