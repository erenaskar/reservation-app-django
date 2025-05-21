from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('events/<int:pk>/reserve/', views.make_reservation, name='make_reservation'),
    path('reservations/', views.user_reservations, name='user_reservations'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/add-balance/', views.add_balance, name='add_balance'),
] 