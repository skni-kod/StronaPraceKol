import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.utils import timezone
import textwrap

from django.utils.text import slugify


class NotificationPeriod(models.Model):
    name = models.CharField(max_length=64)
    period = models.IntegerField()  # in seconds
    last_used = models.DateTimeField(default=timezone.now)


class StudentClub(models.Model):
    name = models.CharField(max_length=128)
    faculty = models.CharField(max_length=128)
    patron = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_pk(cls):
        club, created = cls.objects.get_or_create(name='Brak', faculty='', patron='')
        return club.pk


class Paper(models.Model):
    title = models.CharField(max_length=128)
    club = models.ForeignKey(StudentClub, default=StudentClub.get_default_pk, on_delete=models.SET_DEFAULT)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=128)
    description = models.TextField()
    approved = models.BooleanField(default=False)
    reviewers = models.ManyToManyField(User, related_name='reviewers', blank=True, max_length=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    statement = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.title[0:40]}'

    def get_unread_messages(self, user):
        if user not in self.reviewers.all() and user != self.author:
            return []

        messages = []
        for message in Message.objects.filter(paper=self):
            if message.author == user:
                continue
            if not message.is_seen(user):
                messages.append(message)

        return messages


class CoAuthor(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)


def remove_polish_chars(text):
    polish_chars = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }

    for polish_char, ascii_char in polish_chars.items():
        text = text.replace(polish_char, ascii_char)

    return text

def paper_directory_path(instance, filename):
    _filename = filename.split('.')
    filename = re.sub(r'\W+', '', _filename[0])
    filename = filename.replace(' ','_')
    filename = textwrap.shorten(filename,width=100,placeholder='')
    filename += f'.{_filename[-1]}'
    return f'paper_files/paperNo.{instance.paper.pk}/{filename}'


class UploadedFile(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    file = models.FileField(upload_to=paper_directory_path, blank=True,max_length=512)
    created_at = models.DateTimeField(default=timezone.now)

    def filename(self):
        return os.path.basename(self.file.name)


class Grade(models.Model):
    BADGE_STYLES = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
    )

    GRADE_CATEGORIES = (
        ('correspondence', 'Zgodność z tematyką'),
        ('originality', 'Oryginalność'),
        ('merits', 'Poprawność merytoryczna'),
        ('presentation', 'Jakość prezentacji'),
        ('final_grade', 'Ocena końcowa'),
    )

    def get_tag_display_text(self):
        for itm in self.GRADE_CATEGORIES:
            if itm[0] == self.tag:
                return itm[1]
        return ''

    name = models.CharField(max_length=32)
    value = models.CharField(max_length=16, default='')
    tag = models.CharField(max_length=16, choices=GRADE_CATEGORIES)
    display_color = models.CharField(max_length=16, default='primary', choices=BADGE_STYLES)

    def __str__(self):
        return f'[{self.tag}] {self.name}'


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    text = models.TextField()
    correspondence = models.ForeignKey(Grade, related_name='correspondence', on_delete=models.SET_NULL, blank=True,
                                       null=True, limit_choices_to={'tag': 'correspondence'})
    originality = models.ForeignKey(Grade, related_name='originality', on_delete=models.SET_NULL, blank=True,
                                    null=True, limit_choices_to={'tag': 'originality'})
    merits = models.ForeignKey(Grade, related_name='merits', on_delete=models.SET_NULL, blank=True,
                               null=True, limit_choices_to={'tag': 'merits'})
    presentation = models.ForeignKey(Grade, related_name='presentation', on_delete=models.SET_NULL, blank=True,
                                     null=True, limit_choices_to={'tag': 'presentation'})
    final_grade = models.ForeignKey(Grade, related_name='final_grade', on_delete=models.SET_NULL, blank=True,
                                    null=True, limit_choices_to={'tag': 'final_grade'})
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def aggregate_grades(self):
        return self.correspondence, self.originality, self.merits, self.presentation, self.final_grade

    def __str__(self):
        return f'[{self.author}] - {self.paper}'


class Announcement(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return textwrap.shorten(self.text, width=20)


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, related_name='paper', default=None, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviewer', default=None, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def is_seen(self, user):
        if MessageSeen.objects.filter(reader=user, message=self).count() > 0:
            return True
        return False

    def __str__(self):
        return f'[{self.author.username}][{self.created_at.strftime("%d-%m-%Y %H:%M")}]: {self.text[0:30]}'


class MessageSeen(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

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


pre_delete.connect(delete_file_with_object, sender=UploadedFile)