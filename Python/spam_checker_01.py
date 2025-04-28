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
PROMPT_FILE = os.getenv('PROMPT_FILE')
LOCAL_LLM = os.getenv('LOCAL_LLM')

# Загрузка промта
try:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        logger.info(f"Промт загружен из {PROMPT_FILE}")
except Exception as e:
    logger.error(f"Ошибка загрузки промта: {e}")
    raise

async def check_spam(topic: str) -> bool:
    """Асинхронная проверка сообщения на спам"""
    try:
        formatted_prompt = prompt_template.format(question=topic)
        llm = ChatOllama(
            model=LOCAL_LLM,
            temperature=0
        )
        response = await llm.ainvoke([HumanMessage(content=formatted_prompt)])
        model_response = response.content.strip().upper()
        logger.debug(f'model_response={model_response}')
        print(f'model_response={model_response}')
        print(type(model_response))

        return  model_response == "SPAM"
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return False