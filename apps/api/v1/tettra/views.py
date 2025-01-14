from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as django_filters
from rest_framework import mixins, permissions, response, status, viewsets

from apps.tettra.models import TettraPageCategory, TettraPageSubcategory

from .filters import TettraPageSubcategoriesFilter
from .serializers import (
    TettraPageCategorySerializer,
    TettraPageImportDumpSerializer,
    TettraPageSubcategorySerializer,
)


class TettraPageImportDumpViewSet(viewsets.GenericViewSet):
    serializer_class = TettraPageImportDumpSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        return response.Response(
            data=dict(
                error=_("Deprecated API. Please use the new tettra_page management command.")
            ),
            status=status.HTTP_410_GONE,
        )


class TettraPageCategoriesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TettraPageCategory.objects.all().distinct("category_id").order_by("category_id")
    serializer_class = TettraPageCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class TettraPageSubcategoriesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        TettraPageSubcategory.objects.all().distinct("subcategory_id").order_by("subcategory_id")
    )
    serializer_class = TettraPageSubcategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = TettraPageSubcategoriesFilter
