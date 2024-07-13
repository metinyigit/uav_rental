from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Product, Rental

# Django'nun User ve Group Modellerini Admin Panelinden Kaldır
admin.site.unregister(Group)
# User Model için Admin Konfigürasyonu
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Kullanıcı (User) modelinin admin panelindeki görünümünü düzenler.
    """
    list_display = ('username', 'email', 'role')  # Gösterilecek alanlar
    search_fields = ('username', 'email')  # Arama yapılacak alanlar
    list_filter = ('role',)  # Filtreleme seçenekleri

# Product Model için Admin Konfigürasyonu
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Ürün (Product) modelinin admin panelindeki görünümünü düzenler.
    """
    list_display = ('brand', 'model', 'weight', 'category', 'daily_rent_price', 'seller')
    search_fields = ('brand', 'model', 'category', 'seller__username')  # Arama yapılacak alanlar
    list_filter = ('category', 'seller')  # Filtreleme seçenekleri
    ordering = ('-daily_rent_price',)  # Varsayılan sıralama

# Rental Model için Admin Konfigürasyonu
@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    """
    Kiralama (Rental) modelinin admin panelindeki görünümünü düzenler.
    """
    list_display = ('buyer', 'product', 'start_date', 'end_date')
    search_fields = ('buyer__username', 'product__model')  # Arama yapılacak alanlar
    list_filter = ('start_date', 'end_date', 'product')  # Filtreleme seçenekleri
    date_hierarchy = 'start_date'  # Tarih hiyerarşisi için kullanılır
