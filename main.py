import logging
from db import Start
from config import TOKEN
from app.keyboard.keyboard import handle_message, handle_callback_query
from telegram.ext import (ApplicationBuilder,
                          CallbackQueryHandler,
                          CommandHandler,
                          filters,
                          MessageHandler)
from app.functionality.user.parsing import analyt_handler
from app.functionality.admin.posting import conv_handler
from app.functionality.admin.subscription import add_conv_handler, del_conv_handler
from app.functionality.admin.accesses import admin_handler, adm_del_handler
from app.functionality.user.comparison import gpt_handler
from app.functionality.user.start import start


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

    application.add_handler(start_handler)
    application.add_handler(analyt_handler)
    application.add_handler(conv_handler)
    application.add_handler(admin_handler)
    application.add_handler(adm_del_handler)
    application.add_handler(gpt_handler)
    application.add_handler(add_conv_handler)
    application.add_handler(del_conv_handler)
    application.add_handler(callback_query_handler)
    application.add_handler(message_handler, group=1)

    application.run_polling()



