from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.template import loader
# Create your views here.

def test(request):
    now = datetime.datetime.now()
    html = "It is now %s" % now
    template = loader.get_template('users/index.xhtml')
    context = {
        'html': html,
    }
    return HttpResponse(template.render(context, request))