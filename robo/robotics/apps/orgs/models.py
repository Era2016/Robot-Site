from django.db import models
from django.db import DatabaseError
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import TimeStampedModel


class OrganizationManager(models.Manager):
    def owned_by(self, user):
        return super(OrganizationManager, self).get_queryset().filter(
            organizationuser__user=user,
            organizationuser__user_role=OrganizationUser.USER_ROLE_OWNER
        )

    def has_member(self, user):
        return super(OrganizationManager, self).get_queryset().filter(
            organizationuser__user=user
        )


@python_2_unicode_compatible
class Organization(TimeStampedModel):
    name = models.CharField(max_length=100)
    website = models.URLField()
    description = models.TextField()
    industry = models.CharField(max_length=100, blank=True)
    picture = models.ImageField(upload_to='org_images', blank=True)
    year_founded = models.IntegerField()
    size = models.IntegerField()
    objects = OrganizationManager()

    def owner(self):
        try:
            return self.organizationuser_set.get(
                user_role=OrganizationUser.USER_ROLE_OWNER
            ).user
        except OrganizationUser.DoesNotExist:
            raise DatabaseError("Owner of organization not found")

    def set_owner(self, owner):
        try:
            organization_user_owner = self.organizationuser_set.get(
                user_role=OrganizationUser.USER_ROLE_OWNER
            )
            organization_user_owner.user = owner
        except OrganizationUser.DoesNotExist:
            OrganizationUser.objects.create(
                user=owner, organization=self,
                user_role=OrganizationUser.USER_ROLE_OWNER
            )

    def members(self):
        User = get_user_model()
        return User.objects.filter(
            organizationuser__organization=self
        )

    def has_member(self, user):
        return OrganizationUser.objects.filter(organization=self, user=user).count()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class OrganizationUser(TimeStampedModel):
    USER_ROLE_OWNER = 1
    USER_ROLE_EMPLOYEE = 2
    USER_ROLE_CHOICES = (
        (USER_ROLE_OWNER, 'Owner'),
        (USER_ROLE_EMPLOYEE, 'Employee'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    organization = models.ForeignKey(Organization)
    user_role = models.PositiveSmallIntegerField(choices=USER_ROLE_CHOICES)

    class Meta:
        unique_together = (('user', 'organization'),)

    def __str__(self):
        return self.organization.name
