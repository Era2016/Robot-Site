from core.pagination import CustomPagination


class NotificationPagination(CustomPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.unread_count = queryset.filter(unread=True).count()
        return super(NotificationPagination, self).paginate_queryset(
            queryset, request, view
        )

    def get_response_meta(self, data):
        meta = super(NotificationPagination, self).get_response_meta(data)
        meta.update({'unread_count': self.unread_count})
        return meta
