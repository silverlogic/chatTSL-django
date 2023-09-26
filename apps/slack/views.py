import json
import logging
from typing import Optional

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pydash
from rest_framework import status

from apps.slack import slack_bot_client
from apps.tettra.models import TettraPageCategory, TettraPageSubcategory

from .modals import SlackOpenAIChatModalBuilder
from .models import SlackEventCallbackData, SlackOpenAIChat
from .tasks import slack_handle_event_callback_message
from .utils import get_user_for_slack_user, verify_signature_for_slack_request

logger = logging.getLogger(__name__)


@csrf_exempt
def event_hook(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        if settings.ENVIRONMENT in ["development"]:
            logger.info(json.dumps(data, indent=4))

        if verify_signature_for_slack_request(request=request) is False:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

        type = data["type"]
        if type == "url_verification":
            return JsonResponse(dict(challenge=data["challenge"]), safe=False)
        if type == "event_callback":
            slack_event_callback_data = SlackEventCallbackData.objects.create(data=data)
            slack_handle_event_callback_message.delay(
                slack_event_callback_data_id=slack_event_callback_data.id
            )
        return HttpResponse(status=status.HTTP_200_OK)
    except json.JSONDecodeError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def slash_chat_settings(request):
    if verify_signature_for_slack_request(request=request) is False:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    team_id: str = request.POST.get("team_id")
    user_id: str = request.POST.get("user_id")
    channel_id: str = request.POST.get("channel_id")
    trigger_id: str = request.POST.get("trigger_id")
    user = get_user_for_slack_user(slack_user_id=user_id)
    if user is None:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    slack_chats = SlackOpenAIChat.objects.filter(
        slack_event_json__team_id=team_id,
        chat__user=user,
        slack_event_json__event__channel=channel_id,
    ).order_by("-created")[:10]

    modal_builder = SlackOpenAIChatModalBuilder(
        slack_chats=slack_chats,
        tettra_page_categories=TettraPageCategory.objects.distinct("category_id").order_by(
            "category_id"
        ),
        tettra_page_subcategories=TettraPageSubcategory.objects.distinct("subcategory_id").order_by(
            "subcategory_id"
        ),
    )

    response = slack_bot_client.views_open(
        trigger_id=trigger_id, view=modal_builder.build(private_metadata=channel_id)
    )
    response.validate()

    return HttpResponse(status=status.HTTP_200_OK)


@csrf_exempt
def interactive_endpoint(request):  # noqa: C901
    if verify_signature_for_slack_request(request=request) is False:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    try:
        payload = json.loads(request.POST.get("payload"))
        if settings.ENVIRONMENT in ["development"]:
            logger.info(json.dumps(payload, indent=4))

        type: str = payload.get("type")
        if type == "block_actions":
            user: dict = payload["user"]
            team: dict = payload["team"]
            view: dict = payload["view"]
            view_id: str = view["id"]
            view_hash: str = view["hash"]
            callback_id: str = view["callback_id"]

            user = get_user_for_slack_user(slack_user_id=user["id"])
            if user is None:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

            if callback_id == SlackOpenAIChatModalBuilder.SLACK_VIEW_CALLBACK_ID():
                state: dict = view["state"]
                values: dict = state["values"]
                channel_id: str = view["private_metadata"]
                slack_chats = SlackOpenAIChat.objects.filter(
                    slack_event_json__team_id=team["id"],
                    chat__user=user,
                    slack_event_json__event__channel=channel_id,
                ).order_by("-created")[:10]
                tettra_page_categories = TettraPageCategory.objects.distinct(
                    "category_id"
                ).order_by("category_id")
                tettra_page_subcategories = TettraPageSubcategory.objects.distinct(
                    "subcategory_id"
                ).order_by("subcategory_id")

                selected_slack_chat: Optional[SlackOpenAIChat] = None
                selected_tettra_page_category: Optional[TettraPageCategory] = None
                selected_tettra_page_subcategory: Optional[TettraPageSubcategory] = None

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.SLACK_CHAT_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    selected_slack_chat = SlackOpenAIChat.objects.get(id=id)

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.TETTRA_PAGE_CATEGORY_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    if id >= 0:
                        selected_tettra_page_category = TettraPageCategory.objects.get(id=id)
                elif selected_slack_chat:
                    selected_tettra_page_category = pydash.get(
                        selected_slack_chat, "chat.tettra_page_category_filter"
                    )

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.TETTRA_PAGE_SUBCATEGORY_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    if id >= 0:
                        selected_tettra_page_subcategory = TettraPageSubcategory.objects.get(id=id)
                elif selected_slack_chat:
                    selected_tettra_page_subcategory = pydash.get(
                        selected_slack_chat, "chat.tettra_page_subcategory_filter"
                    )

                if selected_tettra_page_category:
                    tettra_page_subcategories = tettra_page_subcategories.filter(
                        tettra_pages__category__id=selected_tettra_page_category.id
                    )

                modal_builder = SlackOpenAIChatModalBuilder(
                    slack_chats=slack_chats,
                    tettra_page_categories=tettra_page_categories,
                    tettra_page_subcategories=tettra_page_subcategories,
                    selected_slack_chat=selected_slack_chat,
                    selected_tettra_page_category=selected_tettra_page_category,
                    selected_tettra_page_subcategory=selected_tettra_page_subcategory,
                )
                slack_bot_client.views_update(
                    view_id=view_id,
                    hash=view_hash,
                    view=modal_builder.build(private_metadata=channel_id),
                )
        if type == "view_submission":
            view: dict = payload["view"]
            user_id = pydash.get(payload, "user.id")
            channel_id: str = view["private_metadata"]
            callback_id: str = view["callback_id"]

            if callback_id == SlackOpenAIChatModalBuilder.SLACK_VIEW_CALLBACK_ID():
                state: dict = view["state"]
                values: dict = state["values"]

                selected_slack_chat: Optional[SlackOpenAIChat] = None
                selected_tettra_page_category: Optional[TettraPageCategory] = None
                selected_tettra_page_subcategory: Optional[TettraPageSubcategory] = None

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.SLACK_CHAT_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    selected_slack_chat = SlackOpenAIChat.objects.get(id=id)

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.TETTRA_PAGE_CATEGORY_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    if id >= 0:
                        selected_tettra_page_category = TettraPageCategory.objects.get(id=id)

                if selected_option := pydash.get(
                    values,
                    "{}.static_select.selected_option".format(
                        SlackOpenAIChatModalBuilder.TETTRA_PAGE_SUBCATEGORY_BLOCK_ID()
                    ),
                ):
                    id = int(selected_option["value"])
                    if id >= 0:
                        selected_tettra_page_subcategory = TettraPageSubcategory.objects.get(id=id)

                if selected_slack_chat:
                    selected_slack_chat.chat.tettra_page_category_filter = (
                        selected_tettra_page_category
                    )
                    selected_slack_chat.chat.tettra_page_subcategory_filter = (
                        selected_tettra_page_subcategory
                    )
                    selected_slack_chat.chat.save()

                    slack_bot_client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        text="\n".join(
                            [
                                f"Updated Chat Settings for chat :{selected_slack_chat.chat.id}",
                                f"Tettra Page Category Filter: {pydash.get(selected_slack_chat, 'chat.tettra_page_category_filter.id') or 'null'}",
                                f"Tettra Page Subcategory Filter: {pydash.get(selected_slack_chat, 'chat.tettra_page_subcategory_filter.id') or 'null'}",
                            ]
                        ),
                    )

        return HttpResponse(status=status.HTTP_200_OK)
    except json.JSONDecodeError:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
