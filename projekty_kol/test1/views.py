from django.shortcuts import render

from django.template import loader

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

# forms 
from .forms import RegisterForm, LoginForm, AddReferat

def index(request):
    template = loader.get_template('index.html') # getting our template  
    return HttpResponse(template.render()) # rendering the template in HttpResponse
    #return render(request,'index.html')
    
def indexLog(request):
    name = { 'imie':'smiercio'}
    return render(request,'indexLog.html',name)  
    
def logowanie(request):
    log = LoginForm()
    return render(request,'logowanie.html',{'form':log})
    

def rejestracja(request):
    rej = RegisterForm()
    return render(request,'rejestracja.html',{'form':rej})

def kontakt(request):
    return render(request,'kontakt.html')
    
def referaty(request):
    # get all data from database !!!!
    name = { 'imie':'smiercio',
             'title':'Mój pierwszy referat',
             'autors':'Smiercio',
             'status':'Zgłoszono',
    
    
    
           }
    return render(request,'referaty.html',name)
    
def dodajReferat(request):
    ref = AddReferat(request.POST or None);
    name = { 'imie':'smiercio',
             'form':ref,
             'title':"",
            
           }
    title = "nope"
             
    if (ref.is_valid()):
    
        # getting data from form fields
        title = ref.cleaned_data.get("title")
        #print(title)
        # redirect
        template = loader.get_template('referaty.html') # getting our template  
        return HttpResponseRedirect('referaty')
        
    print(title)
    return render(request,'dodajReferat.html',name)
    
    
    
    