from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

# forms
from .forms import UserRegisterForm
from django.contrib import messages

# to use user system
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


# for ListView classes
from django.views import generic

# for TemplateView classes
from django.views.generic import TemplateView


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

'''
def index(request):
    template = loader.get_template('users/index.html')
    context = {
        'title': 'index',
    }
    return HttpResponse(template.render(context, request))
'''

#
#
# before log-in
#
#

'''
def contact(request):
    template = loader.get_template('users/contact.html')
    context = {
                'title':'kontakt',
             }
    return render(request,'users/contact.html',context)
'''

class ContactView(TemplateView):
    template_name = 'users/contact.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ContactView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'index'
        return context


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        rej = UserRegisterForm(request.POST)
        if rej.is_valid():
            rej.save()
            username = rej.cleaned_data.get('username')
            messages.success(request,f'Konto zostało utworzone dla {username}')
            return redirect('login')
    else:
        rej = UserRegisterForm()
    contex = {
                'form':rej,
                'title':'rejestracja',
             }
    return render(request,'users/register.html',contex)



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

    '''
    def get_context_data(self, **kwargs):
        rej = UserRegisterForm()
        # Call the base implementation first to get the context
        context = super(RegisterView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'index'
        context['form'] = rej
        return context
    '''

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST': # cant send to database / HTTP ERROR 405
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
            form = self.form_class(initial=self.initial)
            return redirect('index')
        else:
            form = self.form_class(initial=self.initial)
            return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LoginView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'logowanie'
        return context
    pass


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

'''
@login_required
# to use this you need #LOGIN_URL = 'login' in settings.py
def profile(request):
    contex = {
                'imie':'smiercio',
                'title':'profil',
             }
    return render(request,'users/profile.html',contex)
'''
class ProfileView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    #redirect_field_name = 'login' # if user isn't logged, when redirect

    template_name = 'users/profile.html'
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'index'
        return context