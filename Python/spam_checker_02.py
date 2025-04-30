# Импорт необходимых модулей
import logging
from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Загрузка переменных окружения
load_dotenv()

# Инициализация логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Конфигурация модели
LOCAL_LLM = os.getenv('LOCAL_LLM')


async def check_spam(topic: str, prompt_template: str) -> bool:
    """Асинхронная проверка сообщения на спам с использованием заданного промпта"""
    try:
        # Форматирование промпта с текущим сообщением
        formatted_prompt = prompt_template.format(question=topic)

        # Инициализация модели языкового обучения
        llm = ChatOllama(
            model=LOCAL_LLM,
            temperature=0
        )

        # Асинхронный вызов языковой модели
        response = await llm.ainvoke([HumanMessage(content=formatted_prompt)])
        model_response = response.content.strip().upper()
        logger.debug(f'model_response={model_response}')

        # Определение результата проверки (SPAM/NOT_SPAM)
        return model_response == "SPAM"
    except Exception as e:
        logger.error(f"Ошибка при проверке спама: {e}")
        return False