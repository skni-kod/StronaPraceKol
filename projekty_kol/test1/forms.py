from django import forms

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