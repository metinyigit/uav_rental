from django.urls import path, include
from .views import (
    signup_view, login_view, seller_dashboard, seller_dashboard_ajax, 
    buyer_dashboard, buyer_dashboard_ajax, index_view, 
    add_product, edit_product, delete_product, 
    rent_product, update_rental, delete_rental
)
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProductViewSet, RentalViewSet

# API view setlerini yönetmek için bir DefaultRouter oluşturuyoruz.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'rentals', RentalViewSet)

urlpatterns = [
    # Kullanıcı kayıt sayfasına yönlendirme
    path('signup/', signup_view, name='signup'),
    
    # Kullanıcı giriş sayfasına yönlendirme
    path('login/', login_view, name='login'),
    
    # Kullanıcı çıkış sayfasına yönlendirme
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Satıcı kontrol paneline yönlendirme
    path('seller_dashboard/', seller_dashboard, name='seller_dashboard'),
    
    # Alıcı kontrol paneline yönlendirme
    path('buyer_dashboard/', buyer_dashboard, name='buyer_dashboard'),
    
    # Ürün kiralama işlemi için yönlendirme
    path('rent_product/<int:product_id>/', rent_product, name='rent_product'),
    
    # Kiralamayı güncelleme işlemi için yönlendirme
    path('update_rental/<int:rental_id>/', update_rental, name='update_rental'),
    
    # Kiralamayı silme işlemi için yönlendirme
    path('delete_rental/<int:rental_id>/', delete_rental, name='delete_rental'),
    
    # Yeni ürün ekleme sayfasına yönlendirme
    path('add_product/', add_product, name='add_product'),
    
    # Ürünü düzenleme sayfasına yönlendirme
    path('edit_product/<int:pk>/', edit_product, name='edit_product'),
    
    # Ürünü silme sayfasına yönlendirme
    path('delete_product/<int:pk>/', delete_product, name='delete_product'),
    
    # Alıcı kontrol paneli için AJAX isteklerine yanıt verecek yol
    path('buyer_dashboard/ajax/', buyer_dashboard_ajax, name='buyer_dashboard_ajax'),
    
    # Satıcı kontrol paneli için AJAX isteklerine yanıt verecek yol
    path('seller_dashboard/ajax/', seller_dashboard_ajax, name='seller_dashboard_ajax'),
    
    # Ana sayfaya yönlendirme
    path('', index_view, name='index'),  # Index sayfası
    
    # API yönlendirmeleri
    path('api/', include(router.urls)),  # API yönlendirmeleri
]
