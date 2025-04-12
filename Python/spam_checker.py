import logging
from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

load_dotenv()

LOCAL_LLM = os.getenv('LOCAL_LLM')
print(f'LOCAL_LLM ={LOCAL_LLM }')

logger = logging.getLogger(__name__)

async def check_spam(topic: str) -> bool:
    prompt = """Ты - система определения спама в чатах Telegram. 
    Твоя задача - анализировать сообщения и определять, являются ли они спамом. 

    Характеристики спам-сообщений:
    1. Предложения быстрого заработка с нереалистично высокими суммами.
    2. Призывы к действию типа "пишите в личные сообщения", "ограниченное предложение".
    3. Намеренные орфографические ошибки или замена букв символами (например, "сOoбщение" вместо "сообщение").
    4. Неконкретные предложения работы без деталей.
    5. Обещания легкого заработка, "свободного графика" без объяснения сути работы.
    6. Использование эмодзи или необычных символов для привлечения внимания.
    7. Отсутствие контекста или связи с предыдущими сообщениями в чате.

    Проанализируй предоставленное сообщение и определи, является ли оно спамом на основе этих критериев. 

    Отвечай только "SPAM", если сообщение соответствует характеристикам спама, 
    или "NOT_SPAM", если это обычное сообщение. 
    Не добавляйте никаких дополнительных комментариев или объяснений.
    Вот текст сообщения: {question}"""
    try:
        # Инициализация локальной языковой модели с параметрами
        # local_llm = "llama3.2:3b-instruct-fp16"
        # local_llm = "deepseek-r1:14b"
        llm = ChatOllama(model=LOCAL_LLM, temperature=0)

        # Формирование запроса для LLM
        # print(f'text={topic}')
        prompt_formatted = prompt.format(question=topic)
        # Отправка запроса (сформированного промпта) в модель и получение ответа
        generation = llm.invoke([HumanMessage(content=prompt_formatted)])
        model_response = generation.content
        print(f'model_response={model_response}')
        print(type(model_response))

        return model_response == "SPAM"
    except Exception as e:
        logger.error(f"Ошибка при проверке на спам: {e}")
        return False