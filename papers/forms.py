import re

from crispy_forms.helper import FormHelper
from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django_summernote.fields import SummernoteTextFormField
from django.core.exceptions import ValidationError

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

UploadFileFormSet = inlineformset_factory(Paper, UploadedFile, form=FileUploadForm,
                                          fields=['file'], extra=1, can_delete=True)


### CO AUTHOR FORMS
class CoAuthorForm(forms.ModelForm):
    class Meta:
        model = CoAuthor
        fields = ['name', 'surname', 'email', 'percentage']
        labels = {
            'name': _('Imię'),
            'surname': _('Nazwisko'),
            'percentage': _('Procent udziału')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        formtag_prefix = re.sub('-[0-9]+$', '', kwargs.get('prefix', ''))

class CoAuthorInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            p = form.cleaned_data.get("percentage") or 0
            

            if p < 0:
                raise ValidationError(_("Procentowy udział wspołautora nie może być ujemny."))
            
            total += p

        
        # Co-authors must take less than 100% so author has at least 0.01%
        if total >= 99.99:
            raise ValidationError(_("Suma procentów wspołautorów musi być mniejsza niż 100, aby autor miał dodatni udział (teraz %(val)s)."),
                                  params={"val": round(total, 2)},)

    #calculate author percentage based on co-author percentages.
    def calculate_author_percentage(self):
        co_author_total = 0
        if self.is_valid():
            for co_author_form in self.forms:
                if not co_author_form.cleaned_data.get("DELETE"):
                    percentage = co_author_form.cleaned_data.get("percentage") or 0
                    co_author_total += percentage
        return round(100 - co_author_total, 2)

CoAuthorFormSet = inlineformset_factory(Paper, CoAuthor, form=CoAuthorForm,formset=CoAuthorInlineFormSet,
                                        fields=['name', 'surname', 'email', 'percentage'], extra=1,
                                        can_delete=True)


### PAPER FORMS
class PaperCreationForm(forms.ModelForm):
    description = SummernoteTextFormField(label='Krótkie streszczenie')
    approved = forms.BooleanField(required=False,label=_('Gotowy do recenzji'))

    class Meta:
        model = Paper
        fields = ['title', 'club', 'keywords', 'description', 'approved']
        exclude = ['author', 'reviewers', 'statement']
        labels = dict(title=_('Tytuł'), club=_('Koło naukowe'), keywords=_('Słowa kluczowe'), description=_('Opis'))
        help_texts = dict(title=_('Tytuł'), keywords=_('Słowa kluczowe'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club'].queryset = StudentClub.objects.exclude(name='Brak')


### REVIEW FORMS
class GradeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name}'


def get_grade_label(tag):
    try:
        grade = Grade.objects.filter(tag=tag).first()
        if grade is None:
            return 'None'
        return grade.get_tag_display_text()
    except:
        return 'None'


class ReviewCreationForm(forms.ModelForm):
    text = SummernoteTextFormField(label='Treść recenzji')
    correspondence = GradeChoiceField(label=get_grade_label('correspondence'),
                                      queryset=Grade.objects.filter(tag='correspondence'))
    originality = GradeChoiceField(label=get_grade_label('originality'),
                                   queryset=Grade.objects.filter(tag='originality'))
    merits = GradeChoiceField(label=get_grade_label('merits'),
                              queryset=Grade.objects.filter(tag='merits'))
    final_grade = GradeChoiceField(label=get_grade_label('final_grade'),
                                   queryset=Grade.objects.filter(tag='final_grade'))
    presentation = GradeChoiceField(label=get_grade_label('presentation'),
                                    queryset=Grade.objects.filter(tag='presentation'))

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


### AUTHOR DATA FORMS
class AuthorPersonalDataForm(forms.Form):
    """Form for collecting author personal data (name, surname, PESEL, address)"""
    name = forms.CharField(
        max_length=100,
        label='Imię',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    surname = forms.CharField(
        max_length=100,
        label='Nazwisko',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pesel = forms.CharField(
        max_length=11,
        label='PESEL',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '11 cyfr'
        })
    )
    address = forms.CharField(
        max_length=255,
        label='Adres zamieszkania',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'ulica, numer, miasto, kod'})
    )


AuthorPersonalDataFormSet = forms.formset_factory(AuthorPersonalDataForm, extra=0)