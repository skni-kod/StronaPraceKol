from django.urls import path
from . import views
from django.contrib.auth import views as pass_reset_view


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('kontakt/', views.ContactView.as_view(), name='contact'),
    path('rejestracja/', views.RegisterView.as_view(), name='register'),
    path('logowanie/',views.LoginView.as_view(), name='login'),
    path('wylogowany/',views.LogoutView.as_view(), name='logout'),
    path('profil/', views.ProfileView.as_view(), name='profile'),
    path('zmiana_hasła/', views.PasswordChangeView.as_view(), name='passwordChange'),
    path('usuwanie_konta/', views.AccountDeleteView.as_view(), name='accountDelete'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', pass_reset_view.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', pass_reset_view.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', pass_reset_view.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]