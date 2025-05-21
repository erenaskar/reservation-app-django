from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import uuid

class User(AbstractUser):
    """
    Özel kullanıcı modeli
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('organizator', 'Organizatör'),
        ('user', 'Kullanıcı'),
    )
    
    balance = models.DecimalField(_("Bakiye"), max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(_("Rol"), max_length=20, choices=ROLE_CHOICES, default='user')
    
    class Meta:
        verbose_name = _("Kullanıcı")
        verbose_name_plural = _("Kullanıcılar")

    def __str__(self):
        return self.username

class Event(models.Model):
    """
    Etkinlik modeli
    """
    title = models.CharField(_("Başlık"), max_length=200)
    description = models.TextField(_("Açıklama"))
    event_date = models.DateTimeField(_("Tarih/Saat"))
    price = models.DecimalField(_("Fiyat"), max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(_("Kapasite"))
    location = models.CharField(_("Konum"), max_length=200)
    city = models.CharField(_("Şehir"), max_length=100)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name=_("Oluşturan"))
    
    class Meta:
        verbose_name = _("Etkinlik")
        verbose_name_plural = _("Etkinlikler")
        ordering = ['event_date']

    def __str__(self):
        return self.title
    
    @property
    def available_seats(self):
        return self.capacity - self.reservations.count()
    
    @property
    def is_full(self):
        return self.available_seats <= 0
    
    @property
    def is_past(self):
        from django.utils import timezone
        return self.event_date < timezone.now()

class Reservation(models.Model):
    """
    Rezervasyon modeli
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name=_("Kullanıcı"))
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations', verbose_name=_("Etkinlik"))
    reservation_code = models.UUIDField(_("Rezervasyon Kodu"), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    qr_code = models.ImageField(_("QR Kod"), upload_to='qr_codes/', blank=True, null=True)
    
    class Meta:
        verbose_name = _("Rezervasyon")
        verbose_name_plural = _("Rezervasyonlar")
        unique_together = ('user', 'event')
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # QR Kod oluşturma
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"Rezervasyon No: {self.reservation_code}\nEtkinlik: {self.event.title}\nKullanıcı: {self.user.username}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            self.qr_code.save(f'qr_{self.reservation_code}.png', File(buffer), save=False)
            
        super().save(*args, **kwargs)
