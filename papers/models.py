from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete


class StudentClub(models.Model):
    name = models.CharField(max_length=128)
    acronym = models.CharField(max_length=12)

    def __str__(self):
        return self.acronym


class Paper(models.Model):
    title = models.CharField(max_length=128)
    club = models.ForeignKey(StudentClub, on_delete=models.CASCADE)
    authors = models.ManyToManyField(User)
    authors_string = models.CharField(max_length=128)
    original_author_id = models.IntegerField()
    keywords = models.CharField(max_length=64)
    description = models.TextField()
    add_date = models.DateTimeField(default=timezone.now)
    last_edit_date = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)


class CoAuthor(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    email = models.EmailField()
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)


def paper_directory_path(instance, filename):
    return f'paper_files{instance.paper.pk}/{filename}'


class UploadedFile(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    file = models.FileField(upload_to=paper_directory_path)
    add_date = models.DateTimeField(default=timezone.now)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    comment = models.TextField()


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    add_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_date = models.DateTimeField(default=timezone.now)


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()


def check_empty_author_relation(instance, **kwargs):
    papers = Paper.objects.filter(authors=instance)
    for paper in papers:
        if len(paper.authors.all()) == 1:
            paper.delete()
        elif paper.original_author_id == instance.pk:
            for author in paper.authors.all():
                if author.pk != instance.pk:
                    paper.original_author_id = author.pk
                    paper.save()
                    break


pre_delete.connect(check_empty_author_relation, sender=User)
