from django.shortcuts import render

from django.template import loader
# Create your views here.

from django.http import HttpResponse

def index(request):
    template = loader.get_template('index.html') # getting our template  
    return HttpResponse(template.render()) # rendering the template in HttpResponse
    #return render(request,'index.html')
    
    
    
def logowanie(request):
    return render(request,'logowanie.html')
    

def rejestracja(request):
    return render(request,'rejestracja.html')

def kontakt(request):
    return render(request,'kontakt.html')