from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Kullanıcı rolleri için seçimler
    ROLE_CHOICES = [
        ('seller', 'Satıcı'),
        ('buyer', 'Alıcı'),
    ]
    # Kullanıcı rolü (satıcı veya alıcı)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Product(models.Model):
    # Ürünlerin satıcısını belirtir (User modeli ile ilişkilendirir)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    # Günlük kira bedeli
    daily_rent_price = models.DecimalField(max_digits=10, decimal_places=0)
    # Marka bilgisi
    brand = models.CharField(max_length=100)
    # Model bilgisi
    model = models.CharField(max_length=100)
    # Ağırlık bilgisi
    weight = models.CharField(max_length=100)
    # Kategori bilgisi
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand} {self.model}"

class Rental(models.Model):
    # Kiralayan kullanıcı (alıcı)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    # Kiralanan ürün
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Kiralama başlangıç tarihi
    start_date = models.DateField()
    # Kiralama bitiş tarihi
    end_date = models.DateField()

    def __str__(self):
        return f"Rental of {self.product} by {self.buyer} from {self.start_date} to {self.end_date}"
