import json
from collections import OrderedDict

from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.encoders import JSONEncoder


class WebsocketRequest:
    def __init__(self, query_params):
        self.query_params = query_params


class WebsocketPageNumberPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, scope, view=None, page=1, **kwargs):
        request = WebsocketRequest({"page": page})
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("pages", self.page.paginator.num_pages),
                ("results", data),
            ]
        )


class GenericConsumer(GenericAsyncAPIConsumer):
    def filter_queryset(self, queryset, filters=None, **kwargs):
        request = WebsocketRequest(filters)
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, cls=JSONEncoder)
