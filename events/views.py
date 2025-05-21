from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone

from .models import User, Event, Reservation
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    ReservationForm, 
    BalanceForm,
    EventFilterForm
)

# Anasayfa
def home(request):
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:6]
    return render(request, 'events/home.html', {'events': upcoming_events})

# Etkinlik Listeleme ve Filtreleme
def event_list(request):
    events = Event.objects.filter(event_date__gte=timezone.now())
    form = EventFilterForm(request.GET or None)
    
    if form.is_valid():
        if form.cleaned_data.get('city'):
            events = events.filter(city__icontains=form.cleaned_data['city'])
        
        if form.cleaned_data.get('min_price'):
            events = events.filter(price__gte=form.cleaned_data['min_price'])
        
        if form.cleaned_data.get('max_price'):
            events = events.filter(price__lte=form.cleaned_data['max_price'])
        
        if form.cleaned_data.get('start_date'):
            events = events.filter(event_date__date__gte=form.cleaned_data['start_date'])
        
        if form.cleaned_data.get('end_date'):
            events = events.filter(event_date__date__lte=form.cleaned_data['end_date'])
    
    paginator = Paginator(events, 9)  # 9 etkinlik per sayfa
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'form': form,
    })

# Etkinlik Detayı
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_has_reservation = False
    
    if request.user.is_authenticated:
        user_has_reservation = Reservation.objects.filter(user=request.user, event=event).exists()
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_has_reservation': user_has_reservation,
    })

# Kayıt Olma
class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'events/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, _("Hesabınız başarıyla oluşturuldu. Şimdi giriş yapabilirsiniz."))
        return super().form_valid(form)

# Giriş Yapma
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'events/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, _("Başarıyla giriş yaptınız."))
        return super().form_valid(form)

# Çıkış Yapma
def logout_view(request):
    logout(request)
    messages.success(request, _("Başarıyla çıkış yaptınız."))
    return redirect('home')

# Rezervasyon Yapma
@login_required
def make_reservation(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user already has a reservation
    if Reservation.objects.filter(user=request.user, event=event).exists():
        messages.error(request, _("Bu etkinlik için zaten bir rezervasyon yapmış bulunmaktasınız."))
        return redirect('event_detail', pk=event.pk)
    
    # Check event capacity
    if event.is_full:
        messages.error(request, _("Bu etkinlik için tüm yerler dolmuştur."))
        return redirect('event_detail', pk=event.pk)
    
    # Check if event is in the past
    if event.is_past:
        messages.error(request, _("Geçmiş etkinliklere rezervasyon yapamazsınız."))
        return redirect('event_detail', pk=event.pk)
    
    # Check user balance
    if request.user.balance < event.price:
        messages.error(request, _("Bakiyeniz yetersiz. Lütfen önce bakiye yükleyiniz."))
        return redirect('add_balance')
    
    form = ReservationForm(request.POST or None, user=request.user, event=event)
    
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            # Decrement user balance
            request.user.balance -= event.price
            request.user.save(update_fields=['balance'])
            
            # Create reservation
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.event = event
            reservation.save()
        
        messages.success(request, _("Rezervasyonunuz başarıyla yapıldı."))
        return redirect('reservation_detail', pk=reservation.pk)
    
    return render(request, 'events/make_reservation.html', {
        'form': form,
        'event': event,
    })

# Kullanıcı Rezervasyonları
@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'events/user_reservations.html', {'reservations': reservations})

# Rezervasyon Detayı
@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    return render(request, 'events/reservation_detail.html', {'reservation': reservation})

# Bakiye Yükleme
@login_required
def add_balance(request):
    if request.method == 'POST':
        form = BalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            # Basit bir ödeme simülasyonu
            request.user.balance += amount
            request.user.save(update_fields=['balance'])
            
            messages.success(request, _(f"{amount} TL bakiyenize başarıyla yüklendi."))
            return redirect('profile')
    else:
        form = BalanceForm()
    
    return render(request, 'events/add_balance.html', {'form': form})

# Kullanıcı Profili
@login_required
def profile(request):
    return render(request, 'events/profile.html', {'user': request.user})
