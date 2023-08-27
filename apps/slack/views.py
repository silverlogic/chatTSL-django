import json
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status

from apps.chatbot.models import OpenAIChat

from .tasks import slack_handle_event_callback_message
from .utils import get_or_create_user_for_slack_user, verify_signature_for_slack_request

logger = logging.getLogger(__name__)


@csrf_exempt
def event_hook(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        # Deprecated
        token = data["token"]
        if token != settings.SLACK_VERIFICATION_TOKEN:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        # New
        if verify_signature_for_slack_request(request=request) is False:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        type = data["type"]
        if type == "url_verification":
            return JsonResponse(dict(challenge=data["challenge"]), safe=False)
        if type == "event_callback":
            event = data["event"]
            event_type = event["type"]
            if event_type == "message":
                slack_handle_event_callback_message.delay(request_data=data)
        return HttpResponse(status=status.HTTP_200_OK)
    except json.JSONDecodeError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def slash_new_chat(request):
    # Deprecated
    token = request.POST.get("token")
    if token != settings.SLACK_VERIFICATION_TOKEN:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
    # New
    if verify_signature_for_slack_request(request=request) is False:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    user_id = request.POST.get("user_id")
    user, _ = get_or_create_user_for_slack_user(slack_user_id=user_id)
    if user is None:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    chat = OpenAIChat.objects.create(user=user)
    return HttpResponse(f"Started new chat {chat.id}", status=status.HTTP_200_OK)
