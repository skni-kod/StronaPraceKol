from django.http import HttpResponse
from django.views.generic import TemplateView
from django.http import JsonResponse


class AboutView(TemplateView):
    template_name = "messaging/messagebox.html"



def send_json(request):
    data = [{'name': 'Peter', 'email': 'peter@example.org'},
            {'name': 'Julia', 'email': 'julia@example.org'}]

    return JsonResponse(data, safe=False)
