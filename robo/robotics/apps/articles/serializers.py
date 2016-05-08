from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core import fields as core_fields
from core import mixins as core_mixins
from core import serializers as core_serializers
from core.exceptions import ServiceUnavailable
from common import fields as common_fields
from .models import Article, Publication, ImportedArticle, ArticleRevision
from .parser import ArticleParser


class ArticleSerializer(core_serializers.ModelSerializer):
    title = serializers.CharField(
        source='current_revision.title', required=False
    )
    content = serializers.CharField(
        source='current_revision.content', required=False
    )
    author = serializers.PrimaryKeyRelatedField(
        source='current_revision.author', read_only=True
    )
    '''
    picture = serializers.ImageField(
        source='current_revision.picture', required=False
    )'''
    class Meta:
        model = Article
        fields = ('id', 'task_brief', 'title', 'picture', 'content', 'author')
        read_only_fields = ('id', 'task_brief')

    @transaction.atomic
    def update(self, instance, validated_data):
        revision_data = validated_data.pop('current_revision')
        revision_kwargs = {}
        if 'title' in revision_data:
            revision_kwargs['title'] = revision_data.pop('title')
        if 'content' in revision_data:
            revision_kwargs['content'] = revision_data.pop('content')
        revision_kwargs['author'] = validated_data.pop('author')

        ret = super(ArticleSerializer, self).update(instance, validated_data)
        instance.save_revision(**revision_kwargs)
        return ret

class ArticlePictureSerializer(core_serializers.ModelSerializer):
    class Meta:
        model = ArticleRevision
        fields = ['picture']

class PublicationSerializer(core_mixins.DynamicFieldsSerializerMixin,
                            core_serializers.ReadOnlyModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = ('id', 'url', 'name', 'image', 'count')

    def get_count(self, publication):
        if hasattr(publication, 'id__count'):
            return publication.id__count
        return None


class ImportedArticleCreateSerializer(serializers.Serializer):
    url = serializers.URLField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.article = None
        super(ImportedArticleCreateSerializer, self).__init__(*args, **kwargs)

    def validate_url(self, url):
        existing_articles = ImportedArticle.objects.filter(user=self.user, url=url)
        if len(existing_articles):
            raise ValidationError('Article already exists')
        return url

    def validate(self, data):
        url = data.get('url')
        self.parse_article(url)
        return data

    def parse_article(self, url):
        self.article = ArticleParser(url)
        self.article.download()
        self.article.parse()
        if not self.article.is_parsed:
            raise ServiceUnavailable
        self.article.nlp()

    def create(self, validated_data):
        publication, created = Publication.objects.get_or_create(
            url=self.article.source_url
        )
        article = ImportedArticle.objects.create(
            user=validated_data.get('user'), url=validated_data.get('url'),
            title=self.article.title.strip(), content=self.article.text.strip(),
            publish_date=self.article.publish_date, publication=publication
        )
        article.meta_keywords = self.parse_article_keywords(self.article.meta_keywords)
        article.news_keywords = self.parse_article_keywords(self.article.news_keywords)
        article.nlp_keywords = self.parse_article_keywords(self.article.keywords)
        article.keywords = self.parse_article_keywords(
            self.article.meta_keywords + self.article.news_keywords
        )
        if self.article.has_top_image():
            article.image = self.article.top_image
        article.save()

        return article

    def parse_article_keywords(self, str_keywords):
        keywords = []
        for str_keyword in set(str_keywords):
            if len(str_keyword.strip()):
                try:
                    keywords.append(common_fields.KeywordField()
                                                 .to_internal_value(str_keyword))
                except ValidationError:
                    pass  # just ignore invalid keywords
        return keywords

    def update(self, validated_data):
        raise AssertionError(
            'update() is not allowed on %s' % self.__class__.__name__
        )


class ImportedArticleSerializer(core_serializers.ModelSerializer):
    keywords = core_fields.ListField(
        child=common_fields.KeywordField(),
        source='keywords.all', required=False, allow_blank=True
    )
    available_keywords = core_fields.ListField(
        child=common_fields.KeywordField(), read_only=True
    )
    publication = PublicationSerializer(read_only=True, exclude_fields=('count',))

    class Meta:
        model = ImportedArticle
        fields = ('id', 'user', 'url', 'title', 'content', 'image', 'keywords',
                  'available_keywords', 'publication', 'publish_date')
        read_only_fields = ('id', 'user', 'url')

    def create(self, validated_data):
        raise AssertionError(
            'create is not allowed in %s' % self.__class__.__name__
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        has_keywords = False
        if 'keywords' in validated_data:
            keywords = validated_data.pop('keywords')
            has_keywords = True
        instance = super(ImportedArticleSerializer, self).update(instance, validated_data)
        if has_keywords:
            instance.keywords = keywords.get('all')
            # workaround: instance.keywords is cached & will not be correct
            return ImportedArticle.objects.get(pk=instance.pk)
        return instance


#class EditorArticle(core_)
