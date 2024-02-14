from app.functionality.user.functions import *
from app.keyboard.keyboard import handle_message, handle_callback_query
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler)
from db import Start
from config import TOKEN
from app.functionality.admin.functions import *
import logging


# Проверка работоспособности базы данных
Start()


# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Построение бота
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    callback_query_handler = CallbackQueryHandler(handle_callback_query)

    application.add_handler(start_handler)  # Предполагается, что он не конфликтует с ConversationHandler
    application.add_handler(conv_handler)  # Группа не указана, по умолчанию = 0
    application.add_handler(
        add_conv_handler)  # Группа не указана, по умолчанию = 0, порядок добавления определяет приоритет
    application.add_handler(del_conv_handler)  # То же, что выше
    application.add_handler(
        callback_query_handler)  # Может быть в любой группе, не конфликтует с текстовыми сообщениями
    application.add_handler(message_handler,
                            group=1)  # Более низкий приоритет, чтобы не блокировать ConversationHandlerы

    application.run_polling()



