from django.conf.urls import include, url
from django.conf import settings

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers

from common import viewsets as common_viewsets
from users import viewsets as user_viewsets
from orgs import viewsets as org_viewsets
from tasks import viewsets as task_viewsets
from jobs import viewsets as job_viewsets
from articles import viewsets as article_viewsets
from ratings import viewsets as rating_viewsets


# Endpoints for REST APIs
router = routers.SimpleRouter()
router.register(r'users', user_viewsets.UserViewSet)
router.register(r'categories', common_viewsets.CategoryViewSet)
router.register(r'orgs', org_viewsets.OrganizationViewSet)
router.register(r'orguser', org_viewsets.OrganizationUserViewSet, base_name = 'orguser')
router.register(r'briefs', task_viewsets.TaskBriefViewSet, base_name='briefs')
router.register(r'jobs', job_viewsets.JobViewSet, base_name='jobs')


user_nested_router = routers.NestedSimpleRouter(
    router, r'users', lookup='user'
)
user_nested_router.register(
    r'notifications', user_viewsets.UserNotificationViewSet,
    base_name='notifications'
)
user_nested_router.register(
    r'orgs', org_viewsets.UserOrganizationViewSet,
    base_name='organizations'
)
user_nested_router.register(
    r'jobs', job_viewsets.UserJobViewSet, base_name='jobs'
)
user_nested_router.register(
    r'applications', job_viewsets.UserApplicationViewSet,
    base_name='applications'
)
user_nested_router.register(
    r'briefs', task_viewsets.UserTaskBriefViewSet,
    base_name='briefs'
)
user_nested_router.register(
    r'tasks', task_viewsets.UserTaskViewSet,
    base_name='tasks'
)
user_nested_router.register(
    r'articles', article_viewsets.UserImportedArticleViewSet,
    base_name='articles'
)
user_nested_router.register(
    r'publications', article_viewsets.UserPublicationViewSet,
    base_name='publications'
)
user_nested_router.register(
    r'ratings', rating_viewsets.UserRatingViewSet,
    base_name='ratings'
)

organization_nested_router = routers.NestedSimpleRouter(
    router, r'orgs', lookup='org'
)
organization_nested_router.register(
    r'briefs', task_viewsets.OrganizationTaskBriefViewSet,
    base_name='briefs'
)
organization_nested_router.register(
    r'tasks', task_viewsets.OrganizationTaskViewSet,
    base_name='tasks'
)


router.register(r'briefs', article_viewsets.BriefArticleViewSet)  # for detail_route
brief_nested_router = routers.NestedSimpleRouter(
    router, r'briefs', lookup='brief'
)
brief_nested_router.register(
    r'comments', task_viewsets.TaskBriefCommentViewSet, base_name='comments'
)
brief_nested_router.register(
    r'tasks', task_viewsets.BriefTaskViewSet, base_name='tasks'
)
brief_nested_router.register(
    r'ratings', rating_viewsets.TaskBriefRatingViewSet, base_name='ratings'
)

task_nested_router = routers.NestedSimpleRouter(
    brief_nested_router, r'tasks', lookup='task'
)
task_nested_router.register(
    r'jobs', job_viewsets.TaskJobViewSet, base_name='jobs'
)
task_nested_router.register(
    r'ratings', rating_viewsets.TaskRatingViewSet, base_name='ratings'
)

job_nested_router = routers.NestedSimpleRouter(router, r'jobs', lookup='job')
job_nested_router.register(
    r'applications', job_viewsets.JobApplicationViewSet, base_name='applications'
)


urlpatterns = format_suffix_patterns([
    #url('^payments/', include('payments.urls')),
    url(r'^', include(router.urls)),
    url(r'^', include(user_nested_router.urls)),
    url(r'^', include(organization_nested_router.urls)),
    url(r'^', include(brief_nested_router.urls)),
    url(r'^', include(task_nested_router.urls)),
    url(r'^', include(job_nested_router.urls)),
])


if settings.DEBUG:
    urlpatterns += format_suffix_patterns([
        url(r'^accounts/', include('rest_auth.urls')),
        url(r'^accounts/registration/', include('rest_auth.registration.urls')),
    ])
