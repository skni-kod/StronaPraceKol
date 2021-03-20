from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

# forms
from .forms import UserRegisterForm, UserLoginForm, UserPasswordChangeForm
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



class IndexView(TemplateView):
    template_name = 'users/index.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'index'
        return context

#
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
        if(self.request.user.is_authenticated):
            return redirect('index')
        else:
            return render(request, self.template_name,context)

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
        if(self.request.user.is_authenticated):
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


class ProfileView(LoginRequiredMixin,TemplateView):
    login_url = 'login' # if user isn't logged, when redirect
    #redirect_field_name = 'login' # if user isn't logged, when redirect

    template_name = 'users/profile.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'profil'
        return context


class PasswordChangeView(LoginRequiredMixin,TemplateView):
    login_url = 'login' # if user isn't logged, when redirect
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
        return render(request, self.template_name,context)

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


class AccountDeleteView(LoginRequiredMixin,TemplateView):
    login_url = 'login' # if user isn't logged, when redirect

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