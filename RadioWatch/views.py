from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import User,Product, Bargain, Customer
from decimal import Decimal




# View for Home Page
@login_required
def home_view(request):

    template = loader.get_template('home.html')  # Load the home template
    context = {}  # Define the context (can be updated with dynamic data later)
    return HttpResponse(template.render(context, request))


# View for Signup
def signup_view(request):
    """
    Handle user signup.
    - Display a form for user registration.
    - Validate and save user data on POST request.
    - Redirect to login page on successful registration.
    """
    if request.method == 'POST':
        form = UserSignupForm(request.POST)  # Bind data to the form
        if form.is_valid():
            user = form.save()  # Save the user (password will be hashed)
            
            # Authenticate and log the user in after successful signup
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)  # Log the user in

                # Check if the user is authenticated and redirect to home
                if request.user.is_authenticated:
                    return redirect('home')  # Redirect to home page after login
                else:
                    return redirect('login')  # Redirect to login page if something goes wrong

            else:
                return render(request, 'loginpage.html', {'form': form, 'error': 'Authentication failed.'})

    else:
        form = UserSignupForm()  # Instantiate an empty form

    return render(request, 'loginpage.html', {'form': form, 'is_signup': True})

# View for Login
def login_view(request):
    """
    Handle user login.
    - Authenticate user with provided credentials.
    - Redirect to home page on successful login.
    - Display error message on invalid credentials.
    """
    if request.method == 'POST':
        username = request.POST.get('username_or_email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log the user in

            # Check if the user is authenticated and redirect to home
            if request.user.is_authenticated:
                return redirect('home')  # Redirect to home page after login
            else:
                return redirect('login')  # Redirect to login page if something goes wrong
        else:
            # Render login page with error message
            return render(request, 'loginpage.html', {'error': 'Invalid credentials'})

    return render(request, 'loginpage.html', {'is_signup': False})

def cart_view(request):
    # logic for cart view
    return render(request, 'cart.html')  # Adjust the template name as needed

def wishlist_view(request):
    return render(request, 'wishlist.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# View for products by category (e.g., Analog, Digital, etc.)
def product_by_category(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'product_category.html', {'products': products, 'category': category})

# View for products by type (e.g., Analog, Digital, etc.)
def product_by_type(request, product_type):
    products = Product.objects.filter(type=product_type)
    return render(request, 'product_type.html', {'products': products, 'product_type': product_type})

def product_list(request):
    products = Product.objects.all()  # Ensure this fetches correct data
    return render(request, "product_list.html", {"products": products})

# View for products by brand
def product_by_brand(request, brand_name):
    products = Product.objects.filter(brand_name=brand_name)
    return render(request, 'product_brand.html', {'products': products, 'brand_name': brand_name})


def bargain_product(request, customer_id, product_id):
    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    # Check if a bargain exists or create a new one
    bargain, created = Bargain.objects.get_or_create(customer=customer, product=product)

    # Calculate discount based on purchase history
    actual_price = product.price
    discount = 0  # Default discount is 0%

    if customer.total_purchases > 5:
        discount = max(discount, 10)  # 10% discount for frequent buyers

    if customer.total_spent >= 20000:
        discount = max(discount, 20)  # 20% discount for high-spenders

    if customer.total_purchases == 0:  # First-time buyer
        discount = max(discount, 5)  # 5% discount for new users

    # Calculate the final price
    final_price = round(Decimal(actual_price) * Decimal(1 - (discount) / 100), 2)
    
    
    # Save final price to the bargain model
    Bargain.final_price= final_price
    bargain.save()

    return render(request, 'bargain.html', {'bargain': bargain, 'discount': discount})
