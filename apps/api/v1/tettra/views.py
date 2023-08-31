import json

from django.core.files.uploadedfile import InMemoryUploadedFile

from django_filters import rest_framework as django_filters
from rest_framework import mixins, permissions, response, status, viewsets

from apps.tettra.models import TettraPage, TettraPageCategory, TettraPageSubcategory

from .filters import TettraPageSubcategoriesFilter
from .serializers import (
    TettraPageCategorySerializer,
    TettraPageImportDumpSerializer,
    TettraPageSerializer,
    TettraPageSubcategorySerializer,
)


class TettraPageImportDumpViewSet(viewsets.GenericViewSet):
    serializer_class = TettraPageImportDumpSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file: InMemoryUploadedFile = serializer.validated_data["file"]
        content: str = file.read()
        data = json.loads(content)
        response_data = dict()

        for tettra_page_data in data:
            tettra_page_data["page_id"] = tettra_page_data.get("id", -1)
            page_id = tettra_page_data["page_id"]
            if any(
                [
                    tettra_page_data.get("category_id", None) is None,
                    tettra_page_data.get("category_name", None) is None,
                ]
            ):
                response_data[page_id] = "Skipping because of null category"
            elif tettra_page_data.get("deleted_at", None) is not None:
                TettraPage.objects.filter(page_id=page_id).delete()
                response_data[page_id] = "Deleted"
            else:
                category_data = dict(
                    category_id=tettra_page_data.pop("category_id"),
                    category_name=tettra_page_data.pop("category_name"),
                )
                subcategory_data: dict = None
                if all(
                    [
                        tettra_page_data.get("subcategory_id", None) is not None,
                        tettra_page_data.get("subcategory_name", None) is not None,
                    ]
                ):
                    subcategory_data = dict(
                        subcategory_id=tettra_page_data.pop("subcategory_id"),
                        subcategory_name=tettra_page_data.pop("subcategory_name"),
                    )
                try:
                    serializer = TettraPageSerializer(
                        TettraPage.objects.get(page_id=page_id), data=tettra_page_data, partial=True
                    )
                    response_data[page_id] = "Updated"
                except TettraPage.DoesNotExist:
                    serializer = TettraPageSerializer(data=tettra_page_data, partial=True)
                    response_data[page_id] = "Created"

                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save(category=category_data, subcategory=subcategory_data)
                except BaseException as e:
                    response_data[page_id] = str(e)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
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
