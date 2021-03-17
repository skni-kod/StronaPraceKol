from django import forms
from .models import Paper, UploadedFile, CoAuthor, Review
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Row, HTML, ButtonHolder, Submit
from .custom_layout_object import Formset
import re


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


class PaperCreationForm(forms.ModelForm):

    class Meta:
        model = Paper
        fields = ['title', 'club', 'keywords', 'description']
        exclude = ['authors']
        labels = {
            'title': _('Tytuł'),
            'club': _('Koło'),
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
                Fieldset('Dodaj współautorów',
                         Formset('coAuthors')),
                HTML("<br><br><br>"),
                Field('keywords'),
                Field('description'),
                Fieldset('Dodaj pliki',
                         Formset('files', 'papers/upload_files_formset.html')),
                ButtonHolder(Submit('submit', 'Dodaj')),
            )
        )


class PaperEditForm(forms.ModelForm):

    class Meta:
        model = Paper
        fields = ['title', 'club', 'approved', 'keywords', 'description']
        exclude = ['authors']
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
                Field('approved'),
                Fieldset('Współautorzy',
                         Formset('coAuthors')),
                HTML("<br><br><br>"),
                Field('keywords'),
                Field('description'),
                ButtonHolder(Submit('submit', 'Zapisz zmiany')),
            )
        )


class ReviewCreationForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['text']
        labels = {
            'text': _('Recenzja'),
        }

