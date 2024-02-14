from app.functionality.user.functions import *
from app.functionality.admin.functions import *
from telegram.ext import CallbackQueryHandler
from app.functionality.admin.functions import personal_menu


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
    elif text == "Пост🚀":
        await adv(update, context)
    elif text == "Написать пост✏️":
        return conv_handler
    elif text == "Удалить пост❌":
        await delete_message(update, context)
    elif text == "Отправить сейчас🌍":
        await send_message_to_all_users(update, context)
    elif text == "Вернуться в админ-меню👈":
        await admin_start(update, context)
    elif text == "Показать пост🔍":
        await show_post_with_button(update, context)
    elif text == "Подписки🤖":
        await public(update, context)
    elif text == "Активные паблики✅":
        await active_public(update, context)
    elif text == 'Паблик':
        await create_pub(update, context)
    elif text == "Назад👈":
        await admin_start(update, context)


# Функция для обработки кнопок
async def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "1":
        await request_product_name(update, context)
    elif data == "2":
        await start(update, context)


callback_query_handler = CallbackQueryHandler(handle_callback_query)
