from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaperListView.as_view(), name='paperList'),
    path('paper/new', views.PaperCreateView.as_view(), name='paperCreate'),
    path('paper/<int:pk>/', views.PaperDetailView.as_view(), name='paperDetail'),
    path('paper/<int:pk>/file/<int:item>/', views.paper_file_download, name='paperFileDownload'),
]

