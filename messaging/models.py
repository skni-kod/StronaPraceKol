from django.db import models
from django.contrib.auth.models import User
from papers.models import Review
from django.utils import timezone


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    add_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def __str__(self):
        return f'[{self.author.username}][{self.add_date.strftime("%d-%m-%Y %H:%M")}]: {self.text[0:30]}'


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.reader.username} seen: {self.message}'
