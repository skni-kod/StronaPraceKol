from django import template
from django.contrib.auth.models import Group
from django.template.loader import render_to_string

register = template.Library()


@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    """
    Checks if given user is in a group of the given name
    :param user: User object
    :param group_name: string (name of a group)
    :return: boolean
    """
    try:
        group = Group.objects.get(name=group_name)
        if group in user.groups.all():
            return True
    except:
        return False
    return False


@register.filter(name='already_reviewed')
def already_reviewed(user, paper):
    """
    Checks if given user has already reviewed given paper
    :param user: User object
    :param paper: Paper object
    :return: boolean
    """
    reviews = paper.review_set.all()
    for review in reviews:
        if review.author == user:
            return True
    return False


@register.filter(name='get_user_review_id')
def get_user_review_id(user, paper):
    """
    Returns id of a review written by given user for the given paper
    :param user: User object
    :param paper: Paper object
    :return: integer (id of a review)
    """
    for review in paper.review_set.all():
        if review.author == user:
            return review.pk


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


@register.filter(name='in_tag')
def in_tag(things, tag):
    return things.filter(tag=tag)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.simple_tag(name='print_paper')
def print_paper(paper, link, user):
    context = dict()
    context['paper'] = paper
    context['link'] = link
    context['user'] = user
    return render_to_string('papers/paper_list_element.html', context=context)
