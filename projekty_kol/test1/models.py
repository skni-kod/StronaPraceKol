from django.db import models

# Create your models here.


class Referats(models.Model):
    title = models.CharField(max_length=100)
    autors = models.CharField(max_length=100)
    status = models.CharField(max_length=20) 