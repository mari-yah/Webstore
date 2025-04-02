from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, signup_view, update_cart_quantity
from .views import remove_from_cart
from .views import bargain_total

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('bargain_total/<int:customer_id>/', bargain_total, name='bargain_total'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),  # Correctly links to cart view
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),  # Correctly links to cart addition
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # Cart removal
    path('clear-cart/', views.clear_cart, name='clear_cart'),  # Clear cart URL

    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),  # Wishlist view
    path('add-to-wishlist/<str:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # Add to wishlist



    # Product-related URLs
    path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('brand/<str:brand_name>/', views.product_by_brand, name='product_by_brand'),
    path('type/<str:type>/', views.product_by_type, name='product_by_type'),

    # Bargain URLs
    #path('bargain_total/<int:customer_id>/<str:product_id>/', views.bargain_total, name='bargain_total'),
    path('update-cart-quantity/', update_cart_quantity, name='update_cart_quantity'),

    
]


# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)