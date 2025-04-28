import os
import datetime
import asyncio
from spam_checker_01 import check_spam, prompt_template
import asyncio
import sys
import warnings
import aiohttp

warnings.filterwarnings("ignore", category=RuntimeWarning, module="asyncio")

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



def read_test_messages(filename: str) -> list[str]:
    """Чтение тестовых сообщений из файла с разделителем ###"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return [msg.strip() for msg in content.split('###') if msg.strip()]
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []


def generate_log_filename() -> str:
    """Генерация имени лог-файла с текущей датой и временем"""
    now = datetime.datetime.now()
    return now.strftime("Test_Log_%Y%m%d_%H%M.txt")


async def process_batch(test_file: str, expected_result: str, log_file):
    """Обработка батча сообщений и запись результатов"""
    messages = read_test_messages(test_file)
    for message in messages:
        try:
            # Форматирование промта
            formatted_prompt = prompt_template.format(question=message)

            # Получение результата от модели
            is_spam = await check_spam(message)
            actual_result = "SPAM" if is_spam else "NOT_SPAM"

            # Формирование записи лога
            # log_entry = f"""prompt = f\"\"\"{formatted_prompt}\"\"\"
            log_entry = f"""ER={expected_result}, AR={actual_result}, ###{message}###"""
            log_file.write(log_entry + "\n")
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")



async def main():
    """Основная асинхронная функция тестирования"""
    log_filename = generate_log_filename()

    async with aiohttp.ClientSession() as session:

        with open(log_filename, 'w', encoding='utf-8') as log_file:
            # Обработка SPAM-сообщений
            await process_batch("Test_SPAM_01.txt", "SPAM", log_file)

            # Обработка NOT_SPAM-сообщений
            await process_batch("Test_NO_SPAM_01.txt", "NOT_SPAM", log_file)


if __name__ == "__main__":
    asyncio.run(main())