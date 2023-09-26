import itertools
from dataclasses import dataclass
from typing import Optional

from django.db.models.query import QuerySet
from django.utils import timezone

import pydash

from apps.slack.models import SlackOpenAIChat
from apps.tettra.models import TettraPageCategory, TettraPageSubcategory


@dataclass
class SlackOpenAIChatModalBuilder:
    slack_chats: QuerySet[SlackOpenAIChat]
    tettra_page_categories: QuerySet[TettraPageCategory]
    tettra_page_subcategories: QuerySet[TettraPageSubcategory]

    selected_slack_chat: Optional[SlackOpenAIChat] = None
    selected_tettra_page_category: Optional[TettraPageCategory] = None
    selected_tettra_page_subcategory: Optional[TettraPageSubcategory] = None

    @classmethod
    def SLACK_VIEW_CALLBACK_ID(cls) -> str:
        return "slack_chat-options"

    @classmethod
    def SLACK_CHAT_BLOCK_ID(cls) -> str:
        return "actions-slack_chat"

    @classmethod
    def TETTRA_PAGE_CATEGORY_BLOCK_ID(cls) -> str:
        return "actions-tettra_page_category"

    @classmethod
    def TETTRA_PAGE_SUBCATEGORY_BLOCK_ID(cls) -> str:
        return "actions-tettra_page_subcategory"

    def build_slack_chat_block(self) -> dict:
        def _option_for(slack_chat: SlackOpenAIChat) -> dict:
            date = timezone.datetime.fromtimestamp(
                float(slack_chat.slack_event_json["event"]["event_ts"])
            )
            return {
                "text": {
                    "type": "plain_text",
                    "text": "{}    {}".format(
                        slack_chat.slack_event_json["event"]["text"][:30],
                        date.strftime("%d-%m-%Y %I:%M %p UTC"),
                    ),
                    "emoji": False,
                },
                "value": f"{slack_chat.id}",
            }

        items = list(self.slack_chats)
        if len(items) == 0:
            return None

        return {
            "block_id": SlackOpenAIChatModalBuilder.SLACK_CHAT_BLOCK_ID(),
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Slack OpenAI Chat"},
            "accessory": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select an item", "emoji": True},
                "options": [_option_for(item) for item in items],
                **dict(
                    dict(
                        initial_option=_option_for(
                            pydash.find(items, lambda item: item.id == self.selected_slack_chat.id)
                        )
                    )
                    if isinstance(self.selected_slack_chat, SlackOpenAIChat)
                    else dict()
                ),
                "action_id": "static_select",
            },
        }

    def build_tettra_page_category_block(self) -> Optional[dict]:
        def _option_for(tettra_page_category: TettraPageCategory) -> dict:
            return {
                "text": {
                    "type": "plain_text",
                    "text": tettra_page_category.category_name if tettra_page_category else "None",
                    "emoji": False,
                },
                "value": f"{tettra_page_category.id if tettra_page_category else -1}",
            }

        if not isinstance(self.selected_slack_chat, SlackOpenAIChat):
            return None
        items = list(self.tettra_page_categories)
        if len(items) == 0:
            return None

        return {
            "block_id": SlackOpenAIChatModalBuilder.TETTRA_PAGE_CATEGORY_BLOCK_ID(),
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Category"},
            "accessory": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select an item", "emoji": True},
                "options": [_option_for(item) for item in [None, *items]],
                "initial_option": _option_for(
                    pydash.find(
                        items, lambda item: item.id == self.selected_tettra_page_category.id
                    )
                    if self.selected_tettra_page_category
                    else None
                ),
                "action_id": "static_select",
            },
        }

    def build_tettra_page_subcategory_block(self) -> Optional[dict]:
        def _option_for(tettra_page_subcategory: TettraPageSubcategory) -> dict:
            return {
                "text": {
                    "type": "plain_text",
                    "text": tettra_page_subcategory.subcategory_name
                    if tettra_page_subcategory
                    else "None",
                    "emoji": False,
                },
                "value": f"{tettra_page_subcategory.id if tettra_page_subcategory else -1}",
            }

        if not isinstance(self.selected_slack_chat, SlackOpenAIChat):
            return None
        if not isinstance(self.selected_tettra_page_category, TettraPageCategory):
            return None
        items = list(self.tettra_page_subcategories)
        if len(items) == 0:
            return None
        return {
            "block_id": SlackOpenAIChatModalBuilder.TETTRA_PAGE_SUBCATEGORY_BLOCK_ID(),
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Subcategory"},
            "accessory": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select an item", "emoji": True},
                "options": [_option_for(item) for item in [None, *items]],
                "initial_option": _option_for(
                    pydash.find(
                        items, lambda item: item.id == self.selected_tettra_page_subcategory.id
                    )
                    if self.selected_tettra_page_subcategory
                    else None
                ),
                "action_id": "static_select",
            },
        }

    def build(self, **kwargs) -> dict:
        return {
            "callback_id": SlackOpenAIChatModalBuilder.SLACK_VIEW_CALLBACK_ID(),
            "title": {"type": "plain_text", "text": "SlackOpenAIChat Options"},
            **dict(
                dict(submit={"type": "plain_text", "text": "Submit"})
                if isinstance(self.selected_slack_chat, SlackOpenAIChat)
                else dict()
            ),
            "blocks": list(
                itertools.filterfalse(
                    lambda item: not item,
                    [
                        self.build_slack_chat_block(),
                        self.build_tettra_page_category_block(),
                        self.build_tettra_page_subcategory_block(),
                    ],
                )
            ),
            "type": "modal",
            **kwargs,
        }
