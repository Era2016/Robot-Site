from core.pagination import CustomPagination


# FIXME: workaround to support pagination on brief's ordered tasks
# django/django-rest pagination only work with queryset instead of list
# and there's no good solution to retrieve brief's ordered tasks
# in queryset format yet
class NotificationPagination(CustomPagination):
    def get_response_meta(self, data):
        return {
            'count': len(data),
            'page': 1,  # brief should not have more than 20 tasks
            'items_per_page': 20,
            'next': None,
            'previous': None
        }
