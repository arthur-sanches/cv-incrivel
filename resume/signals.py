from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Resume


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_resume(sender, instance, created, **kwargs):
    if created:
        Resume.objects.create(user=instance)
