from django.contrib.auth import views as pass_reset_view
from django.urls import path

from . import views

urlpatterns = [
    #path('register/', views.RegisterView.as_view(), name='register'),
    path('register/', views.LoginView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password_change/', views.PasswordChangeView.as_view(), name='passwordChange'),
    path('account_delete/', views.AccountDeleteView.as_view(), name='accountDelete'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', pass_reset_view.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', pass_reset_view.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', pass_reset_view.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('notificationEmail/', views.SendNotificationsView.as_view(), name='sendNotificationEmail'),
]
