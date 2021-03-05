from django.shortcuts import render

from django.template import loader

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

# forms 
from .forms import RegisterForm, LoginForm, AddReferat

# for ListView classes
from django.views import generic

# models

from .models import Referats    


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
    rej = RegisterForm()
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
    

    



def referaty(request):
    # get all data from database !!!!
    contex = { 'imie':'smiercio',
             'ref_Title':'Mój pierwszy referat',
             'autors':'Smiercio',
             'status':'Zgłoszono',
             'title':'referaty',
           }
    return render(request,'referaty.html',contex)
    
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
    model = Referats
    context_object_name = 'ref_List' # your own name for the list as a template variable
    template_name = 'referaty.html'
    
    
    