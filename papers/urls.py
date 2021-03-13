from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaperListView.as_view(), name='paper-list'),
    path('paper/new', views.PaperCreateView.as_view(), name='paper-create'),
    path('paper/<int:pk>/', views.PaperDetailView.as_view(), name='paper-detail'),
    path('paper/<int:pk>/file/<int:item>/', views.paper_file_download, name='paper-file-download')
]

