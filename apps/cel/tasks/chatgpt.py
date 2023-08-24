from apps.cel import app
from apps.cel.utils import task_lock
from apps.chatgpt.chat import Chat
from core.logger import celery_logger


@app.task(bind=True)
@task_lock()
def chat(self):
    celery_logger.info(f"[Chat] Start {self.request.id}")
    Chat().reply()
    celery_logger.info(f"[Chat] End {self.request.id}")
