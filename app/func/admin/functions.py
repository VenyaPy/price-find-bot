from telegram import (Update,
                      InputMediaPhoto,
                      ReplyKeyboardMarkup)
from app.keyboard.inline import *

from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler
from db import (get_all_user_chat_ids,
                add_admin_message,
                delete_admin_message,
                get_admin_message,
                get_text)
import logging


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def admin_start(update, context):
    reply_markup = ReplyKeyboardMarkup(keyboard_for_admin, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Над чем поработаем?",
                                   reply_markup=reply_markup)


async def personal_menu(update: Update, context: CallbackContext):
    from app.func.user.functions import start
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в пользовательское меню!")
    await start(update, context, check_admin=False)


async def adv(update: Update, context: CallbackContext):
    reply_mark = ReplyKeyboardMarkup(advertising_menu, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите опцию:",
                                   reply_markup=reply_mark)


async def send_message_to_all_users(update: Update, context: CallbackContext):
    chat_ids = get_all_user_chat_ids()
    message_text = get_admin_message()
    if message_text:
        for chat_id in chat_ids:
            await context.bot.send_message(chat_id=chat_id, text=message_text)


TEXT_INPUT = 0


async def start_add_message(update: Update, context: CallbackContext):
    # Запрашиваем у пользователя текст сообщения
    await update.message.reply_text('Введите текст сообщения:')
    return TEXT_INPUT


async def receive_message_text(update: Update, context: CallbackContext):
    message_text = update.message.text

    if message_text:
        add_admin_message(message_text)
        await update.message.reply_text('Сообщение добавлено в базу данных.')
    else:
        await update.message.reply_text('Текст сообщения не может быть пустым.')

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Операция отменена.')
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Написать пост✏️'), start_add_message)],
    states={
        TEXT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message_text)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


async def show_text(update: Update, context: CallbackContext):
    txt = get_text()
    if txt:
        message_text = txt[0]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Сообщений нет. Сначала напишите пост.")


async def delete_message(update, context):
    delete_admin_message()
    await update.message.reply_text('Пост удален из базы данных')












