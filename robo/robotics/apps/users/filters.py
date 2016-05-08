import django_filters
from notifications.models import Notification


class NotificationFilter(django_filters.FilterSet):
    # workaround for demo day, assume that notification with higher id
    # means later created date
    min_id = django_filters.NumberFilter(name="id", lookup_type='gt')

    class Meta:
        model = Notification
        fields = ('min_id',)

# test if the repo works
# test again
