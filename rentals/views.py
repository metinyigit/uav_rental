from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, ProductForm, RentalForm
from .models import Product, Rental,User
from .filters import ProductFilter
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .serializers import UserSerializer, ProductSerializer, RentalSerializer
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse

@login_required
def buyer_dashboard(request):
    """
    Alıcı (buyer) için kontrol paneli görüntüler.
    Kullanıcının rolü 'buyer' değilse, satıcı (seller) kontrol paneline yönlendirir.
    """
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    return render(request, 'buyer/buyer_dashboard.html')
@login_required
def buyer_dashboard_ajax(request): 
    """
    Alıcı kontrol paneli için AJAX destekli ürün listeleme ve filtreleme sağlar.
    Sayfalama, sıralama ve arama işlemleri desteklenir.
    """
    products = Product.objects.all()
    # Kullanıcının kiraladığı ürünler ve diğer kiralanan ürünleri al
    rentals = Rental.objects.filter(buyer=request.user)
    rental_product_ids = rentals.values_list('product_id', flat=True)
    rented_product_ids = Rental.objects.exclude(buyer=request.user).values_list('product_id', flat=True).distinct()

    # Ürün filtreleme
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs
    
    # Sayfalama parametrelerini al
    draw = int(request.GET.get('draw', '0'))
    start = int(request.GET.get('start', '0'))
    length = int(request.GET.get('length', '10'))
    
    # Arama işlemleri
    search_value = request.GET.get('search[value]', '')
    

    if search_value:
        filtered_products = filtered_products.filter(
            Q(brand__icontains=search_value) |
            Q(model__icontains=search_value) |
            Q(weight__icontains=search_value) |
            Q(category__icontains=search_value) |
            Q(daily_rent_price__icontains=search_value) |
            Q(seller__username__icontains=search_value)
        )

    # Sıralama işlemleri
    order_columns = ['brand', 'model', 'weight', 'category', 'daily_rent_price', 'seller.username']
    
    order_column_index = int(request.GET.get('order[0][column]', '0'))
    order_direction = request.GET.get('order[0][dir]', 'asc')
    if order_column_index < len(order_columns):
        order_by = order_columns[order_column_index]
        if order_direction == 'desc':
            order_by = '-' + order_by
        filtered_products = filtered_products.order_by(order_by)
    paginator = Paginator(filtered_products, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)
    products_page = page.object_list

    data = {
        'draw': draw,
        'recordsTotal': paginator.count,
        'recordsFiltered': filtered_products.count(),
        'data': [
            [
                product.brand,
                product.model,
                product.weight,
                product.category,
                product.daily_rent_price,
                product.seller.username,
                get_format_actions(product, rentals, rental_product_ids, rented_product_ids)
            ]
            for product in products_page
        ]
    }

    return JsonResponse(data)
def get_format_actions(product, rentals, rental_product_ids, rented_product_ids):
    """
    Ürün için uygun eylem butonlarını oluşturur.
    Kiralanmışsa, kiralama bilgilerini gösterir ve güncelleme/silme butonları ekler.
    Kiralanmamışsa, kiralama butonu ekler.
    """
    rental_info = ''
    
    if product.id in rental_product_ids:
        for rental in rentals:
            if rental.product_id == product.id:
                start_date = rental.start_date.strftime('%d-%m-%Y')
                end_date = rental.end_date.strftime('%d-%m-%Y')
                days = (rental.end_date - rental.start_date).days
                total_price = days * product.daily_rent_price
                rental_info = (
                    f'<div class="rental-info" data-start-date="{start_date}" data-end-date="{end_date}">'
                    f'<span class="days">{days}</span> gün, <span class="total-price">{total_price}</span> TL'
                    '</div>'
                )
                rental_info += (
                    f'<a href="{reverse("update_rental", args=[rental.id])}" class="btn btn-warning btn-sm">Güncelle</a>'
                    f'<a href="{reverse("delete_rental", args=[rental.id])}" class="btn btn-danger btn-sm">Sil</a>'
                )
                break
    elif product.id not in rented_product_ids:
        rental_info = f'<a href="{reverse("rent_product", args=[product.id])}" class="btn btn-primary btn-sm">Kirala</a>'
    else:
        rental_info = '<span>Zaten Kiralandı</span>'
    
    return rental_info
