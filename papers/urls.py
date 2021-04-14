from django.urls import path

from . import views

urlpatterns = [
    path('', views.PaperListView.as_view(), name='paperList'),
    path('paper/new', views.PaperCreateView.as_view(), name='paperCreate'),
    path('paper/<int:pk>/', views.PaperDetailView.as_view(), name='paperDetail'),
    path('paper/<int:pk>/file/<int:item>/', views.paper_file_download, name='paperFileDownload'),
    path('paper/<int:pk>/edit/', views.PaperEditView.as_view(), name='paperEdit'),
    path('paper/<int:pk>/delete/', views.PaperDeleteView.as_view(), name='paperDelete'),
    path('paper/<int:pk>/reviews/', views.ReviewListView.as_view(), name='reviewList'),
    path('paper/<int:pk>/addreview/', views.ReviewCreateView.as_view(), name='reviewCreate'),
    path('paper/<int:paper>/review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='reviewEdit'),
    path('paper/<int:paper>/review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='reviewDelete'),
    path('reviews/', views.UserReviewListView.as_view(), name='userReviewList'),
    path('paper/<int:pk>/review/assign/', views.ReviewerAssignmentView.as_view(), name='reviewerAssignment'),

]
