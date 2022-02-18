from django.urls import path

from . import views

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='documentList'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='documentDetail'),
    path('document/new/', views.DocumentCreateView.as_view(), name="documentCreate"),
    path('document/<int:pk>/edit', views.DocumentEditView.as_view(), name="documentEdit"),
    path('document/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='documentDelete'),
    path('document/<int:pk>/file/<int:item>/', views.document_file_download, name='documentFileDownload'),
]
