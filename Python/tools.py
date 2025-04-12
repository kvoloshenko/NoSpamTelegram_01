import logging
from aiogram import types

logger = logging.getLogger(__name__)

async def block_user(message: types.Message) -> bool:
    """
    Блокирует пользователя в чате.
    """
    try:
        await message.chat.ban(user_id=message.from_user.id)
        logger.info(f"Пользователь {message.from_user.id} {message.from_user.full_name} заблокирован.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при блокировке: {e}")
        return False

async def delete_user_messages(message: types.Message) -> bool:
    """
    Удаляет текущее сообщение пользователя.
    """
    try:
        await message.delete()
        logger.info(f"Сообщение {message.message_id} удалено.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении: {e}")
        return False

async def forward_to_group(message: types.Message, target_chat_id: str) -> bool:
    """
    Пересылает сообщение в указанную группу/чат.
    """
    try:
        await message.bot.forward_message(
            chat_id=target_chat_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        logger.info(f"Сообщение {message.message_id} переслано в группу {target_chat_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при пересылке: {e}")
        return False