from django.db.models.signals import post_save
from .models import UserDetail
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    """
    Creates UserDetails object when new user is created
    :param sender: UserObject
    :param instance: User object that was created
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        UserDetail.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_details(sender, instance, **kwargs):
    instance.userdetail.save()
