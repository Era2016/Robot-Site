from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    def get_response_meta(self, data):
        return {
            'count': self.page.paginator.count,
            'page': self.page.number,
            'items_per_page': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link()
        }

    def get_paginated_response(self, data):
        return Response({
            'meta': self.get_response_meta(data),
            'results': data
        })
