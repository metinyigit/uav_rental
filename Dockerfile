FROM python:3.11.5

# Çalışma dizinini oluşturma ve ayarlama
WORKDIR /app

# Gerekli paketleri yükleme
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu konteynıra kopyalama
COPY . .


# Django uygulamasını çalıştırma
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Konteynırın dışarıya 8000 portunu açması
EXPOSE 8000
