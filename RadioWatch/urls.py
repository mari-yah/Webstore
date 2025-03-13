from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import update_cart_quantity

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<str:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    # Product-related URLs
    path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('brand/<str:brand_name>/', views.product_by_brand, name='product_by_brand'),
    path('type/<str:type>/', views.product_by_type, name='product_by_type'),

    # Bargain URLs
    path('home/bargain/<int:customer_id>/<str:product_id>/', views.bargain_product, name='bargain_product'),
    path('update-cart-quantity/', update_cart_quantity, name='update_cart_quantity'),

    
]


# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
