import logging

from app.func.user.functions import *
from app.func.admin.functions import *
from telegram.ext import CallbackQueryHandler
from app.func.admin.functions import personal_menu
from app.func.admin.adv import *



# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    state = context.user_data.get('state')

    if text == "Связаться с поддержкой📞":
        await callback(update, context)
    elif text == "Как пользоваться❓":
        await start(update, context)
    elif text == "Анализ товара🔎":
        await request_product_name(update, context)
    elif state == 'AWAITING_PRODUCT_NAME':
        await analyze_product(update, context)
    elif text == "История запросов📒":
        await history_requests(update, context)
    elif text == "Пользовательское меню‍🤓":
        await personal_menu(update, context)
    elif text == "Реклама💵":
        await start_adv(update, context)


# Функция перенаправления кнопок Анализ и Вернуться
async def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "1":
        await request_product_name(update, context)
    elif data == "2":
        await start(update, context)


callback_query_handler = CallbackQueryHandler(handle_callback_query)
