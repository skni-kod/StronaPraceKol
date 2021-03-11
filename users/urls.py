from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    #path('kontakt/', views.contact, name='contact'),
    path('kontakt/', views.ContactView.as_view(), name='contact'),
    #path('rejestracja/', views.register, name='register'),
    path('rejestracja/', views.RegisterView.as_view(), name='register'),

    path('logowanie/',views.LoginView.as_view(), name='login'),
    path('wylogowany/',views.LogoutView.as_view(), name='logout'),
    #path('profil/', views.profile, name='profile'),
    path('profil/', views.ProfileView.as_view(), name='profile'),
]