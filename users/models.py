from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import textwrap


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=timezone.now)
    email_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} detail'


class ContactInfo(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakty"


class Announcement(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return textwrap.shorten(self.text, width=20)

    class Meta:
        verbose_name = "Ogłoszenie"
        verbose_name_plural = "Ogłoszenia"

