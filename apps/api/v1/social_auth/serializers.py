import requests
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from social.apps.django_app.utils import load_strategy, load_backend
from social.exceptions import MissingBackend

from apps.users.pipeline import EmailNotProvidedError, EmailAlreadyExistsError


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.CharField()
    access_token = serializers.CharField()

    def validate_provider(self, provider):
        strategy = load_strategy(self.context['request'])

        try:
            return load_backend(strategy, provider, redirect_uri=None)
        except MissingBackend:
            raise serializers.ValidationError('Invalid provider.')

    def create(self, validated_data):
        try:
            user = validated_data['provider'].do_auth(validated_data['access_token'])
        except requests.HTTPError:
            raise serializers.ValidationError({'access_token': 'invalid_access_token'})
        except EmailNotProvidedError:
            raise serializers.ValidationError({'email': 'no_email_provided'})
        except EmailAlreadyExistsError:
            raise serializers.ValidationError({'email': 'email_already_in_use'})
        return Token.objects.get_or_create(user=user)[0]
