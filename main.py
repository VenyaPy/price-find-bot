from app.func.user.functions import *
from app.keyboard.keyboard import handle_message, handle_callback_query
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler)
from db import Start
from config import TOKEN
from app.func.admin.functions import *
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

    # Регистрация обработчиков в приложении
    application.add_handler(start_handler)
    application.add_handler(conv_handler)  # Добавьте сначала conv_handler
    application.add_handler(message_handler, group=1)  # Добавьте message_handler в группу с более низким приоритетом
    application.add_handler(callback_query_handler)

    application.run_polling()



