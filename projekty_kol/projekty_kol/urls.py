"""projekty_kol URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

'''
To add app
'''
from test1 import views
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.index, name='index'),
    path('admin/', admin.site.urls),
    path('index/',views.index, name='index'),
    path('indexLog/',views.indexLog, name='indexLog'),
    path('logowanie/',views.LoginView.as_view(template_name='logowanie.html'), name='logowanie'),
    path('wylogowany/',views.LogoutView.as_view(template_name='wylogowany.html'), name='wylogowany'),
    #path('logowanie/',views.logowanie, name='logowanie'),
    path('rejestracja/',views.rejestracja, name='rejestracja'),
    path('kontakt/',views.kontakt,name='kontakt'),
    #path('referaty/',views.referaty,name='referaty'),
    path('referaty/',views.ReferatListView.as_view(),name='referaty'),
    path('dodajReferat/',views.dodajReferat,name='dodajReferat'),
    path('dodajReferat/',views.dodajReferat),
    path('profile/', views.profile, name='profile'),
    path('summernote/', include('django_summernote.urls')),
    
]
