from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_detail')
    last_seen = models.DateTimeField(default=timezone.now)
    email_notification_sent = models.BooleanField(default=False)
    city = models.CharField(max_length=100, default='nie podano')
    street = models.CharField(max_length=100, default='nie podano')
    number = models.CharField(max_length=100, default='nie podano')

    def __str__(self):
        return f'{self.user.username} detail'
