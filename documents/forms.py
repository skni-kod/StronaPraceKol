from django import forms
from crispy_forms.helper import FormHelper
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from .models import *


### FILE FORMS
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))


UploadFileFormSet = inlineformset_factory(Document, UploadedFile, form=FileUploadForm,
                                          fields=['file'], extra=1, can_delete=True)


# DOCUMENT FORMS
class DocumentCreationForm(forms.ModelForm):
    ready = forms.BooleanField(required=False, label=_('Gotowy do przesłania'))

    class Meta:
        model = Document
        fields = ['name', 'club', 'ready']
        exclude = ['author']
        labels = dict(name=_('Nazwa dokumentu'), club=_('Koło naukowe'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = StudentClub.objects.exclude(name='Brak')
