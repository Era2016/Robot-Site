from django.db import models
from django.db import DatabaseError
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.dispatch import receiver

from common.models import Keyword
from core.models import TimeStampedModel
from tasks.models import TaskBrief, task_brief_published


@python_2_unicode_compatible
class Article(TimeStampedModel):
    task_brief = models.OneToOneField(TaskBrief)

    # added by me as a terrible idea to make the image uploading works.
    picture = models.ImageField(upload_to='article_images', blank=True)
    def save_revision(self, **kwargs):
        author = kwargs.get('author')
        current_revision = self.current_revision
        is_new_author = not current_revision or author != current_revision.author
        if is_new_author:
            ArticleRevision.objects.create(article=self, **kwargs)
        else:
            for attr, value in kwargs.items():
                setattr(current_revision, attr, value)
            current_revision.save()

    @property
    def current_revision(self):
        try:
            return self.revisions.latest(field_name='modified')
        except ArticleRevision.DoesNotExist:
            return None

    @property
    def last_revision(self):
        try:
            return self.revisions.order_by('-modified')[1]
        except IndexError:
            return None

    def __str__(self):
        return self.task_brief.__str__()


@python_2_unicode_compatible
class ArticleRevision(TimeStampedModel):
    article = models.ForeignKey(Article, related_name='revisions')
    picture = models.ImageField(upload_to='article_images', blank=True)
    title = models.CharField(max_length=256, blank=True)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.article.__str__()


@python_2_unicode_compatible
class Publication(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=256, blank=True)
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.url


class ImporterArticleQuerySet(models.QuerySet):
    def prefetch_common_fields(self, exclude=None):
        related_fields = set([
            'keywords', 'meta_keywords', 'news_keywords',
            'nlp_keywords', 'publication'
        ])
        if exclude:
            related_fields = related_fields - set(exclude)
        return self.prefetch_related(*related_fields)


@python_2_unicode_compatible
class ImportedArticle(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='articles')
    url = models.URLField()
    title = models.CharField(max_length=256)
    content = models.TextField()
    image = models.URLField(blank=True)
    keywords = models.ManyToManyField(Keyword, related_name='articles')
    meta_keywords = models.ManyToManyField(Keyword, related_name='meta_articles')
    news_keywords = models.ManyToManyField(Keyword, related_name='news_articles')
    nlp_keywords = models.ManyToManyField(Keyword, related_name='nlp_articles')
    publish_date = models.DateTimeField(null=True, blank=True)
    publication = models.ForeignKey(Publication, related_name='articles')

    objects = ImporterArticleQuerySet.as_manager()

    @property
    def available_keywords(self):
        return (self.meta_keywords.all() |
                self.news_keywords.all() |
                self.nlp_keywords.all()).distinct()

    class Meta:
        unique_together = (('user', 'url'),)

    def __str__(self):
        return self.title


@receiver(task_brief_published, sender=TaskBrief)
def create_brief_article(sender, instance, **kwargs):
    if not hasattr(instance, 'article'):
        Article.objects.create(task_brief=instance)
