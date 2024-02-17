from telegram import (Update,
                      ReplyKeyboardMarkup)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from db import (add_public,
                show_public,
                delete_public)


ID_PUB = 1
URL_PUB = 2


async def public(update: Update, context: CallbackContext):
    # Предполагается, что переменная pub_admin уже определена где-то в вашем коде
    reply_markup = ReplyKeyboardMarkup(pub_admin, resize_keyboard=True, one_time_keyboard=False)
    user_id = update.effective_chat.id
    await context.bot.send_message(text="Выберите функцию:",
                                   chat_id=user_id,
                                   reply_markup=reply_markup)


async def start_add_public(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ID паблика")
    return ID_PUB


async def add_pub_url(update: Update, context: CallbackContext):
    # Сохраняем ID в контексте беседы
    context.user_data['pub_id'] = update.message.text.strip()
    await update.message.reply_text("Теперь введите URL паблика")
    return URL_PUB


async def add_pub(update: Update, context: CallbackContext):
    # Извлекаем сохраненный ID из контекста беседы
    pub_id = context.user_data.get('pub_id')
    # Получаем URL из сообщения пользователя
    pub_url = update.message.text.strip()
    if not pub_url:
        await update.message.reply_text("URL паблика не может быть пустым. Попробуйте снова.")
        return URL_PUB
    try:
        add_public(pub_id, pub_url)
        await update.message.reply_text("Паблик успешно добавлен.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при добавлении паблика: {e}")
    return ConversationHandler.END


async def cancel_dd(update: Update, context: CallbackContext):
    await update.message.reply_text("Добавление паблика отменено.")
    return ConversationHandler.END  # Завершаем диалог


add_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Добавить паблик❗'), start_add_public)],
    states={
        ID_PUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_pub_url)],
        URL_PUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_pub)],
    },
    fallbacks=[CommandHandler('cancel', cancel_dd)],
)


async def active_public(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    mes = show_public()  # Получаем список пар (id, id_public)
    if not mes:  # Проверяем, не пустой ли список
        await context.bot.send_message(chat_id=chat_id, text="Извините, у вас ещё нет пабликов")
    else:
        # Преобразуем список пар в строку, где каждый элемент форматируется как "idX - URL"
        publics_info = "\n".join(f"id{public_id[0]} - {public_id[1]}" for public_id in mes)
        await context.bot.send_message(chat_id=chat_id, text=publics_info)


DELETE = 1  # Используем целое число для определения состояния


async def delete_publics(update: Update, context: CallbackContext):
    await update.message.reply_text("Выберите ID паблика для его удаления")
    return DELETE


async def delete(update: Update, context: CallbackContext):
    pub_id = update.message.text
    try:
        id_to_delete = int(pub_id)  # Преобразуем текст в целое число
        delete_public(id_to_delete)
        await update.message.reply_text("Паблик удален.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный числовой ID.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при удалении паблика: {e}")


async def cancel_del(update: Update, context: CallbackContext):
    await update.message.reply_text("Удаление паблика отменено.")
    return ConversationHandler.END


del_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Удалить паблик⛔'), delete_publics)],
    states={
        DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete)],
    },
    fallbacks=[CommandHandler('cancel', cancel_del)]  # Используем стандартную команду /cancel
)