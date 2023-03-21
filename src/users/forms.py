from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from .models import UserDetail


class UserRegisterForm(UserCreationForm):
    error_messages = {
        'This password is too common.': _('Podane hasło jest zbyt często wykorzystywane'),
        'password_mismatch': _('Podane hasła nie są identyczne'),
    }
    email = forms.EmailField()
    password1 = forms.CharField(label=_("Hasło"),
                                widget=forms.PasswordInput,
                                help_text=_("<ul class='text-left'>"
                                            "<li>Hasło musi zawierać conajmniej 8 znaków</li>"
                                            "<li>Hasło musi być oryginalne</li>"
                                            "<li>Hasło nie może być skojarzone z pozostałymi danymi</li>"
                                            "<li>Hasło nie może składać się tylko z cyfr</li>"
                                            "</ul>"
                                            ),
                                )

    password2 = forms.CharField(label=_("Powtórz hasło"),
                                widget=forms.PasswordInput)
    city = forms.CharField(max_length=100, label=_("Miasto"), validators=[RegexValidator("^[A-ZŁŚĆŻŹ][a-ząćęłńóśźż]+(?:[\s-][A-ZŁŚĆŻŹ][a-ząćęłńóśźż]+)*$", "Wprowadź poprawne miasto.")])
    street = forms.CharField(max_length=100, label=_("Ulica"), validators=[RegexValidator("^[A-ZŁŚĆŻŹ][a-ząćęłńóśźż]+(?:[\s-][A-ZŁŚĆŻŹ]?[a-ząćęłńóśźż]+)*$","Wprowadź poprawną ulicę.")])
    number = forms.CharField(max_length=100, label=_("Numer budynku/mieszkania"), validators=[RegexValidator("^[0-9]+[A-Z]?(\/[0-9]+[A-Z]?)?$", "Wprowadź poprawny numer.")])

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        for field in self.Meta.required:
            self.fields[field].required = True
    
    def save(self, commit: bool = ...):
        user = super().save(commit)
        UserDetail.objects.create(user=user, city=self.cleaned_data['city'], street=self.cleaned_data['street'], number=self.cleaned_data['number'])
        return user

    class Meta:
        model = User
        help_texts = {'username': _('Maksymalnie 150 znaków, dopuszczone znaki: litery, cyfry oraz @/./+/-/_')}
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'city', 'street', 'number']
        labels = {
            'first_name': _('Imię'),
            'last_name': _('Nazwisko'),
            'username': _('Login'),
            'email': _('Adres email'),
        }

        required = (
            'first_name',
            'last_name',
            'username'
        )


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Login'), max_length=254)
    password = forms.CharField(label=_("Hasło"), widget=forms.PasswordInput)


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Stare hasło"),
                                   widget=forms.PasswordInput)

    new_password1 = forms.CharField(label=_("Nowe hasło"),
                                    widget=forms.PasswordInput,
                                    help_text=_("<ul class='text-left'>"
                                                "<li>Hasło musi zawierać conajmniej 8 znaków</li>"
                                                "<li>Hasło musi być oryginalne</li>"
                                                "<li>Hasło nie może być skojarzone z pozostałymi danymi</li>"
                                                "<li>Hasło nie może składać się tylko z cyfr</li>"
                                                "</ul>"
                                                ),
                                    )

    new_password2 = forms.CharField(label=_("Powtórz nowe hasło"),
                                    widget=forms.PasswordInput)
