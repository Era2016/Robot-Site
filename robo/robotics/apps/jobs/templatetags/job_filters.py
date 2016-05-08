from django import template
from django.contrib.auth import get_user_model

from jobs.models import Job, JobApplication

User = get_user_model()

register = template.Library()


@register.filter
def can_apply(user, job):
    if not isinstance(user, User) and not isinstance(job, Job):
        return False

    return JobApplication.objects.filter(job=job, applicant=user).count() == 0


@register.filter
def job_application_date(user, job):
    if not isinstance(user, User) and not isinstance(job, Job):
        return None
    try:
        return JobApplication.objects.get(job=job, applicant=user).created
    except:
        return None
