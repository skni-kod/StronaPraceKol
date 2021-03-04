from django.shortcuts import render

from django.template import loader

# Create your views here.
from django.http import HttpResponse

# forms 
from .forms import RegisterForm, LoginForm

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
    return render(request,'referaty.html')