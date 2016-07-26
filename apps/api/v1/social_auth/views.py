from rest_framework import response, viewsets

from .serializers import SocialAuthSerializer


class SocialAuthViewSet(viewsets.GenericViewSet):
    serializer_class = SocialAuthSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return response.Response({'token': token.key})
