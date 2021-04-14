import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Row, HTML, ButtonHolder, Submit
from django import forms
from django.forms.models import inlineformset_factory, formset_factory
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from .custom_layout_object import Formset
from .models import *


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


class CoAuthorForm(forms.ModelForm):
    class Meta:
        model = CoAuthor
        fields = ['name', 'surname', 'email']
        labels = dict(name=_('Imię'), surname=_('Nazwisko'))

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


class PaperCreationForm(forms.ModelForm):
    description = forms.CharField(label='Krótki opis', widget=SummernoteWidget())
    coAuthors = Formset('coAuthors')

    class Meta:
        model = Paper
        fields = ['title', 'club', 'keywords', 'description']
        exclude = ['authors', 'reviewers']
        labels = dict(title=_('Tytuł'), club=_('Koło naukowe'), keywords=_('Słowa kluczowe'), description=_('Opis'))
        help_texts = dict(title=_('Tytuł referatu'),keywords=_('Pojedyncze słowa oddzielone spacją'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = StudentClub.objects.exclude(acronym='Brak')
        self.fields['club'].widget.attrs['class'] = 'custom-select'


class PaperEditForm(forms.ModelForm):
    description = forms.CharField(label='Krótki opis', widget=SummernoteWidget())

    class Meta:
        model = Paper
        fields = ['title', 'club', 'approved', 'keywords', 'description']
        exclude = ['authors', 'reviewers']
        labels = {
            'title': _('Tytuł'),
            'club': _('Koło'),
            'approved': _('Zatwierdź'),
            'keywords': _('Słowa kluczowe'),
            'description': _('Krótki opis'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('club'),
                Field('keywords'),
                Field('description'),

                HTML('<div class="row">'),
                Field('approved'),
                HTML('</div>'),

                HTML('<div class="row text-left ml-2">'),
                HTML('<span class="text-danger">( Pole to wskazuje recenzentowi, że referat jest gotowy )</span>'),
                HTML('</div>'),
                HTML('<hr>'),

                HTML('<div class="row>'),
                HTML('<div class="col>'),
                Fieldset('Współautorzy',
                         HTML('</div>'),
                         HTML('</div>'),

                         HTML("<br>"),
                         HTML('<div class="row offset-1">'),
                         Formset('coAuthors')),
                HTML('</div>'),

                HTML("<hr><br>"),
                ButtonHolder(Submit('submit', 'Zapisz zmiany')),
                HTML("<br><br>"),
            )
        )
        self.fields['club'].queryset = StudentClub.objects.exclude(acronym='Brak')


class ReviewCreationForm(forms.ModelForm):
    text = forms.CharField(label='Recenzja', widget=SummernoteWidget())

    class Meta:
        model = Review
        fields = ['text']
        labels = dict(text=_('Recenzja'))


class ReviewerAssignmentForm(forms.ModelForm):

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']
        if len(reviewers) > 2:
            raise forms.ValidationError('Nie możesz przypisać więcej niż 2 recenzentów')
        return reviewers

    class Meta:
        model = Paper
        fields = ['reviewers']
        labels = {'reviewers': _('Recenzenci'), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewers'].queryset = User.objects.filter(groups__name='reviewer')

