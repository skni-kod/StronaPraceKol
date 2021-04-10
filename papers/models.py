import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.utils import timezone


class StudentClub(models.Model):
    name = models.CharField(max_length=128)
    acronym = models.CharField(max_length=12)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.acronym

    @classmethod
    def get_default_pk(cls):
        club, created = cls.objects.get_or_create(name='Brak koła', acronym='Brak')
        return club.pk


class Paper(models.Model):

    title = models.CharField(max_length=128)
    club = models.ForeignKey(StudentClub, default=StudentClub.get_default_pk, on_delete=models.SET_DEFAULT)
    authors = models.ManyToManyField(User, related_name='authors', blank=True)
    original_author_id = models.IntegerField()
    keywords = models.CharField(max_length=128)
    description = models.TextField()
    add_date = models.DateTimeField(default=timezone.now)
    last_edit_date = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    reviewers = models.ManyToManyField(User, related_name='reviewers', blank=True, max_length=2)

    def __str__(self):
        return f'{self.title[0:40]}'

    def get_unread_messages(self, user):
        cnt = 0
        for review in Review.objects.filter(paper=self):
            for message in Message.objects.filter(review=review):
                if not review.author == user and not message.author == user:
                    break
                if message.author == user:
                    continue
                if not message.is_seen(user):
                    cnt += 1
        return cnt


class CoAuthor(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)


def paper_directory_path(instance, filename):
    return f'paper_files/paperNo.{instance.paper.pk}/{filename}'


class UploadedFile(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    file = models.FileField(upload_to=paper_directory_path, blank=True)
    add_date = models.DateTimeField(default=timezone.now)

    def filename(self):
        return os.path.basename(self.file.name)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    text = models.TextField()


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()


def check_empty_author_relation(instance, **kwargs):
    """
    Checks if user that is being deleted is an original author of any paper of the last author of any paper.
    If any paper has no other authors it's deleted, otherwise original_author is replaced with another author
    :param instance: User objects (user that is being deleted)
    :param kwargs:
    :return:
    """
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


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    add_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def is_seen(self, user):
        if MessageSeen.objects.filter(reader=user, message=self).count() > 0:
            return True
        return False

    def __str__(self):
        return f'[{self.author.username}][{self.add_date.strftime("%d-%m-%Y %H:%M")}]: {self.text[0:30]}'


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.reader.username} seen: {self.message}'


def delete_file_with_object(instance, **kwargs):
    """
    Deletes files from system when UploadedFile object is deleted from database
    :param instance: UploadedFile object (file that is being deleted)
    :param kwargs:
    :return:
    """
    instance.file.delete()


pre_delete.connect(check_empty_author_relation, sender=User)
pre_delete.connect(delete_file_with_object, sender=UploadedFile)
