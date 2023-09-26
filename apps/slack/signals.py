import logging

from django.db.models.signals import post_delete
from django.dispatch import receiver

from slack_sdk import WebClient, errors as slack_errors

from apps.slack.models import SlackInstallation

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=SlackInstallation)
def on_slack_event_installation_deleted(sender, instance: SlackInstallation, *args, **kwargs):
    if not SlackInstallation.objects.exists():
        slack_oauth_response = instance.slack_oauth_response
        slack_client = WebClient(token=slack_oauth_response["access_token"])

        try:
            # TODO: Should we revoke or completely uninstall?
            response = slack_client.auth_revoke()
            # response = slack_client.apps_uninstall(
            #     client_id=settings.SLACK_CLIENT_ID,
            #     client_secret=settings.SLACK_CLIENT_SECRET,
            #     app_id=slack_oauth_response["app_id"],
            #     team_ids=[slack_oauth_response["team"]["id"]],
            # )
            response.validate()
        except slack_errors.SlackApiError as e:
            error = e.response.data.get("error")
            if error == "account_inactive":
                pass
            else:
                raise e
