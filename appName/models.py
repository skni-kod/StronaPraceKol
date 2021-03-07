from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete


class StudentClub(models.Model):
    name = models.CharField(max_length=128)  # can be changed to longer
    acronym = models.CharField(max_length=12)

    def __str__(self):
        return self.acronym


class Paper(models.Model):
    title = models.CharField(max_length=128)  # can be changed to longer
    club = models.ForeignKey(StudentClub, on_delete=models.CASCADE)
    authors = models.ManyToManyField(User)
    authors_string = models.CharField(max_length=128)
    keywords = models.CharField(max_length=64)
    description = models.TextField()
    add_date = models.DateTimeField(default=timezone.now)
    last_edit_date = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField()

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    comment = models.TextField()

    def __str__(self):
        return self.paper.title


# alternate Review model
# class Review(models.Model):
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
#     upload_date = models.DateTimeField(default=timezone.now)
#     comment = models.TextField()
#     originality = models.SmallIntegerField()
#     accordance = models.SmallIntegerField()
#     quality = models.SmallIntegerField()
#     final_grade = models.SmallIntegerField()
#     approved = models.BooleanField()
#
#     def __str__(self):
#         return self.paper.title


def paper_directory_path(instance, filename):
    return f'paper_files/{instance.paper.id}/{filename}'


class UploadedFile(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    file = models.FileField(upload_to=paper_directory_path)
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.paper.title


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    text = models.TextField()


# checks if any paper has only one author (that is being deleted) and deletes them if any are found
def check_empty_authors_relation(instance, **kwargs):
    for paper in Paper.objects.filter(authors=instance):
        if len(paper.authors.all()) == 1:
            paper.delete()


pre_delete.connect(check_empty_authors_relation, sender=User)
