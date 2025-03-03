from django.http import Http404
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, response, serializers, viewsets

from apps.api.v1.decorators import action
from apps.users.models import User

from .serializers import (
    ChangePasswordSerializer,
    ConfirmEmailSerializer,
    UserPublicSerializer,
    UserSerializer,
)


class UpdateSelfPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("PUT", "PATCH"):
            if not request.user.is_authenticated or request.user != obj:
                return False
        return True


class UsersViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        UpdateSelfPermission,
    ]
    queryset = User.objects.all().order_by("id")
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("first_name", "last_name")

    @action(detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return response.Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[],
        serializer_class=UserPublicSerializer,
    )
    def public(self, request):
        user = request.GET.get("username", None)
        user_instance = User.objects.get(username=user)
        serializer = UserPublicSerializer(user_instance)
        return response.Response(serializer.data)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=ChangePasswordSerializer,
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"detail": "success"})

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[],
        serializer_class=ConfirmEmailSerializer,
    )
    def confirm_email(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_object()
        except Http404:
            raise serializers.ValidationError(_("Invalid token"))
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({})
