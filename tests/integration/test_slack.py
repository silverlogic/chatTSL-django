from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

import pytest

from apps.chatbot.models import OpenAIChat

import tests.factories as f

pytestmark = pytest.mark.django_db


class TestSlack:
    @patch("apps.slack.utils.verify_signature_for_slack_request")
    @patch("apps.slack.utils.get_or_create_user_for_slack_user")
    def test_slash_new_chat(
        self,
        mock_get_or_create_user_for_slack_user,
        mock_verify_signature_for_slack_request,
        client,
    ):
        user = f.UserFactory(
            email="test@tsl.io", first_name="Test", last_name="TSL", username="test-tsl"
        )
        user.save()
        mock_get_or_create_user_for_slack_user.return_value = (user, False)
        mock_verify_signature_for_slack_request.return_value = True
        url = reverse("{}:{}".format("slack", "slash_new_chat"))
        assert OpenAIChat.objects.filter(user=user).count() == 0
        data = "token={token}&user_id={user_id}".format(
            token=settings.SLACK_VERIFICATION_TOKEN, user_id=user.id
        )
        r = client.post(url, data, content_type="application/x-www-form-urlencoded")
        assert r.status_code == 200
        assert OpenAIChat.objects.filter(user=user).count() == 1

    @patch("apps.slack.utils.verify_signature_for_slack_request")
    @patch("apps.slack.utils.get_or_create_user_for_slack_user")
    def test_event_hook(
        self,
        mock_get_or_create_user_for_slack_user,
        mock_verify_signature_for_slack_request,
        client,
    ):
        user = f.UserFactory(
            email="test@tsl.io", first_name="Test", last_name="TSL", username="test-tsl"
        )
        user.save()
        mock_get_or_create_user_for_slack_user.return_value = (user, False)
        mock_verify_signature_for_slack_request.return_value = True
        url = reverse("{}:{}".format("slack", "event_hook"))
        data = {
            "token": settings.SLACK_VERIFICATION_TOKEN,
            "type": "url_verification",
            "challenge": "test-challenge",
        }
        r = client.post(url, data)
        assert r.json()["challenge"] == "test-challenge"
