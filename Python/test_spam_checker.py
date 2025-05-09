import os
import datetime
import asyncio
from spam_checker import check_spam
import sys
import warnings
import aiohttp
from dotenv import load_dotenv

load_dotenv()
PROMPT_DIR = os.getenv('PROMPT_DIR')
SPAM_FILE = os.getenv('SPAM_FILE')
NO_SPAM_FILE = os.getenv('NO_SPAM_FILE')

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
        print(f"Ошибка чтения файла {filename}: {e}")
        return []


def generate_log_filename(prompt_name: str = "", suffix: str = "") -> str:
    """Генерация имени лог-файла с датой, временем и именем промпта"""
    now = datetime.datetime.now()
    name_part = f"_{prompt_name}" if prompt_name else ""
    return now.strftime(f"./Logs/Test_Log_%Y%m%d_%H%M{name_part}{suffix}.txt")


async def process_batch(test_file: str, expected_result: str, log_file, failed_log_file, prompt_template: str) -> int:
    """Обработка батча сообщений и запись результатов в логи"""
    messages = read_test_messages(test_file)
    error_count = 0
    for message in messages:
        try:
            # Проверка сообщения с текущим промптом
            is_spam = await check_spam(message, prompt_template)
            actual_result = "SPAM" if is_spam else "NOT_SPAM"

            # Формирование записи лога
            log_entry = f"ER={expected_result}, AR={actual_result}, ###{message}###"
            log_file.write(log_entry + "\n")

            # Подсчет ошибок при несовпадении
            if actual_result != expected_result:
                failed_log_file.write(log_entry + "\n")
                error_count += 1
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
    return error_count


async def main():
    """Основная функция для тестирования всех промптов"""
    # Проверка существования директории с промптами

    if not os.path.exists(PROMPT_DIR):
        print(f"Директория {PROMPT_DIR} не найдена")
        return

    # Получение списка промптов
    prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith('.txt')]
    if not prompt_files:
        print("Не найдено промптов в директории Prompts")
        return

    # Создание лог-файлов STATS
    stats_filename = generate_log_filename("", "_STATS")

    # Обработка каждого промпта
    for prompt_file in prompt_files:
        prompt_path = os.path.join(PROMPT_DIR, prompt_file)
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                print(f'prompt_path ={prompt_path}')
                prompt_template = f.read()
            prompt_name = os.path.splitext(prompt_file)[0]
        except Exception as e:
            print(f"Ошибка чтения промпта {prompt_file}: {e}")
            continue

        # Создание лог-файлов
        log_filename = generate_log_filename(prompt_name, "")
        failed_log_filename = generate_log_filename(prompt_name, "_FAILED")
        # stats_filename = generate_log_filename(prompt_name, "_STATS")
        # stats_filename = generate_log_filename("", "_STATS")

        async with aiohttp.ClientSession() as session:
            try:
                with open(log_filename, 'w', encoding='utf-8') as log_file, \
                        open(failed_log_filename, 'w', encoding='utf-8') as failed_log_file:

                    # Тестирование SPAM и NOT_SPAM

                    spam_errors = await process_batch(
                        SPAM_FILE, "SPAM", log_file, failed_log_file, prompt_template
                    )
                    not_spam_errors = await process_batch(
                        NO_SPAM_FILE, "NOT_SPAM", log_file, failed_log_file, prompt_template
                    )
                    total_errors = spam_errors + not_spam_errors

            except Exception as e:
                print(f"Ошибка работы с логами для {prompt_name}: {e}")
                continue

        # Запись статистики
        try:
            with open(stats_filename, 'a', encoding='utf-8') as stats_file:
                stats_file.write(f"Промпт: {prompt_name}\nОшибок: {total_errors}\n")
            print(f"Статистика для {prompt_name} сохранена в {stats_filename}")
        except Exception as e:
            print(f"Ошибка записи статистики для {prompt_name}: {e}")


if __name__ == "__main__":
    asyncio.run(main())