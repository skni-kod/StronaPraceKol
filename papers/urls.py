from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaperListView.as_view(), name='paper-list'),
    path('paper/<int:pk>/', views.PaperDetailView.as_view(), name='paper-detail'),
]

