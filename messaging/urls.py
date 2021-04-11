from django.urls import path

from .views import get_message, send_message, render_message

urlpatterns = [
    path('get_message/', get_message, name='get_messages'),
    path('send_message/', send_message, name='send_message'),
    path('render_message/', render_message, name='render_messages'),
]
