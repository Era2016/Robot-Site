from django.conf.urls import include, url
from django.conf import settings

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers

from common import viewsets as common_viewsets
from users import viewsets as user_viewsets
from orgs import viewsets as org_viewsets


# Endpoints for REST APIs
router = routers.SimpleRouter()
router.register(r'users', user_viewsets.UserViewSet)
router.register(r'categories', common_viewsets.CategoryViewSet)
router.register(r'orgs', org_viewsets.OrganizationViewSet)
router.register(r'orguser', org_viewsets.OrganizationUserViewSet, base_name = 'orguser')

user_nested_router = routers.NestedSimpleRouter(
    router, r'users', lookup='user'
)
user_nested_router.register(
    r'notifications', user_viewsets.UserNotificationViewSet,
    base_name='notifications'
)
user_nested_router.register(
    r'code', user_viewsets.UserCodeViewSet,
    base_name='code'
)
user_nested_router.register(
    r'orgs', org_viewsets.UserOrganizationViewSet,
    base_name='organizations'
)


organization_nested_router = routers.NestedSimpleRouter(
    router, r'orgs', lookup='org'
)

urlpatterns = format_suffix_patterns([
    #url('^payments/', include('payments.urls')),
    url(r'^', include(router.urls)),
    url(r'^', include(user_nested_router.urls)),
    url(r'^', include(organization_nested_router.urls)),
])


if settings.DEBUG:
    urlpatterns += format_suffix_patterns([
        url(r'^accounts/', include('rest_auth.urls')),
        url(r'^accounts/registration/', include('rest_auth.registration.urls')),
    ])
