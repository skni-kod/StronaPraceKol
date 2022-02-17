from django import template
from django.contrib.auth.models import Group
from django.template.loader import render_to_string

register = template.Library()


@register.filter(name='slice_page')
def slice_page(path):
    """
    Function removes proper amount of characters from the end of a given path,
    so that it can later be appended in an altered form
    :param path: string (url path with filter and page parameters)
    :return: string (sliced path)
    """
    index = len(path) - 7
    if path.count('&page=') >= 1:
        while True:
            tmp = path.find('&page=', index)
            if tmp != -1:
                break
            else:
                index -= 1
        return path[:-(len(path) - index)]
    else:
        return path

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

@register.simple_tag(name='print_document')
def print_document(document, link, user):
    context = dict()
    context['document'] = document
    context['link'] = link
    context['user'] = user
    return render_to_string('documents/document_list_element.html', context=context)
