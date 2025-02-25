from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import bargain_product

urlpatterns = [
    path('', views.home_view, name='home'),  # Home page
    path('home/', views.home_view, name='home'),  # Home page
    path('signup/', views.signup_view, name='signup'),  # Signup page
    path('login/', views.login_view, name='login'),  # Login page

    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # ✅ Changed from <int> to <str>
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    path('wishlist/', views.wishlist_view, name='wishlist'), 

    path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),  # ✅ Changed from <int> to <str>
    path('brand/<str:brand_name>/', views.product_by_brand, name='product_by_brand'),
    path('type/<str:type>/', views.product_by_type, name='product_by_type'),
    path('bargain/<int:customer_id>/<int:product_id>/', bargain_product, name='bargain_product'),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
