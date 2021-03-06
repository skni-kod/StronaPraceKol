from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages


# forms
from .forms import UserRegisterForm
from .forms import RegisterForm, LoginForm, AddReferat

# for ListView classes
from django.views import generic

# models
from .models import Paper

# to use user system
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# before log-in

def index(request):
    if request.user.is_authenticated:
        return redirect('indexLog')

    contex = {'title':'index'}
    template = loader.get_template('index.html') # getting our template  
    return HttpResponse(template.render(contex)) # rendering the template in HttpResponse
    #return render(request,'index.html')
    
def logowanie(request):
    if request.user.is_authenticated:
        return redirect('indexLog')

    log = LoginForm()
    contex = {
                'form':log,
                'title':'logowanie',
             }
    return render(request,'logowanie.html',contex) 
    
def rejestracja(request):
    if request.user.is_authenticated:
        return redirect('indexLog')

    if request.method == 'POST':
        rej = UserRegisterForm(request.POST)
        if rej.is_valid():
            rej.save()
            username = rej.cleaned_data.get('username')
            messages.success(request,f'Konto zostało utworzone dla {username}')
            return redirect('logowanie')
    else:
        rej = UserRegisterForm()

    contex = {
                'form':rej,
                'title':'rejestracja',
             }
    return render(request,'rejestracja.html',contex)


def kontakt(request):
    if request.user.is_authenticated:
        return redirect('indexLog')

    contex = {
                'title':'kontakt',
             }
    return render(request,'kontakt.html',contex)

class LoginView(auth_views.LoginView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LoginView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'logowanie'
        return context
    pass
    
# after log-in

@ login_required # requires to be logged
def indexLog(request):
    contex = { 
                'imie':'smiercio',
                'title':'indexLog',
             }
    return render(request,'indexLog.html',contex)  
    

    


'''
def referaty(request):
    # get all data from database !!!!
    contex = {
             'imie':'smiercio',
             'ref_Title':'Mój pierwszy referat',
             'autors':'Smiercio',
             'status':'Zgłoszono',
             'title':'referaty',
           }
    return render(request,'referaty.html',contex)
'''
@ login_required # requires to be logged
def dodajReferat(request):

    if request.method == 'POST':
        ref = AddReferat(request.POST)
        if ref.is_valid():
            ref.save()
            return redirect('referaty')
    else:
        ref = AddReferat()

    name = { 'imie':'smiercio',
             'form':ref,
             'title':"dodajReferat",    
           }
    return render(request,'dodajReferat.html',name)
    

class ReferatListView(generic.ListView):
    model = Paper
    context_object_name = 'ref_List' # your own name for the list as a template variable
    template_name = 'referaty.html'

    def get_queryset(self): # to get all Papers
        #print(self.request.user.username)
        user = get_object_or_404(User,username=self.request.user.username)
        #print(self.kwargs.get('username'))
        return Paper.objects.filter(author=user)#.order_by('-add_date')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ReferatListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'referaty'
        context['imie'] = 'smiercio'
        return context


    




class LogoutView(auth_views.LogoutView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LogoutView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'wylogowany'
        return context
    pass

@ login_required # requires to be logged
def profile(request):
    contex = {
                'imie':'smiercio',
                'title':'profile',
             }
    return render(request,'profile.html',contex)