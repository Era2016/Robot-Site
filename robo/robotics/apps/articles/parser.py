import re

from newspaper import Article as NewspaperArticle


class ArticleParser(NewspaperArticle):

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        # workaround: newspaper doesn't work with https
        # so replace all https with http
        self._url = value.replace('https://', 'http://')

    @property
    def news_keywords(self):
        if not self.is_downloaded or not self.is_parsed:
            return []
        if not hasattr(self, '_news_keywords'):
            news_keywords = self.meta_data.get('news_keywords', '').split(',')
            self._news_keywords = [keyword.strip() for keyword in news_keywords]

        return self._news_keywords

    @property
    def source_url(self):
        return re.sub(r'(https://|http://|www.)', '', self._source_url)

    @source_url.setter
    def source_url(self, value):
        self._source_url = value
