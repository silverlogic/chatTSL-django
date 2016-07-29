from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse

from requests import HTTPError
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_social_auth.views import SocialTokenOnlyAuthView, decorate_request
from social.exceptions import AuthException
from social.utils import parse_qs

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

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        input_data = self.get_serializer_in_data()
        provider_name = self.get_provider_name(input_data)
        if not provider_name:
            return self.respond_error("Provider is not specified")
        self.set_input_data(request, input_data)
        decorate_request(request, provider_name)
        manual_redirect_uri = request.data.get('redirect_uri', None)
        if manual_redirect_uri:
            self.request.backend.redirect_uri = manual_redirect_uri
        serializer_in = self.get_serializer_in(data=input_data)
        if self.oauth_v1() and request.backend.OAUTH_TOKEN_PARAMETER_NAME not in input_data:
            # oauth1 first stage (1st is get request_token, 2nd is get access_token)
            request_token = parse_qs(request.backend.set_unauthorized_token())
            return Response(request_token)
        serializer_in.is_valid(raise_exception=True)
        try:
            user = self.get_object()
        except (AuthException, HTTPError) as e:
            return self.respond_error(e)
        if isinstance(user, HttpResponse):  # An error happened and pipeline returned HttpResponse instead of user
            return user
        resp_data = self.get_serializer(instance=user)
        self.do_login(request.backend, user)
        return Response(resp_data.data)

    def respond_error(self, error):
        if isinstance(error, (AuthException, HTTPError)):
            raise serializers.ValidationError({'non_field_errors': 'invalid_credentials'})
        return Response(status=status.HTTP_400_BAD_REQUEST)
