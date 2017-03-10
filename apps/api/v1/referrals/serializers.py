from django.utils.translation import ugettext as _

from rest_framework import serializers

from apps.users.models import User


class ReferralsSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            if User.objects.get(email=email):
                raise serializers.ValidationError(_("Can't refer someone that's already registered."))

        except User.DoesNotExist:
            pass
        return email
