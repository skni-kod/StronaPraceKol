from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from papers.models import StudentClub
from django.utils import timezone
import textwrap
import os
import re


class Document(models.Model):
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=128)
    club = models.ForeignKey(StudentClub, null=True, on_delete=models.SET_NULL)
    ready = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.name[0:40]}'


def document_directory_path(instance, filename):
    _filename = filename.split('.')
    filename = re.sub(r'\W+', '', _filename[0])
    filename = filename.replace(' ','_')
    filename = textwrap.shorten(filename,width=100,placeholder='')
    filename += f'.{_filename[-1]}'
    return f'document_files/documentNo.{instance.document.pk}/{filename}'


class UploadedFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    file = models.FileField(upload_to=document_directory_path, blank=True, max_length=512)

    def filename(self):
        return os.path.basename(self.file.name)


def delete_file_with_object(instance, **kwargs):
    """
    Deletes files from system when UploadedFile object is deleted from database
    :param instance: UploadedFile object (file that is being deleted)
    :param kwargs:
    :return:
    """
    instance.file.delete()


pre_delete.connect(delete_file_with_object, sender=UploadedFile)
