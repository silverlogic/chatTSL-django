from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import NumberFilter

from apps.tettra.models import TettraPageSubcategory


class TettraPageSubcategoriesFilter(FilterSet):
    category_id = NumberFilter(field_name="tettra_pages__category__category_id", distinct=True)

    class Meta:
        model = TettraPageSubcategory
        fields = ("category_id",)
