import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from .models import *


### FILE FORMS

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        labels = {'file': _('Pliki')}
        help_texts = {'file': _('Pliki możesz dodać później w zakładce edycji referatu')}
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('file'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


UploadedFileFormSet = inlineformset_factory(Paper, UploadedFile, form=FileUploadForm,
                                            fields=['file'], extra=1, can_delete=True)


class FileAppendForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        labels = {'file': _('Pliki')}
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('file'),
                Field('DELETE', type='hidden'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


## CO AUTHOR FORMS

class CoAuthorForm(forms.ModelForm):
    class Meta:
        model = CoAuthor
        fields = ['name', 'surname', 'email']
        labels = {
            'name': _('Imię'),
            'surname': _('Nazwisko')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Field('name'),
                Field('surname'),
                Field('email'),
                css_class='formset_row-{}'.format(formtag_prefix)
            )
        )


CoAuthorFormSet = inlineformset_factory(Paper, CoAuthor, form=CoAuthorForm,
                                        fields=['name', 'surname', 'email'], extra=1,
                                        can_delete=True)


class CoAuthorDynamicForm(forms.ModelForm):
    class Meta:
        model = Paper
        exclude = ('title', 'club', 'authors', 'original_author_id',
                   'keywords', 'description', 'approved', 'reviewers', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coAuthors = CoAuthor.objects.filter(paper=self.instance)
        for i in range(len(coAuthors) + 1):
            name_field_name = f'coAuthor_{i}_name'
            surname_field_name = f'coAuthor_{i}_surname'
            email_field_name = f'coAuthor_{i}_email'
            self.fields[name_field_name] = forms.CharField(required=True)
            self.fields[surname_field_name] = forms.CharField(required=True)
            self.fields[email_field_name] = forms.EmailField(required=False)
            try:
                self.initial[name_field_name] = coAuthors[i].name
                self.initial[surname_field_name] = coAuthors[i].surname
                self.initial[email_field_name] = coAuthors[i].email
            except IndexError:
                self.initial[name_field_name] = ''
                self.initial[surname_field_name] = ''
                self.initial[email_field_name] = ''
        # create extra blank fields
        name_field_name = f'coAuthor_{i + 1}_name'
        surname_field_name = f'coAuthor_{i + 1}_surname'
        email_field_name = f'coAuthor_{i + 1}_email'
        self.fields[name_field_name] = forms.CharField(required=True)
        self.fields[surname_field_name] = forms.CharField(required=True)
        self.fields[email_field_name] = forms.EmailField(required=False)

    def clean(self):
        coAuthors = set()
        i = 0
        name_field_name = f'coAuthor_{i}_name'
        surname_field_name = f'coAuthor_{i}_surname'
        email_field_name = f'coAuthor_{i}_email'
        while self.cleaned_data.get(name_field_name):
            coAuthors.add([self.cleaned_data[name_field_name],
                           self.cleaned_data[surname_field_name],
                           self.cleaned_data[email_field_name]])
            i += 1
            name_field_name = f'coAuthor_{i}_name'
            surname_field_name = f'coAuthor_{i}_surname'
            email_field_name = f'coAuthor_{i}_email'
        self.cleaned_data['coAuthors'] = coAuthors

    def save(self):
        paper = self.instance
        paper.coauthor_set.all().delete()
        for coAuthor in self.cleaned_data['coAuthors']:
            CoAuthor.objects.create(name=coAuthor[0],
                                    surname=coAuthor[1],
                                    email=coAuthor[2],
                                    paper=self.instance)

    def get_coauthor_fields(self):
        for field_name in self.data:
            if field_name.startswith('coAuthor_'):
                yield self[field_name]


### PAPER FORMS

class PaperCreationForm(forms.ModelForm):
    description = forms.CharField(label='Krótki opis', widget=SummernoteWidget())

    class Meta:
        model = Paper
        fields = ['title', 'club', 'keywords', 'description']
        exclude = ['authors', 'reviewers']
        labels = dict(title=_('Tytuł'), club=_('Koło naukowe'), keywords=_('Słowa kluczowe'), description=_('Opis'))
        help_texts = dict(title=_('Tytuł'), keywords=_('Słowa oddzielone spacją'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = StudentClub.objects.exclude(acronym='Brak')


### REVIEW FORMS
class GradeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name}'


def get_grade_label(tag):
    grade = Grade.objects.filter(tag=tag).first()

    if grade is None:
        return 'None'
    return grade.get_tag_display_text()


class ReviewCreationForm(forms.ModelForm):
    text = forms.CharField(label='Treść recenzji', widget=SummernoteWidget())
    correspondence = GradeChoiceField(label=get_grade_label('correspondence'), required=True,
                                      queryset=Grade.objects.filter(tag='correspondence'))
    originality = GradeChoiceField(label=get_grade_label('originality'), required=True,
                                   queryset=Grade.objects.filter(tag='originality'))
    merits = GradeChoiceField(label=get_grade_label('merits'), required=True,
                              queryset=Grade.objects.filter(tag='merits'))
    presentation = GradeChoiceField(label=get_grade_label('presentation'), required=True,
                                    queryset=Grade.objects.filter(tag='presentation'))
    final_grade = GradeChoiceField(label=get_grade_label('final_grade'), required=True,
                                   queryset=Grade.objects.filter(tag='final_grade'))

    class Meta:
        model = Review
        fields = ['correspondence', 'originality', 'merits', 'presentation', 'final_grade', 'text']


class ReviewerChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        cnt = Paper.objects.filter(reviewers=obj).count()
        return f'{obj.first_name} {obj.last_name} ({cnt})'


class ReviewerAssignmentForm(forms.ModelForm):
    reviewers = ReviewerChoiceField(queryset=User.objects.filter(groups__name='reviewer'), label='Recenzent',
                                    required=False)

    class Meta:
        model = Paper
        fields = ['reviewers']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].widget.attrs = {'id': 'admin-assign-reviewers-select', 'size': '10',
                                                 'class': 'custom-select'}

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']
        if reviewers.count() > 2:
            raise forms.ValidationError('Nie można przypisać więcej niż dwóch recenzentów')
        return reviewers
