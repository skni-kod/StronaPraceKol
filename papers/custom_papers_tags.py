from django import template
from django.contrib.auth.models import User, Group


register = template.Library()


@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    group = Group.objects.get(name=group_name)
    if group in user.groups.all():
        return True
    return False


@register.filter(name='already_reviewed')
def already_reviewed(user, paper):
    reviews = paper.review_set.all()
    for review in reviews:
        if review.author == user:
            return True
    return False


@register.filter(name='get_user_review_id')
def get_user_review_id(user, paper):
    for review in paper.review_set.all():
        if review.author == user:
            return review.pk