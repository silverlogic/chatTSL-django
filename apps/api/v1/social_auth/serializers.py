from django.utils.translation import ugettext_lazy as _

import requests
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from social.apps.django_app.utils import load_backend, load_strategy
from social.exceptions import MissingBackend

from apps.referrals.utils import get_user_from_referral_code
from apps.users.pipeline import EmailAlreadyExistsError, EmailNotProvidedError


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.CharField()
    access_token = serializers.CharField()
    referral_code = serializers.CharField(required=False, allow_blank=True)

    def validate_provider(self, provider):
        strategy = load_strategy(self.context['request'])

        try:
            return load_backend(strategy, provider, redirect_uri=None)
        except MissingBackend:
            raise serializers.ValidationError('Invalid provider.')

    def validate_referral_code(self, referral_code):
        referrer = get_user_from_referral_code(referral_code)
        if not referrer:
            raise serializers.ValidationError(_('Invalid referral code.'))
        return referral_code

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
