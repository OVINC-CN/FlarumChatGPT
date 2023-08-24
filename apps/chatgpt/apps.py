from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class ChatgptConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chatgpt"
    verbose_name = gettext_lazy("ChatGPT")
