from rest_framework import status
from rest_framework.response import Response


class DestroyModelMixin:
    """Destroy mixin that returns serialized object as response.

    HTTP_204_NO_CONTENT with Content-Length != 0
    Response is dropped by iOS so request will fail after timeout

    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance, many=False).data
        self.perform_destroy(instance)
        return Response(data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()
