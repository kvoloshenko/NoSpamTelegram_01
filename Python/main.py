import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from spam_checker import check_spam
# from Simple_Request_Local_Model import check_spam
from spam_storage import save_spam_message
from dotenv import load_dotenv
from tools import block_user, delete_user_messages, forward_to_group

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
print(f'TARGET_GROUP_ID ={TARGET_GROUP_ID}')

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dp.message()
async def handle_message(message: types.Message):
    # TODO
    # if message.chat.type != 'supergroup' or message.is_topic_message:
    #     print(f'message.chat.type = {message.chat.type}')
    #     return

    if not message.text:
        logger.info(f"Получено сообщение без текста (тип: {message.content_type})")
        return  # Пропускаем обработку

    logger.info(f"Проверка сообщения: {message.text[:50]}...")

    # TODO
    is_spam = await check_spam(message.text)
    print(f'await check_spam({message.text})')
    print(f'is_spam={is_spam}')
    print(type(is_spam))
    # is_spam = False
    # is_spam = True

    if is_spam:
        # await message.reply("Внимание: это сообщение может быть спамом.")
        # TODO
        save_spam_message(
            sender_full_name=message.from_user.full_name,
            message_text=message.text
        )
        # Пересылка сообщения в другую группу
        if TARGET_GROUP_ID:
            await forward_to_group(message, TARGET_GROUP_ID)
        else:
            logger.warning("ID целевой группы не указан в .env")
        await delete_user_messages(message)
        # await block_user(message)
    else:
        logger.info(f"Сообщение не является спамом: {message.text[:50]}...")

async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал на завершение работы")
    finally:
        logger.info("Программа завершена")