import ast
import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI

from .models import TettraPageSubcategory

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TettraPageSubcategory)
def generate_subcategory_icon(sender, instance, **kwargs):
    if kwargs.get("created", False) and not instance.subcategory_icon:
        chat_openai = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY, temperature=0, model="gpt-4-0613"
        )

        used_emojis = TettraPageSubcategory.objects.exclude(id=instance.id).values_list(
            "subcategory_icon", flat=True
        )
        used_emojis = list(filter(None, used_emojis))

        messages = [
            SystemMessage(
                content="You are a helpful assistant that finds the best emoji to use as a subcategory icon. Please return a JSON response with the following format: { 'subcategory_name': 'Getting Started', 'emojis': ['👋', '👍', '👌'] }"
            ),
            HumanMessage(
                content=f"The best 3 emojis for {instance.subcategory_name}, excluding the ones already used {used_emojis}, are:",
            ),
        ]

        try:
            chat_response = chat_openai(messages)
            chat_response_content = chat_response.content
            response_dict = ast.literal_eval(chat_response_content)
            emoji_suggestions = response_dict.get("emojis")

            if all(emoji in used_emojis for emoji in emoji_suggestions):
                instance.subcategory_icon = None
                instance.save()
                raise Exception("No new emoji found by the AI model.")

            for emoji in emoji_suggestions:
                if emoji not in used_emojis:
                    instance.subcategory_icon = emoji
                    instance.save()
                    break
        except Exception as e:
            logger.exception(e)
            instance.subcategory_icon = None
            instance.save()
