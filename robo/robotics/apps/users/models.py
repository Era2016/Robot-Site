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
    code = models.TextField(blank=True, default='0')
    level = models.TextField(blank=True, default='1')
    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class UserRole(TimeStampedModel):
    user = models.OneToOneField(User, primary_key=True)
    role = models.PositiveSmallIntegerField(choices=enums.UserRole.choices())
    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class UserInformation(TimeStampedModel):
    # this is to migrate the origional information from the origional
    # server
    # however the following things should be noticed when using
    # this table:
    '''
    id field is built in, and is incremental in the background. I am not sure if
    the id field is useful but I'm gonna omit that column

    TimeStampedModel automatically offers you information about the user action
    in the timeline. 

    Notice that this table is not connected to the formal definition of the user
    class which is used in this project. 
    '''
    name = models.TextField(max_length = 100, blank=True)
    gender = models.TextField(max_length = 100, blank=True)
    title = models.TextField(max_length = 100, blank=True)
    email = models.TextField(max_length = 120, blank=True)
    telephone = models.TextField(max_length = 100, blank=True)
    organization = models.TextField(max_length = 256, blank=True)
    designation = models.TextField(max_length = 128, blank=True)
    city = models.TextField(max_length = 100, blank=True)
    country = models.TextField(max_length = 100, blank=True)
    platform = models.TextField(max_length = 100, blank=True)
    purpose = models.TextField(blank=True)
    competition_date_from = models.DateTimeField(blank=True)
    competition_date_to = models.DateTimeField(blank=True)
    code = models.TextField(max_length = 100, blank=True)
    valid = models.TextField(max_length = 100, blank=True)
    mentor_name = models.TextField(max_length = 128, blank=True)
    mentor_email = models.TextField(max_length = 128, blank=True)
    activation_count = models.IntegerField(blank=True, default=0)
    activation_max = models.IntegerField(blank=True, default=1)
    submit_time = models.DateTimeField(blank=True)
    expiry_date = models.DateTimeField(blank=True)
    def __str__(self):
        return self.name

    


# Automatically create a profile for new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserCode.objects.create(user=instance)
