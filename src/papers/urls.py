from django.urls import path

from . import views

urlpatterns = [
    path('', views.PaperListView.as_view(), name='paperList'),
    #papers
    path('paper/new/', views.PaperCreateView.as_view(), name='paperCreate'),
    path('paper/<int:pk>/', views.PaperDetailView.as_view(), name='paperDetail'),
    path('paper/<int:pk>/file/<int:item>/', views.paper_file_download, name='paperFileDownload'),
    path('paper/<int:pk>/edit/', views.PaperEditView.as_view(), name='paperEdit'),
    path('paper/<int:pk>/delete/', views.PaperDeleteView.as_view(), name='paperDelete'),
    path('paper/<int:paper>/review/<int:reviewer>/', views.userReviewShow, name='reviewShow'),
    path('paper/<int:pk>/review/assign/', views.ReviewerAssignmentView.as_view(), name='reviewerAssignment'),
    #reviews
    path('review/', views.ReviewListView.as_view(), name='reviewList'),
    path('review/<int:paper>/new/', views.ReviewCreateView.as_view(), name='reviewCreate'),
    path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='reviewDetail'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='reviewEdit'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='reviewDelete'),
    path('review/success/', views.ReviewSuccessView.as_view(), name='reviewSuccess'),
]
