from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('kontakt/', views.ContactView.as_view(), name='contact'),
    path('rejestracja/', views.RegisterView.as_view(), name='register'),
    path('logowanie/',views.LoginView.as_view(), name='login'),
    path('wylogowany/',views.LogoutView.as_view(), name='logout'),
    path('profil/', views.ProfileView.as_view(), name='profile'),
    path('zmiana_hasła/', views.PasswordChangeView.as_view(), name='passwordChange'),
    path('usuwanie_konta/', views.AccountDeleteView.as_view(), name='accountDelete'),
]