@login_required
def rent_product(request, product_id):
    """
    Bir ürünü kiralar. Kiralama formu ile işlem yapar.
    AJAX isteği ile formu dönerse, form HTML'ini ve günlük kira bedelini döner.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.buyer = request.user
            rental.product = product
            rental.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'}, status=200)
            return redirect('buyer_dashboard')
    else:
        form = RentalForm()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'form': form.as_p(), 'rental': rental.daily_rent_price}, status=200)
    return render(request, 'buyer/rent_product.html', {'form': form, 'product': product})

@login_required
def update_rental(request, rental_id):
    #Kiralamayı günceller. AJAX isteği ile formu dönerse, form HTML'ini ve günlük kira bedelini döner.
    rental = get_object_or_404(Rental, id=rental_id)
    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'}, status=200)
            return redirect('buyer_dashboard')
    else:
        form = RentalForm(instance=rental)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'form': form.as_p(), 'rental': rental.daily_rent_price}, status=200)
    
    return render(request, 'buyer/update_rental.html', {'form': form, 'rental': rental})

@login_required
def delete_rental(request, rental_id):
    #Kiralamayı siler ve alıcı kontrol paneline yönlendirir.
    rental = get_object_or_404(Rental, id=rental_id)
    rental.delete()
    return redirect('buyer_dashboard')

@login_required
def seller_dashboard(request):
    """
    Satıcı (seller) için kontrol paneli görüntüler.
    Kullanıcının rolü 'seller' değilse, alıcı (buyer) kontrol paneline yönlendirir.
    """
    if request.user.role != 'seller':
        return redirect('buyer_dashboard')
    return render(request, 'seller/seller_dashboard.html')

@login_required
def seller_dashboard_ajax(request):
    """
    Satıcı kontrol paneli için AJAX destekli ürün listeleme ve filtreleme sağlar.
    Sayfalama, sıralama ve arama işlemleri desteklenir.
    """
   
    products = Product.objects.filter(seller=request.user)
    # Ürün filtreleme
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs

    # Sayfalama parametrelerini al
    draw = int(request.GET.get('draw', '0'))
    start = int(request.GET.get('start', '0'))
    length = int(request.GET.get('length', '10'))
    
    # Arama işlemleri
    search_value = request.GET.get('search[value]', '')

    if search_value:
        filtered_products = filtered_products.filter(
            Q(brand__icontains=search_value) |
            Q(model__icontains=search_value) |
            Q(weight__icontains=search_value) |
            Q(category__icontains=search_value) |
            Q(daily_rent_price__icontains=search_value) |
            Q(rental__buyer__username__icontains=search_value)
        ).distinct()
    
    # Sıralama işlemleri
    order_column_index = int(request.GET.get('order[0][column]', '0'))
    order_direction = request.GET.get('order[0][dir]', 'asc')

    order_columns = ['brand', 'model', 'weight', 'category', 'daily_rent_price', 'rental.buyer.username']
    
    if order_column_index < len(order_columns):
        order_by = order_columns[order_column_index]
        if order_direction == 'desc':
            order_by = '-' + order_by
        filtered_products = filtered_products.order_by(order_by)
    
    # Sayfalama işlemleri
    paginator = Paginator(filtered_products, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)
    products_page = page.object_list

    data = {
        'draw': draw,
        'recordsTotal': paginator.count,
        'recordsFiltered': filtered_products.count(),
        'data': [
            [
                product.brand,
                product.model,
                product.weight,
                product.category,
                product.daily_rent_price,
                """
                Ürün için kiralama bilgilerini oluşturur.
                Ürün kiralandıysa, kiralama bilgilerini gösterir ve güncelleme/silme butonları ekler.
                """
                ', '.join([rental.buyer.username or '-' for rental in product.rental_set.all()]) or '-',
                '<br>'.join([
                    f"{rental.start_date.strftime('%d.%m.%Y')} - {rental.end_date.strftime('%d.%m.%Y')}"
                    for rental in product.rental_set.all()
                ]) or '-',
                f'<a href="{reverse("edit_product", args=[product.pk])}" class="btn btn-warning btn-sm">Düzenle</a> '
                f'<a href="{reverse("delete_product", args=[product.pk])}" class="btn btn-danger btn-sm">Sil</a>'
            ]
            for product in products_page
        ]
    }

    return JsonResponse(data)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'seller/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller/edit_product.html', {'form': form})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('seller_dashboard')
    return render(request, 'seller/delete_product.html', {'product': product})

def index_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'seller':
            return redirect('seller_dashboard')
        else:
            return redirect('buyer_dashboard')
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('buyer_dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'user/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'seller':
            return redirect('seller_dashboard')
        else:
            return redirect('buyer_dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('buyer_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Kullanıcı adı veya şifre yanlış!'})
    
    return render(request, 'user/login.html')

# API ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
