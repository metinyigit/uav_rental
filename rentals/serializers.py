from rest_framework import serializers
from .models import User, Product, Rental

class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcı modelini JSON formatına dönüştürmek için kullanılan serializer.
    Kullanıcı ID'si, kullanıcı adı, e-posta ve rol bilgilerini içerir.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ProductSerializer(serializers.ModelSerializer):
    """
    Ürün modelini JSON formatına dönüştürmek için kullanılan serializer.
    Ürün ID'si, satıcı bilgisi, günlük kira bedeli, marka, model, ağırlık ve kategori bilgilerini içerir.
    """
    class Meta:
        model = Product
        fields = ['id', 'seller', 'daily_rent_price', 'brand', 'model', 'weight', 'category']

class RentalSerializer(serializers.ModelSerializer):
    """
    Kiralama modelini JSON formatına dönüştürmek için kullanılan serializer.
    Kiralama ID'si, alıcı, ürün, başlangıç ve bitiş tarihi bilgilerini içerir.
    """
    class Meta:
        model = Rental
        fields = ['id', 'buyer', 'product', 'start_date', 'end_date']
