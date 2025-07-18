from app.config.settings import settings
from app.utils.logger import app_logger as logger

from langchain.chat_models import init_chat_model

model = init_chat_model(
    api_key=settings.DEEPSEEK_MODEL_API_KEY,
    base_url=settings.DEEPSEEK_MODEL_BASE_URL,
    model=settings.DEEPSEEK_MODEL_NAME,
)

questions = "你好，请你介绍一下你自己"

result = model.invoke(questions)
logger.info(result.content)
