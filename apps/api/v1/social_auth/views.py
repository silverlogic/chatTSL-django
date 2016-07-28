from django.http import Http404

from requests import HTTPError
from rest_framework import viewsets, serializers
from rest_social_auth.views import SocialTokenOnlyAuthView
from social.exceptions import AuthException

from apps.users.pipeline import EmailAlreadyExistsError, EmailNotProvidedError

from .serializers import SocialAuthOAuth1Serializer, SocialAuthOAuth2Serializer


class SocialAuthViewSet(SocialTokenOnlyAuthView, viewsets.GenericViewSet):
    oauth1_serializer_class_in = SocialAuthOAuth1Serializer
    oauth2_serializer_class_in = SocialAuthOAuth2Serializer

    def create(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Http404:
            raise serializers.ValidationError({'provider': ['Invaild provider']})
        except EmailNotProvidedError:
            raise serializers.ValidationError({'email': 'no_email_provided'})
        except EmailAlreadyExistsError:
            raise serializers.ValidationError({'email': 'email_already_in_use'})

    def respond_error(self, error):
        if isinstance(error, (AuthException, HTTPError)):
            raise serializers.ValidationError({'non_field_errors': 'invalid_credentials'})
        return super().respond_error(error)
