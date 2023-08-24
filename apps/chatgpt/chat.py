from typing import Dict, List

import openai
import requests
from django.conf import settings
from django.utils.translation import gettext
from openai.openai_object import OpenAIObject

from apps.chatgpt.models import ChatLog
from core.logger import logger


class Chat:
    def __init__(self):
        self.web = requests.session()
        self.web.headers = {"Authorization": f"Token {settings.FLARUM_USER_API_TOKEN}"}
        self.username = self.load_username()

    def load_username(self) -> str:
        resp = self.web.get(f"{settings.FLARUM_API_URL}/users/{settings.FLARUM_USER_ID}").json()
        return resp["data"]["attributes"]["username"]

    def reply(self):
        posts = self.load_all_posts()
        logger.info("[ChatPostsCount] %d", len(posts["data"]))
        for post in posts["data"]:
            message = self.parse_user_content(post)
            if message:
                is_success, reply = self.call_api(messages=[{"role": "user", "content": message}])
            else:
                is_success = False
                reply = self.create_error_reply()
            self.create_post(post=post, included=posts["included"], reply=reply)
            self.record_log(post=post, reply=reply, is_success=is_success)

    def call_api(self, messages: List[Dict[str, str]]) -> (bool, OpenAIObject):
        try:
            return True, openai.ChatCompletion.create(model=settings.OPENAI_DEFAULT_MODEL, messages=messages)
        except Exception as err:
            logger.exception("[CallOpenAIFailed] %s", err)
            return False, self.create_error_reply()

    def create_error_reply(self) -> OpenAIObject:
        reply = OpenAIObject()
        choice = OpenAIObject()
        message = OpenAIObject()
        setattr(message, "content", gettext("OpenAI Error"))
        setattr(choice, "message", message)
        setattr(reply, "choices", [choice])
        return reply

    def parse_resp_message(self, reply: OpenAIObject) -> str:
        choices = getattr(reply, "choices", None)
        if not choices:
            return ""
        choice = choices[0]
        message = getattr(choice, "message", None)
        if not message:
            return ""
        return getattr(message, "content", "")

    def load_all_posts(self) -> dict:
        # ignore replied
        replied_posts = [str(i) for i in ChatLog.objects.values_list("post_id", flat=True)]
        # load all
        resp = self.web.get(
            url=(
                "{}/posts"
                "?filter%5Btype%5D=comment"
                "&filter%5Bmentioned%5D={}"
                "&page%5Boffset%5D"
                "&page%5Blimit%5D={}"
                "&sort=-createdAt"
            ).format(settings.FLARUM_API_URL, settings.FLARUM_USER_ID, settings.FLARUM_REPLY_MAX_SIZE)
        ).json()
        resp["data"] = [
            p
            for p in resp["data"]
            if p["id"] not in replied_posts and p["relationships"]["user"]["data"]["id"] != settings.FLARUM_USER_ID
        ]
        return resp

    def parse_user_content(self, post: dict) -> str:
        return post["attributes"].get("content", "")

    def record_log(self, post: dict, reply: OpenAIObject = None, is_success: bool = True) -> None:
        usage = getattr(reply, "usage", OpenAIObject())
        ChatLog.objects.create(
            post_id=post["id"],
            message=self.parse_user_content(post),
            reply=self.parse_resp_message(reply),
            openai_id=getattr(reply, "openai_id", None),
            model=getattr(reply, "model", None),
            duration=getattr(reply, "response_ms", None),
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            is_success=is_success,
        )

    def create_post(self, post: dict, included: list, reply: OpenAIObject) -> bool:
        data = {
            "data": {
                "type": "posts",
                "attributes": {
                    "content": '@"{}"#p{} {}'.format(
                        self.get_reply_username(post=post, included=included),
                        post["id"],
                        self.parse_resp_message(reply),
                    )
                },
                "relationships": {"discussion": post["relationships"]["discussion"]},
            }
        }
        try:
            status_code = self.web.post(f"{settings.FLARUM_API_URL}/posts", json=data).status_code
            return 200 <= status_code < 300
        except Exception as err:
            logger.exception("[CreatePostFailed] %s", err)
            return False

    def get_reply_username(self, post: dict, included: list) -> str:
        user_id = post["relationships"]["user"]["data"]["id"]
        for include in included:
            if include["type"] == "users" and include["id"] == user_id:
                return include["attributes"]["username"]
        return user_id
