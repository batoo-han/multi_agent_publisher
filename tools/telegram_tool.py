import logging
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramTool:
    """
    Утилита для отправки сообщений и фото через Telegram Bot API.
    """

    def __init__(self, token: str):
        self.token = token

    async def send_message(self, chat_id: int, text: str):
        """
        Отправляет текстовое сообщение в указанный чат.

        :param chat_id: ID чата или канала
        :param text: Текст сообщения (Markdown разрешен)
        :return: telegram.Message
        """
        request = HTTPXRequest()
        bot = Bot(token=self.token, request=request)
        try:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown'
            )
            logger.info("Message sent [chat_id=%s, message_id=%s]", chat_id, msg.message_id)
            return msg
        except TelegramError as e:
            logger.error("Error sending message: %s", e)
            raise
        finally:
            await request.shutdown()

    async def send_photo(self, chat_id: int, photo_url: str, caption: str = None):
        """
        Отправляет фото по URL в указанный чат.

        :param chat_id: ID чата или канала
        :param photo_url: Ссылка на изображение
        :param caption: Подпись к изображению (Markdown разрешен)
        :return: telegram.Message
        """
        request = HTTPXRequest()
        bot = Bot(token=self.token, request=request)
        try:
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption or '',
                parse_mode='Markdown'
            )
            logger.info("Photo sent [chat_id=%s, message_id=%s]", chat_id, msg.message_id)
            return msg
        except TelegramError as e:
            logger.error("Error sending photo: %s", e)
            raise
        finally:
            await request.shutdown()