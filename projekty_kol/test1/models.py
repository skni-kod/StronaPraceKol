from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

'''
class Referats(models.Model):
    title = models.CharField(max_length=100)
    autors = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
'''
class StudentClub(models.Model):
    name = models.CharField(max_length=128)  # can be changed to longer
    acronym = models.CharField(max_length=12)

    def __str__(self):
        return self.acronym


class Paper(models.Model):
    title = models.CharField(max_length=128)  # can be changed to longer
    club = models.ForeignKey(StudentClub, on_delete=models.CASCADE)
    authors = models.CharField(max_length=128)
    keywords = models.CharField(max_length=64)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    add_date = models.DateTimeField(default=timezone.now)
    last_edit_date = models.DateTimeField(default=timezone.now)
    status = models.SmallIntegerField()


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    comment = models.TextField()


def paper_directory_path(instance, filename):
    return f'paper_files/{instance.paper.id}/{filename}'


class UploadedFile(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    file = models.FileField(upload_to=paper_directory_path)
    upload_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class DownloadedFile(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    download_date = models.DateTimeField(default=timezone.now)