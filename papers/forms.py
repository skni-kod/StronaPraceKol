from django import forms
from .models import Paper, UploadedFile
from django.utils.translation import ugettext_lazy as _


class PaperCreationForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ['title', 'club', 'authors', 'keywords', 'description']
        labels = {
            'title': _('Tytuł'),
            'club': _('Koło'),
            'authors': _('Autorzy'),
            'keywords': _('Słowa kluczowe'),
            'description': _('Krótki opis'),
        }


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        labels = {'file': _('Pliki')}
        help_texts = {'file': _('Pliki możesz dodać później w zakładce edycji referatu')}
        widgets = {'file': forms.ClearableFileInput(attrs={'multiple': True})}
