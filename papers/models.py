import os
import re
import textwrap

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_file_size(value):
    """Validate whether the uploaded file size is within the allowed limit (MAX_FILE_SIZE)."""
    if value.size > MAX_FILE_SIZE:
        raise ValidationError(f'Maximum file size is {MAX_FILE_SIZE / (1024 * 1024)} MB.')

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
    author_percentage= models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    author_phone = models.CharField(max_length=16, blank=True)
    keywords = models.CharField(max_length=128)
    description = models.TextField()
    approved = models.BooleanField(default=False)
    reviewers = models.ManyToManyField(User, related_name='reviewers', blank=True, max_length=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    statement = models.PositiveIntegerField(default=0)
    statement_reminder_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.title[0:40]}'
    
    def has_statement(self):
        """Check if statement file was uploaded"""
        return self.statement > 0 and UploadedFile.objects.filter(pk=self.statement).exists()

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
    percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
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
    ext = filename.split('.')[-1]
    clean_name = re.sub(r'\W+', '', filename.rsplit('.', 1)[0])
    short_name = clean_name[:40]

    return f'paper_files/paperNo.{instance.paper.pk}/{short_name}.{ext}'

    # _filename = filename.split('.')
    # filename = re.sub(r'\W+', '', _filename[0])
    # filename = filename.replace(' ','_')
    # filename = textwrap.shorten(filename,width=100,placeholder='')
    # filename += f'.{_filename[-1]}'
    # return f'paper_files/paperNo.{instance.paper.pk}/{filename}'


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
        ('originality', 'Czy jest to oryginalne opracowanie wśród publikacji z tego zakresu?'),
        ('layout', 'Czy układ opracowania jest zadowalający?'),
        ('length', 'Czy objętość  opracowania jest adekwatna do jego treści?'),
        ('language', 'Czy język oraz sposób przedstawienia wyników jest jasny dla czytelnika?'),
        ('nomenclature', 'Czy oznaczenia oraz terminologia odpowiadają standardom z określonej dyscypliny nauki?'),
        ('interpretation', 'Czy według Pani(a) opinii interpretacja wyników oraz wnioski są logiczne i uzasadnione?'),
        ('abstract', 'Czy streszczenie zawiera wystarczające oraz użyteczne informacje?'),
        ('title', 'Czy tytuł artykułu jest jasny i odpowiada jego treści?'),
        ('illustrations', 'Czy rysunki i tabele są potrzebne oraz odpowiednie?'),
        ('final_grade', 'Wniosek końcowy (rekomendacja do celów wydawniczych): praca'),
    )

    GRADE_CATEGORIES_EN = (
        ('originality', 'Is this a new and original contribution to the literature in this field?'),
        ('layout', 'Is the organization of the paper satisfactory?'),
        ('length', 'Is the length of the paper appropriate to the content?'),
        ('language', 'Is the language and presentation clear to readers familiar with the field?'),
        ('nomenclature', 'Do the notation and nomenclature used meet the standards determined in the area which the paper deals with?'),
        ('interpretation', 'Do the interpretation of the results and conclusions sound logical and justifiable in your opinion?'),
        ('abstract', 'Does the abstract contain sufficient and useful information?'),
        ('title', 'Does the title of the paper reflect sufficiently and clearly the content?'),
        ('illustrations', 'Are the illustrations and tables all necessary and acceptable?'),
        ('final_grade', 'Final recommendation (to publishing purpose): paper'),
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

    originality = models.ForeignKey(
        Grade, related_name='originality',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'originality'}
    )

    layout = models.ForeignKey(
        Grade, related_name='layout',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'layout'}
    )

    length = models.ForeignKey(
        Grade, related_name='length',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'length'}
    )

    language = models.ForeignKey(
        Grade, related_name='language',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'language'}
    )

    nomenclature = models.ForeignKey(
        Grade, related_name='nomenclature',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'nomenclature'}
    )

    interpretation = models.ForeignKey(
        Grade, related_name='interpretation',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'interpretation'}
    )

    abstract = models.ForeignKey(
        Grade, related_name='abstract',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'abstract'}
    )

    title = models.ForeignKey(
        Grade, related_name='title',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'title'}
    )

    illustrations = models.ForeignKey(
        Grade, related_name='illustrations',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'illustrations'}
    )

    final_grade = models.ForeignKey(
        Grade, related_name='final_grade',
        on_delete=models.SET_NULL, blank=True, null=True,
        limit_choices_to={'tag': 'final_grade'}
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def aggregate_grades(self):
        return (
            self.originality,
            self.layout,
            self.length,
            self.language,
            self.nomenclature,
            self.interpretation,
            self.abstract,
            self.title,
            self.illustrations,
            self.final_grade,
        )

    def get_questions_with_answers(self):
        result = []

        for tag, label in Grade.GRADE_CATEGORIES:
            selected_grade = getattr(self, tag)

            label_en = next((item[1] for item in Grade.GRADE_CATEGORIES_EN if item[0] == tag), '')

            options = []
            for grade in Grade.objects.filter(tag=tag):
                options.append({
                    "name": grade.name,
                    "checked": selected_grade and grade.pk == selected_grade.pk
                })

            result.append({
                "tag": tag,
                "label": label,
                "label_en": label_en,
                "options": options
            })

        return result

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