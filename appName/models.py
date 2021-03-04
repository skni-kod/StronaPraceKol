from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class StudentClub(models.Model):
    name = models.CharField(max_length=128)  # can be changed to longer
    acronym = models.CharField(max_length=12)

    def __str__(self):
        return self.acronym


class Paper(models.Model):
    title = models.CharField(max_length=128)  # can be changed to longer
    club_id = models.SmallIntegerField()
    keywords = models.CharField(max_length=64)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    add_date = models.DateTimeField(default=timezone.now)
    last_edit_date = models.DateTimeField(default=timezone.now)
    status = models.SmallIntegerField()


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
    paper_id = models.SmallIntegerField()
    upload_date = models.DateTimeField(default=timezone.now)
    comment = models.TextField()


class UploadedFile(models.Model):
    paper_id = models.SmallIntegerField()
    file = models.FileField(upload_to=f'paper_files{paper_id}')  # TODO test if it rly works
    upload_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class DownloadedFile(models.Model):
    file_id = models.SmallIntegerField()
    author_id = models.SmallIntegerField()
    download_date = models.DateTimeField(default=timezone.now)
