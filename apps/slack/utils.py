import hashlib
import hmac
import logging
import sys
from io import BytesIO
from pathlib import Path
from time import time
from typing import Optional, Tuple

from django.conf import settings
from django.core.files.images import ImageFile

import requests
from avatar.models import Avatar

from apps.slack import slack_bot_client
from apps.users.models import User

logger = logging.getLogger(__name__)


def get_user_for_slack_user(slack_user_id: str) -> Optional[User]:
    response = slack_bot_client.users_profile_get(
        user=slack_user_id,
    )
    response.validate()
    user_profile: dict = response["profile"]
    is_from_bot = isinstance(user_profile.get("api_app_id"), str)
    if is_from_bot:
        return None

    try:
        return User.objects.get(
            email=user_profile["email"],
        )
    except User.DoesNotExist:
        return None


def get_or_create_user_for_slack_user(slack_user_id: str) -> Tuple[Optional[User], bool]:
    response = slack_bot_client.users_profile_get(
        user=slack_user_id,
    )
    response.validate()
    user_profile: dict = response["profile"]
    is_from_bot = isinstance(user_profile.get("api_app_id"), str)
    if is_from_bot:
        return (None, False)

    user, created = User.objects.update_or_create(
        email=user_profile["email"],
        defaults=dict(
            first_name=user_profile.get("first_name"),
            last_name=user_profile.get("last_name"),
            username=user_profile.get("display_name"),
        ),
    )
    logger.info(f"Created user: {user} {created}")
    if created and (image_url := user_profile.get("image_original")):
        try:
            response = requests.get(image_url, params={})
            image = BytesIO(response.content)
            avatar = Avatar.objects.create(
                user=user, primary=True, avatar=ImageFile(image, name=Path(image_url).name)
            )
            logger.info(f"Created avatar {avatar}")
        except Exception as e:
            logger.error(f"Failed to create user avatar {e}")

    return (user, created)


def verify_signature_for_slack_request(request) -> bool:
    # Each request comes with request timestamp and request signature
    # return false if the timestamp is out of range
    req_timestamp = request.headers.get("X-Slack-Request-Timestamp")
    if req_timestamp is None or abs(time() - int(req_timestamp)) > 60 * 5:
        return False

    # Verify the request signature using the app's signing secret
    # return false if the signature can't be verified
    req_signature = request.headers.get("X-Slack-Signature")
    if req_signature is None:
        return False

    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    # Compare the generated hash and incoming request signature
    # Python 2.7.6 doesn't support compare_digest
    # It's recommended to use Python 2.7.7+
    # noqa See https://docs.python.org/2/whatsnew/2.7.html#pep-466-network-security-enhancements-for-python-2-7
    # req = str.encode('v0:' + str(req_timestamp) + ':') + request.get_data()
    req = str.encode("v0:" + str(req_timestamp) + ":") + request.body
    request_hash = (
        "v0=" + hmac.new(str.encode(settings.SLACK_SIGNING_SECRET), req, hashlib.sha256).hexdigest()
    )

    if hasattr(hmac, "compare_digest"):
        # Compare byte strings for Python 2
        if sys.version_info[0] == 2:
            return hmac.compare_digest(bytes(request_hash), bytes(req_signature))
        else:
            return hmac.compare_digest(request_hash, req_signature)
    else:
        if len(request_hash) != len(req_signature):
            return False
        result = 0
        if isinstance(request_hash, bytes) and isinstance(req_signature, bytes):
            for x, y in zip(request_hash, req_signature):
                result |= x ^ y
        else:
            for x, y in zip(request_hash, req_signature):
                result |= ord(x) ^ ord(y)
        return result == 0
