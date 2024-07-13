from django import forms
from .models import User, Product, Rental
from datetime import date

class ProductForm(forms.ModelForm):
    """
    Ürün eklemek veya güncellemek için kullanılan form.
    Sadece ürün bilgilerini içerir: günlük kira bedeli, marka, model, ağırlık, kategori.
    """
    class Meta:
        model = Product
        fields = ['brand', 'model', 'weight', 'category','daily_rent_price']
    
    
    def __init__(self, *args, **kwargs):
        """
        Form alanları için yardım metinlerini kaldırır.
        """
        
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Placeholder metinleri ekler
        self.fields['brand'].widget.attrs.update({
            'class': 'form-group',
            'placeholder': 'Marka'
        })
        self.fields['model'].widget.attrs.update({
            'class': 'form-group',
            'placeholder': 'Model'
        })
        self.fields['weight'].widget.attrs.update({
            'class': 'form-group',
            'placeholder': 'Ağırlık'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-group',
            'placeholder': 'Kategori'
        })
        self.fields['daily_rent_price'].widget.attrs.update({
            'class': 'form-group',
            'placeholder': 'Günlük Kira'
        })
        
        # Label'ları kaldırır
        for field in self.fields.values():
            field.widget.attrs['aria-label'] = field.label
            field.label = ''

class SignUpForm(forms.ModelForm):
    """
    Kullanıcı kaydı oluşturmak için kullanılan form.
    Kullanıcı adı, e-posta, şifre ve rol içerir.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        widgets = {
            'password': forms.PasswordInput(),  # Şifre alanı için özel widget
        }
        error_messages = {
            'username': {
                'required': "Kullanıcı adı zorunludur.",
                'max_length': "Kullanıcı adı 150 karakterden daha kısa olmalıdır.",
                'invalid': "Geçersiz kullanıcı adı.",
            },
            'email': {
                'required': "E-posta zorunludur.",
                'invalid': "Geçersiz e-posta adresi.",
            },
            'role': {
                'required': "Bir rol seçmelisiniz.",
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Form alanları için yardım metinlerini kaldırır.
        """
        
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        # Placeholder metinleri ekler
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Kullanıcı Adı'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'E-posta'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Şifre'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Rol'
        })
        self.fields['username'].help_text = None
        self.fields['email'].help_text = None
        self.fields['password'].help_text = None
        self.fields['role'].help_text = None
        
        # Label'ları kaldırır
        for field in self.fields.values():
            field.widget.attrs['aria-label'] = field.label
            field.label = ''

    def save(self, commit=True):
        """
        Kullanıcıyı kaydeder ve şifreyi şifreler.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class RentalForm(forms.ModelForm):
    """
    Kiralama formu. Başlangıç ve bitiş tarihi içerir.
    """
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),  # Tarih seçici widget
            'end_date': forms.DateInput(attrs={'type': 'date'}),  # Tarih seçici widget
        }

    def clean(self):
        """
        Başlangıç ve bitiş tarihlerini doğrular.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        today = date.today()
        
        # Başlangıç tarihinin bugünden eski olmaması gerektiğini kontrol eder
        if start_date and start_date < today:
            self.add_error('start_date', 'Başlangıç tarihi bugünden geçmiş olamaz.')
        
        # Bitiş tarihinin başlangıç tarihi ile aynı olmaması gerektiğini kontrol eder
        if start_date and end_date and start_date == end_date:
            self.add_error('end_date', 'Bitiş tarihi başlangıç tarihi ile aynı olamaz.')
        
        # Bitiş tarihinin başlangıç tarihinden sonra olması gerektiğini kontrol eder
        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır.')
