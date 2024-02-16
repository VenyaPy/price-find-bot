from telegram import (Update)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from db import (show_admins,
                delete_admin,
                add_admin)


async def show_admin(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    admins_string = await show_admins()  # Получаем строку с администраторами
    if admins_string:
        requests_list = admins_string.split(",")
        admins = "\n".join(f"{i + 1}. {request.strip()}" for i, request in enumerate(requests_list))
    else:
        admins = "Список администраторов пуст."

    # Отправляем сообщение асинхронно
    await context.bot.send_message(chat_id=chat_id, text=admins)


ADD = 1  # Предполагается, что это состояние используется в ConversationHandler


async def start_admins(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ID администратора:")
    return ADD


async def add_admins(update: Update, context: CallbackContext):
    id_admin = update.message.text
    await add_admin(id_admin)
    await update.message.reply_text(f"Администратор с ID {id_admin} добавлен.")
    return ConversationHandler.END


admin_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Выдать доступ🔑'), start_admins)],
    states={
        ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admins)],
    },
    fallbacks=[]
)


DEL = 1


async def admins_id(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ID администратора для удаления:")
    return DEL


async def del_admins(update: Update, context: CallbackContext):
    id_admin = update.message.text
    await delete_admin(id_admin)
    await update.message.reply_text(f"Администратор с ID {id_admin} удален.")
    return ConversationHandler.END


adm_del_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Удалить админа🔒'), admins_id)],
    states={
        DEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_admins)],
    },
    fallbacks=[]
)