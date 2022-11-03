from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=timezone.now)
    email_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} detail'
