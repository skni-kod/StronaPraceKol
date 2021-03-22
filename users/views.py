from django.shortcuts import render, redirect
from django.http import HttpResponse

from StronaProjektyKol.settings import SITE_NAME, SITE_DOMAIN, SITE_ADMIN_MAIL

# forms
from .forms import UserRegisterForm, UserLoginForm, UserPasswordChangeForm
from .forms import UserRegisterForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

# to use user system
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

# for ListView classes
from django.views import generic

# for TemplateView classes
from django.views.generic import TemplateView

# for login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django import template

from django.contrib import messages


class IndexView(TemplateView):
    template_name = 'users/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'index'
        return context


#
# before log-in
#
#

class ContactView(TemplateView):
    template_name = 'users/contact.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ContactView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'kontakt'
        return context


class RegisterView(TemplateView):
    template_name = 'users/register.html'

    def get(self, request, *args, **kwargs):
        rej = UserRegisterForm()
        # Call the base implementation first to get the context
        context = super(RegisterView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context = {
            'form': rej,
            'title': 'rejestracja',
        }
        # Check if user is already logged
        if (self.request.user.is_authenticated):
            return redirect('index')
        else:
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            rej = UserRegisterForm(self.request.POST)
            if rej.is_valid():
                rej.save()
                username = rej.cleaned_data.get('username')
                messages.success(self.request, f'Konto zostało utworzone dla {username}')
                return redirect('login')
        else:
            rej = UserRegisterForm()
        return render(request, self.template_name, {'form': rej})


class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        # Check if user is already logged
        if (self.request.user.is_authenticated):
            form = UserLoginForm()
            return redirect('index')
        else:
            form = UserLoginForm()
            context = {
                'form': form,
                'title': 'logowanie',
            }
            return render(request, self.template_name, context)


#
#
# after log-in
#
#

class LogoutView(auth_views.LogoutView):
    template_name = 'users/logout.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LogoutView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'wylogowany'
        return context

    pass


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, when redirect
    # redirect_field_name = 'login' # if user isn't logged, when redirect

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'profil'
        return context


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, when redirect
    template_name = 'users/passwordChange.html'

    def get(self, request, *args, **kwargs):
        password_change = UserPasswordChangeForm(self.request.user)
        # Call the base implementation first to get the context
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context = {
            'form': password_change,
            'title': 'zmiana hasła',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            password_change = UserPasswordChangeForm(self.request.user, self.request.POST)
            if password_change.is_valid():
                password_change.save()
                messages.success(self.request, f'Hasło zostało zmienione')
                return redirect('profile')
        else:
            password_change = UserPasswordChangeForm(self.request.user)
        return render(request, self.template_name, {'form': password_change})


class AccountDeleteView(LoginRequiredMixin, TemplateView):
    login_url = 'login'  # if user isn't logged, when redirect

    template_name = 'users/accountDelete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AccountDeleteView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'usuwanie konta'
        return context

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            request.user.delete()
            messages.success(self.request, f'Konto zostało usunięte')
            return redirect('index')

        return render(request, self.template_name)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                user = associated_users.first()
                subject = "Prace Kół Naukowych - Odzyskiwanie hasła"
                plaintext = template.loader.get_template('registration/password_reset_email.txt')
                htmltemp = template.loader.get_template('registration/password_reset_email.html')
                c = {
                    "email": user.email,
                    'domain': SITE_DOMAIN,
                    'site_name': SITE_NAME,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                text_content = plaintext.render(c)
                html_content = htmltemp.render(c)
                try:
                    msg = EmailMultiAlternatives(subject, text_content, SITE_ADMIN_MAIL, [user.email],
                                                 headers={'Reply-To': SITE_ADMIN_MAIL})
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect('password_reset_done')
            else:
                messages.add_message(request, messages.WARNING, 'Nie znaleziono konta powiązanego z podanym adresem')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset_form.html",
              context={"form": password_reset_form})
