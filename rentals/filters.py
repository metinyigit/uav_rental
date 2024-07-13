import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    # Ürün filtreleme kriterleri
    brand = django_filters.CharFilter(lookup_expr='icontains', label='Marka')
    model = django_filters.CharFilter(lookup_expr='icontains', label='Model')
    weight = django_filters.NumberFilter(lookup_expr='exact', label='Ağırlık')  # Sayısal arama için
    category = django_filters.CharFilter(lookup_expr='icontains', label='Kategori')
    daily_rent_price = django_filters.NumberFilter(lookup_expr='exact', label='Günlük Kira Parası')  # Sayısal arama için
    # Kiralama filtreleme kriterleri
    rental_buyer = django_filters.CharFilter(field_name='rental__buyer__username', lookup_expr='icontains', label='Kiralanan Kişi')
    rental_start_date = django_filters.DateFilter(field_name='rental__start_date', lookup_expr='gte', label='Kiralama Başlangıç Tarihi')
    rental_end_date = django_filters.DateFilter(field_name='rental__end_date', lookup_expr='lte', label='Kiralama Bitiş Tarihi')
    class Meta:
        model = Product
        fields = ['brand', 'model', 'weight', 'category', 'daily_rent_price']
