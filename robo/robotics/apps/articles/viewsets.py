from django.db.models import Count
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
import rest_condition

from core import mixins as core_mixins
from tasks.viewsets import TaskBriefSubViewSetMixin
from users.viewsets import UserSubViewSetMixin
from .models import Article, Publication, ImportedArticle
from .serializers import (
    ArticleSerializer, PublicationSerializer,
    ImportedArticleSerializer, ImportedArticleCreateSerializer,
    ArticlePictureSerializer
)
from . import permissions as article_permissions


class BriefArticleViewSet(TaskBriefSubViewSetMixin,
                          ModelViewSet,
                          GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        rest_condition.Or(article_permissions.IsOneOfBriefAssignees,
                          article_permissions.IsInBriefOrganization),
        article_permissions.IsBriefCurrentAssigneeOrReadOnly,
    )

    def get_article(self):
        try:
            article = self.get_brief().article
            self.check_object_permissions(self.request, article)
            return article
        except Article.DoesNotExist:
            raise NotFound

    @detail_route(methods=['GET', 'PUT'])
    def article(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self._retrieve(request, *args, **kwargs)
        else:
            return self._update(request, *args, **kwargs)

    def _retrieve(self, request, *args, **kwargs):
        # '_retrieve' instead of 'retrieve' since this is private method
        # 'retrieve' will be exposed to public API by rest_framework
        instance = self.get_article()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _update(self, request, *args, **kwargs):
        # '_update' instead of 'update' since this is private method
        # 'update' will be exposed to public API by rest_framework
        instance = self.get_article()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data)

    @detail_route(methods=['POST'], url_path='set-picture')
    def update_profile_picture(self, request, *args, **kwargs):
        article = self.get_object()
        picture_serializer = ArticlePictureSerializer(
            article, data=request.data
        )
        picture_serializer.is_valid(raise_exception=True)
        picture_serializer.save()
        return Response(picture_serializer.data)

    @detail_route(methods=['GET'], url_path='get-picture')
    def get_profile_picture(self, request, *args, **kwargs):
        instance = self.get_article()
        serializer = ArticlePictureSerializer.get_serializer(instance)
        return Response(serializer.data)


class UserImportedArticleViewSet(UserSubViewSetMixin,
                                 core_mixins.MultiSerializerViewSetMixin,
                                 core_mixins.MultiSerializerCreateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    serializer_class = ImportedArticleSerializer
    serializer_action_classes = {
        'create': ImportedArticleCreateSerializer
    }
    permission_classes = (
        permissions.IsAuthenticated,
        article_permissions.IsUserOrReadOnly
    )
    user_permission_exempt_actions = ('list', 'retrieve')

    def get_queryset(self):
        return (ImportedArticle.objects.filter(user=self.get_user())
                                       .prefetch_common_fields()
                                       .order_by('-created'))

    def get_serializer(self, *args, **kwargs):
        action = kwargs.get('action', None) or self.action
        if action == 'create':
            kwargs.update({'user': self.request.user})
        return super(UserImportedArticleViewSet, self).get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserPublicationViewSet(UserSubViewSetMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    serializer_class = PublicationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        article_permissions.IsUserOrReadOnly
    )
    user_permission_exempt_actions = ('list',)

    def get_queryset(self):
        return (Publication.objects.filter(articles__user=self.get_user())
                                   .annotate(Count('id'))
                                   .order_by('-id__count'))
