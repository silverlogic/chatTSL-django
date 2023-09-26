import json
from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

import httpretty
import pytest

from apps.chatbot.models import OpenAIChat
from apps.slack.models import SlackInstallation

import tests.factories as f

pytestmark = pytest.mark.django_db


class TestSlack:
    @patch("apps.slack.views.verify_signature_for_slack_request")
    def test_event_hook__url_verification(
        self,
        mock_verify_signature_for_slack_request,
        client,
    ):
        mock_verify_signature_for_slack_request.return_value = True
        url = reverse("{}:{}".format("slack", "event_hook"))
        data = {
            "token": settings.SLACK_VERIFICATION_TOKEN,
            "type": "url_verification",
            "challenge": "test-challenge",
        }
        r = client.post(url, data)
        assert r.json()["challenge"] == "test-challenge"

    @patch("apps.slack.views.verify_signature_for_slack_request")
    def test_event_hook__tokens_revoked(
        self,
        mock_verify_signature_for_slack_request,
        use_httpretty,
        client,
    ):
        httpretty.register_uri(
            httpretty.POST,
            "https://www.slack.com/api/auth.revoke",
            body=json.dumps(
                {
                    "ok": True,
                }
            ),
            content_type="application/json",
            status=200,
        )

        mock_verify_signature_for_slack_request.return_value = True
        slack_installation = f.SlackInstallationFactory()
        url = reverse("{}:{}".format("slack", "event_hook"))
        data = {
            "token": settings.SLACK_VERIFICATION_TOKEN,
            "team_id": slack_installation.slack_oauth_response["team"]["id"],
            "api_app_id": slack_installation.slack_oauth_response["app_id"],
            "event": {
                "type": "tokens_revoked",
                "tokens": {
                    "oauth": [],
                    "bot": [slack_installation.slack_oauth_response["bot_user_id"]],
                },
                "event_ts": "1694035866.044349",
            },
            "type": "event_callback",
            "event_id": "Ev05RY1WJN1E",
            "event_time": 1694035866,
        }
        r = client.post(url, data)
        assert r.status_code == 200
        assert SlackInstallation.objects.count() == 0

    @patch("apps.slack.views.verify_signature_for_slack_request")
    def test_event_hook__app_uninstalled(
        self,
        mock_verify_signature_for_slack_request,
        use_httpretty,
        client,
    ):
        httpretty.register_uri(
            httpretty.POST,
            "https://www.slack.com/api/auth.revoke",
            body=json.dumps(
                {
                    "ok": True,
                }
            ),
            content_type="application/json",
            status=200,
        )

        mock_verify_signature_for_slack_request.return_value = True
        slack_installation = f.SlackInstallationFactory()
        url = reverse("{}:{}".format("slack", "event_hook"))
        data = {
            "token": settings.SLACK_VERIFICATION_TOKEN,
            "team_id": slack_installation.slack_oauth_response["team"]["id"],
            "api_app_id": slack_installation.slack_oauth_response["app_id"],
            "event": {"type": "app_uninstalled", "event_ts": "1694035866.052202"},
            "type": "event_callback",
            "event_id": "Ev05QUFVQKHV",
            "event_time": 1694035866,
        }
        r = client.post(url, data)
        assert r.status_code == 200
        assert SlackInstallation.objects.count() == 0

    @patch("apps.slack.views.verify_signature_for_slack_request")
    @patch("apps.slack.views.get_user_for_slack_user")
    def test_slash_chat_settings(
        self,
        mock_get_user_for_slack_user,
        mock_verify_signature_for_slack_request,
        use_httpretty,
        client,
    ):
        httpretty.register_uri(
            httpretty.POST,
            "https://www.slack.com/api/views.open",
            body=json.dumps(
                {
                    "ok": True,
                }
            ),
            content_type="application/json",
            status=200,
        )

        user = f.UserFactory(
            email="test@tsl.io", first_name="Test", last_name="TSL", username="test-tsl"
        )
        user.save()
        mock_get_user_for_slack_user.return_value = user
        mock_verify_signature_for_slack_request.return_value = True
        url = reverse("{}:{}".format("slack", "slash_chat_settings"))
        assert OpenAIChat.objects.filter(user=user).count() == 0
        data = "token={token}&user_id={user_id}".format(
            token=settings.SLACK_VERIFICATION_TOKEN, user_id=user.id
        )
        r = client.post(url, data, content_type="application/x-www-form-urlencoded")
        assert r.status_code == 200
