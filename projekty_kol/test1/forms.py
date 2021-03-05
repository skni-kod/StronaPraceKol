from django import forms
from django_summernote.widgets import SummernoteWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']



class RegisterForm(forms.Form):
    login = forms.CharField(label="Login",max_length=50)
    password = forms.CharField(label="Hasło",max_length=50)
    re_password = forms.CharField(label="Powtórz hasło",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:58px;'}))
    name = forms.CharField(label="Imie",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-left:10px;'}))
    surname = forms.CharField(label="Nazwisko",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:25px;'}))
    institution = forms.CharField(label="Instytucja",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:25px;'}))
    title = forms.CharField(label="Tytuł / stopień naukowy / stanowisko",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:220px;'}))
    email = forms.CharField(label="E-mail",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:5px;'}))
    phone = forms.CharField(label="Telefon",max_length=50, widget=forms.TextInput(attrs={'style': 'margin-right:10px;'}))
    agreement1 = forms.BooleanField(label="Wyrażam zgodę na przetwarzanie danych osobowych dla celów publikacji", widget=forms.CheckboxInput(attrs={'style': 'margin-right:310px;'}))
    agreement2 = forms.BooleanField(label="Wysyłaj automatyczne powiadomienia systemu przez e-mail", widget=forms.CheckboxInput(attrs={'style': 'margin-right:210px;'}))

class LoginForm(forms.Form):
    login = forms.CharField(label="Login",max_length=50)
    password = forms.CharField(label="Hasło",max_length=50)
    
class AddReferat(forms.Form):
    '''
    CHOICES = (
        (1,("Mleko")),
        (2,("Woda")),
    )
    '''


    title = forms.CharField(label="Tytuł",max_length=150, widget=forms.TextInput(attrs={'size': '150'}))
    autors = forms.CharField(label="Autorzy",max_length=150, widget=forms.TextInput(attrs={'size': '150'}))
    organization = forms.CharField(label="Koło naukowe lub organizacja studencka",max_length=150, widget=forms.TextInput(attrs={'size': '150'}))
    summary = forms.CharField(label="Streszczenie",widget=SummernoteWidget())
    #select = forms.ChoiceField(label="Wybierz",choices=CHOICES)