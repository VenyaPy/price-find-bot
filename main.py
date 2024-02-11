import logging
from app.func.user.functions import *
from app.keyboard.keyboard import handle_message, handle_callback_query
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, CallbackQueryHandler)
from db import Start
from config import TOKEN
from app.func.admin.functions import *


# Проверка работоспособности базы данных
Start()

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Изменено с INFO на DEBUG для более подробного логирования
)

# Построение бота
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Создание обработчиков команд
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    callback_query_handler = CallbackQueryHandler(handle_callback_query)

    # Регистрация обработчиков в приложении
    application.add_handler(start_handler)
    application.add_handler(conv_handler)
    application.add_handler(message_handler)
    application.add_handler(callback_query_handler)


    # Запуск бота
    application.run_polling()



