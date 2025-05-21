from django.contrib import admin
from .models import User, Event, Reservation
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'balance', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Account info'), {'fields': ('balance', 'role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'price', 'capacity', 'available_seats', 'city', 'creator')
    list_filter = ('event_date', 'city')
    search_fields = ('title', 'description', 'location', 'city')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'event_date'
    
    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = _("Kalan Kapasite")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Organizatörler sadece kendi etkinliklerini görebilir
        if request.user.role == 'organizator':
            return qs.filter(creator=request.user)
        return qs

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('reservation_code', 'created_at', 'qr_code')
