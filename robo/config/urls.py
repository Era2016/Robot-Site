# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from notifications.models import Notification

from . import api

admin.autodiscover()

admin.site.unregister(EmailConfirmation)
admin.site.unregister(EmailAddress)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(Notification)
admin.site.unregister(Group)
admin.site.unregister(Site)


urlpatterns = [
    # Django Admin
    # url(r'^admin/', include(admin.site.urls)),

    # User authentication
    url(r'^accounts/', include('allauth.urls')),

    # Invitations
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),

    url(
        r'^$',
        TemplateView.as_view(template_name='pages/index.html'),
        name='index'
    ),
    # url(r'^users/', include('users.urls', namespace='users')),
    # url(r'^orgs/', include('orgs.urls', namespace='orgs')),
    # url(r'^jobs/', TemplateView.as_view(template_name='jobs.html')),

    url(r'^api/v1/', include(api, namespace="api")),

    # Angular App
    # url(r'^app/', TemplateView.as_view(template_name='angular/index.html'),
    #    name='ng-index')

    url(
        r'^app/',
        login_required(TemplateView.as_view(template_name='index.html')),
        name='ng-index'
    )

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', 'django.views.defaults.bad_request'),
        url(r'^403/$', 'django.views.defaults.permission_denied'),
        url(r'^404/$', 'django.views.defaults.page_not_found'),
        url(r'^500/$', 'django.views.defaults.server_error'),
    ]
