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
    path('cart/', views.cart_view, name='cart'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('category/<str:category>/', views.product_by_category, name='product_by_category'),
    path('type/<str:product_type>/', views.product_by_type, name='product_by_type'),
    path('brand/<str:brand_name>/', views.product_by_brand, name='product_by_brand'),
    path('bargain/<int:customer_id>/<int:product_id>/', bargain_product, name='bargain_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


