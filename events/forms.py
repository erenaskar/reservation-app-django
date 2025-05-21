from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Event, Reservation
from django.core.exceptions import ValidationError
from decimal import Decimal

class CustomUserCreationForm(UserCreationForm):
    """
    Kullanıcı kayıt formu
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap sınıfları ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
class CustomAuthenticationForm(AuthenticationForm):
    """
    Özelleştirilmiş giriş formu
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap sınıfları ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ReservationForm(forms.ModelForm):
    """
    Rezervasyon formu
    """
    class Meta:
        model = Reservation
        fields = []  # Ekstra alan yok, sadece form doğrulama için
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.user or not self.user.is_authenticated:
            raise ValidationError(_("Rezervasyon yapabilmek için giriş yapmalısınız."))
            
        if not self.event:
            raise ValidationError(_("Geçerli bir etkinlik seçmelisiniz."))
        
        # Etkinlik kapasitesi kontrolü
        if self.event.is_full:
            raise ValidationError(_("Bu etkinlik için tüm yerler dolmuştur."))
            
        # Aynı etkinliğe önceden rezervasyon yapılıp yapılmadığı kontrolü
        if Reservation.objects.filter(user=self.user, event=self.event).exists():
            raise ValidationError(_("Bu etkinlik için zaten bir rezervasyon yapmış bulunmaktasınız."))
        
        # Bakiye kontrolü
        if self.user.balance < self.event.price:
            raise ValidationError(_("Yetersiz bakiye. Lütfen önce bakiye yükleyiniz."))
            
        # Geçmiş etkinlik kontrolü
        if self.event.is_past:
            raise ValidationError(_("Geçmiş etkinliklere rezervasyon yapamazsınız."))
            
        return cleaned_data

class BalanceForm(forms.Form):
    """
    Bakiye yükleme formu
    """
    amount = forms.DecimalField(
        label=_("Yüklenecek Miktar"),
        min_value=Decimal('10.00'),
        max_value=Decimal('1000.00'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text=_("10.00 TL ile 1000.00 TL arasında bir değer giriniz")
    )
    
    # İsteğe bağlı - ödeme simülasyonu
    card_number = forms.CharField(
        label=_("Kart Numarası"),
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456'
        })
    )
    
    card_holder = forms.CharField(
        label=_("Kart Üzerindeki İsim"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'AD SOYAD'
        })
    )
    
    expiry_date = forms.CharField(
        label=_("Son Kullanma Tarihi"),
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY'
        })
    )
    
    cvv = forms.CharField(
        label=_("CVV"),
        max_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123'
        })
    )
    
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) not in [15, 16]:
            raise ValidationError(_("Geçerli bir kart numarası giriniz"))
        return card_number
        
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if len(expiry_date) != 5 or expiry_date[2] != '/':
            raise ValidationError(_("Son kullanma tarihini MM/YY formatında giriniz"))
        try:
            month = int(expiry_date.split('/')[0])
            year = int(expiry_date.split('/')[1])
            if month < 1 or month > 12:
                raise ValidationError(_("Ay değeri 01-12 arasında olmalıdır"))
        except (ValueError, IndexError):
            raise ValidationError(_("Son kullanma tarihini MM/YY formatında giriniz"))
        return expiry_date
        
    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) != 3:
            raise ValidationError(_("CVV 3 haneli bir sayı olmalıdır"))
        return cvv

class EventFilterForm(forms.Form):
    """
    Etkinlik filtreleme formu
    """
    city = forms.CharField(
        label=_("Şehir"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        label=_("En Düşük Fiyat"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    max_price = forms.DecimalField(
        label=_("En Yüksek Fiyat"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        label=_("Başlangıç Tarihi"),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        label=_("Bitiş Tarihi"),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError(_("En düşük fiyat en yüksek fiyattan büyük olamaz"))
            
        if start_date and end_date and start_date > end_date:
            raise ValidationError(_("Başlangıç tarihi bitiş tarihinden büyük olamaz")) 