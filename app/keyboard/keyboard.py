from app.functionality.user.functions import *
from telegram.ext import CallbackQueryHandler
from app.functionality.admin.posting import *
from app.functionality.admin.subscription import public, active_public
from app.functionality.admin.accesses import show_admin
from app.functionality.admin.analytics import users, emails, views
from app.functionality.admin.functions import analytic_menu, personal_menu, admin_menu
from app.functionality.user.history import history_requests, history_men, delete_history
from app.functionality.user.callback import callback
from app.functionality.admin.switcher import switch, enable_start, disable_start


# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: CallbackContext, check_admin=True):
    user_id = update.effective_chat.id
    text = update.message.text
    state = context.user_data.get('state')

    if check_admin and await is_admin(user_id):
        if text == "Пост🚀":
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
        elif text == "Назад👈":
            await admin_start(update, context)
        elif text == "Аналитика📂":
            await analytic_menu(update, context)
        elif text == "Пользователи🤖":
            await users(update, context)
        elif text == "EMAIL📧":
            await emails(update, context)
        elif text == "Просмотры👁️":
            await views(update, context)
        elif text == "Доступы🔒":
            await admin_menu(update, context)
        elif text == "Список администраторов✅":
            await show_admin(update, context)
        elif text == "Поддержка🧠":
            await callback(update, context)
        elif text == "Как пользоваться❓":
            await start(update, context)
        elif state == 'AWAITING_PRODUCT_NAME':
            await analyze_product(update, context)
        elif text == "История запросов📒":
            await history_men(update, context)
        elif text == "Пользовательское меню‍🤓":
            await personal_menu(update, context)
        elif text == "Показать историю👀":
            await history_requests(update, context)
        elif text == "Очистить историю❌":
            await delete_history(update, context)
        elif text == "Назад👈":
            await start_menu(update, context)
        elif text == "Проверить♻️":
            await subscription(update, context)
        elif text == "Тумблер⚠️":
            await switch(update, context)
        elif text == "Включить бота✅":
            await enable_start(update, context)
        elif text == "Отключить бота⛔":
            await disable_start(update, context)
    else:
        if not context.bot_data.get('is_bot_active', True):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Бот временно отключен.")
            return
        else:
            if text == "Поддержка🧠":
                await callback(update, context)
            elif text == "Как пользоваться❓":
                await start(update, context)
            elif state == 'AWAITING_PRODUCT_NAME':
                await analyze_product(update, context)
            elif text == "История запросов📒":
                await history_men(update, context)
            elif text == "Пользовательское меню‍🤓":
                await personal_menu(update, context)
            elif text == "Показать историю👀":
                await history_requests(update, context)
            elif text == "Очистить историю❌":
                await delete_history(update, context)
            elif text == "Назад👈":
                await start_menu(update, context)


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
