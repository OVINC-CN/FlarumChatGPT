from django.db import models
from django.utils.translation import gettext_lazy

from core.constants import MEDIUM_CHAR_LENGTH, SHORT_CHAR_LENGTH
from core.models import BaseModel, UniqIDField


class ChatLog(BaseModel):
    """
    Chat Log
    """

    id = UniqIDField(gettext_lazy("ID"))
    post_id = models.BigIntegerField(gettext_lazy("Post ID"), null=True, blank=True, db_index=True)
    message = models.TextField(gettext_lazy("Message"), null=True, blank=True)
    reply = models.TextField(gettext_lazy("Reply Content"), null=True, blank=True)
    openai_id = models.CharField(
        gettext_lazy("OpenAI ID"), max_length=MEDIUM_CHAR_LENGTH, null=True, blank=True, db_index=True
    )
    model = models.CharField(gettext_lazy("Model"), max_length=SHORT_CHAR_LENGTH, db_index=True, null=True, blank=True)
    duration = models.IntegerField(gettext_lazy("Duration(ms)"), null=True, blank=True)
    prompt_tokens = models.IntegerField(gettext_lazy("Prompt Tokens Count"), null=True, blank=True)
    completion_tokens = models.IntegerField(gettext_lazy("Completion Tokens Count"), null=True, blank=True)
    total_tokens = models.IntegerField(gettext_lazy("Total Tokens Count"), null=True, blank=True)
    is_success = models.BooleanField(gettext_lazy("Is Success"), db_index=True)
    created_at = models.DateTimeField(gettext_lazy("Create Time"), auto_now=True, db_index=True)

    class Meta:
        verbose_name = gettext_lazy("Chat Log")
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
