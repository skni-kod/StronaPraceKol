from django.contrib import admin
from django.urls import include, path
from .views import send_json, AboutView

urlpatterns = [
    path('test/', AboutView.as_view()),
    path('get_message/', send_json),
]
