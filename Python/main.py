import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from spam_checker import check_spam
from dotenv import load_dotenv
from tools import block_user, delete_user_messages, forward_to_group

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
PROMPT_FILE = os.getenv('PROMPT_FILE')
SUBSCRIBERS_FILE = os.getenv('SUBSCRIBERS_FILE')  # Новый параметр для файла с подписчиками

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


LOG_DIR = os.getenv('LOG_DIR', 'logs')

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Обработчик для файла
file_handler = logging.FileHandler(
    filename=os.path.join(LOG_DIR, 'bot.log'),
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Загрузка промпта
try:
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
except Exception as e:
    logger.error(f"Ошибка чтения промпта {PROMPT_FILE}: {e}")
    prompt_template = ""

# Загрузка списка подписчиков
subscribers = set()
try:
    if SUBSCRIBERS_FILE:
        with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    subscribers.add(int(line))
        logger.info(f"Загружено {len(subscribers)} подписчиков")
    else:
        logger.warning("Файл подписчиков не указан в настройках")
except Exception as e:
    logger.error(f"Ошибка загрузки подписчиков: {e}")


@dp.message()
async def handle_message(message: types.Message):
    # Пропускаем сообщения без текста
    if not message.text:
        logger.info(f"Получено сообщение без текста (тип: {message.content_type})")
        return

    user_id = message.from_user.id
    logger.info(f"Сообщение от пользователя: {user_id}")
    logger.info(f"Проверка сообщения: {message.text[:50]}...")
    logger.info(f"message.from_user: {message.from_user}")

    # Проверяем наличие пользователя в списке подписчиков
    if user_id in subscribers:
        logger.info(f"Пользователь {user_id} есть в списке подписчиков, проверка спама пропущена")
        return

    # Проверка на спам для неподписанных пользователей
    logger.info(f"Проверка сообщения: {message.text[:50]}...")

    is_spam = await check_spam(message.text, prompt_template)
    logger.info(f"Результат проверки спама: {is_spam}")

    if is_spam:
        logger.warning("Обнаружен спам!")
        if TARGET_GROUP_ID:
            await forward_to_group(message, TARGET_GROUP_ID)
        else:
            logger.warning("ID целевой группы не указан")
        await delete_user_messages(message)
    else:
        logger.info("Сообщение не является спамом")


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Работа бота остановлена")