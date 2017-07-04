from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=Fixture)
def check_fixture(sender, instance, **kwargs):
    print(instance)
    print("checked")


@receiver(pre_save, sender=Bet)
def check_fixture(sender, instance, **kwargs):
    print(instance)
    print("checked")