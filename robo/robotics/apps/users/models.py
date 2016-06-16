from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from core.models import TimeStampedModel
from common.models import Keyword
from common import enums
# users app should not really know about articles app
# from articles.models import Publication


@python_2_unicode_compatible
class User(AbstractUser):

    def name(self):
        return (self.first_name + ' ' + self.last_name) or self.username

    def __str__(self):
        return self.username


@python_2_unicode_compatible
class UserProfile(TimeStampedModel):
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female")
    )

    user = models.OneToOneField(User, primary_key=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='user_images', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

@python_2_unicode_compatible
class UserCode(TimeStampedModel):
    user = models.OneToOneField(User, primary_key=True)
    code = models.TextField(blank=True)
    level = models.TextField(blank=True, default='1')
    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class UserRole(TimeStampedModel):
    user = models.OneToOneField(User, primary_key=True)
    role = models.PositiveSmallIntegerField(choices=enums.UserRole.choices())
    def __str__(self):
        return self.user.username


# Automatically create a profile for new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserCode.objects.create(user=instance)
