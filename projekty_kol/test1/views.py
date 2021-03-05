from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .forms import UserRegisterForm

# forms 
from .forms import RegisterForm, LoginForm, AddReferat

# for ListView classes
from django.views import generic

# models
from .models import Paper

# to use user system
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views



# before log-in

def index(request):
    contex = {'title':'index'}
    template = loader.get_template('index.html') # getting our template  
    return HttpResponse(template.render(contex)) # rendering the template in HttpResponse
    #return render(request,'index.html')
    
def logowanie(request):
    log = LoginForm()
    contex = {
                'form':log,
                'title':'logowanie',
             }
    return render(request,'logowanie.html',contex) 
    
def rejestracja(request):
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
    contex = {
                'title':'kontakt',
             }
    return render(request,'kontakt.html',contex)
    
    
    
# after log-in

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
def dodajReferat(request):
    ref = AddReferat(request.POST or None);
    name = { 'imie':'smiercio',
             'form':ref,
             'title':"dodajReferat",    
           }
    ref_Title = "nope"
             
    if (ref.is_valid()):
    
        # getting data from form fields
        ref_Title = ref.cleaned_data.get("title")
        #print(title)
        # redirect
        template = loader.get_template('referaty.html') # getting our template  
        return HttpResponseRedirect('referaty')
        
    print(ref_Title)
    return render(request,'dodajReferat.html',name)
    

class ReferatListView(generic.ListView):
    model = Paper
    context_object_name = 'ref_List' # your own name for the list as a template variable
    template_name = 'referaty.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ReferatListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'referaty'
        context['imie'] = 'smiercio'
        return context
    

class LoginView(auth_views.LoginView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LoginView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'logowanie'
        return context
    pass


class LogoutView(auth_views.LogoutView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LogoutView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['title'] = 'wylogowany'
        return context
    pass