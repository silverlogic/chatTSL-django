from rest_framework import mixins, permissions, response, status, viewsets

from apps.referrals.emails import send_referrals_email

from .serializers import ReferralsSerializer


class ReferralsViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = ReferralsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']

        info = {
            'email': email,
            'user': user,
        }

        send_referrals_email(info)
        return response.Response(ReferralsSerializer(info).data, status=status.HTTP_200_OK)
