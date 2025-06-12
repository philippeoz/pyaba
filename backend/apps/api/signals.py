from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def use_email_as_username(sender, instance, **kwargs):
    instance.username = instance.email
