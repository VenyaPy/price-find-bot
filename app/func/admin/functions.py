from telegram import (Update,
                      InputMediaPhoto,
                      ReplyKeyboardMarkup)
from app.keyboard.inline import *

from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler
from db import get_all_user_chat_ids
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


AWAITING_POST_TEXT = 1


async def start_adv(update: Update, context: CallbackContext):
    logger.info(f"User {update.effective_user.id} started advertisement conversation.")
    await update.message.reply_text("Введите текст поста:")
    return AWAITING_POST_TEXT  # Переходим в состояние ожидания текста поста


async def receive_post_text(update: Update, context: CallbackContext):
    message = update.message.text  # Получаем текст поста от пользователя
    if not message:  # Проверяем, что сообщение не пустое
        logger.warning(f"Received empty message text from user {update.effective_user.id}.")
        await update.message.reply_text("Получено пустое сообщение. Пожалуйста, введите текст поста.")
        return AWAITING_POST_TEXT  # Возвращаем пользователя к состоянию ввода текста

    user_ids = get_all_user_chat_ids()
    logger.info(f"Sending post to users: {user_ids}")
    for user_id in user_ids:
        if message:  # Дополнительная проверка, на случай изменений в логике
            await context.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Sent message to {user_id}")
        else:
            logger.error(f"Tried to send empty message to {user_id}")
    await update.message.reply_text("Пост успешно отправлен всем пользователям.")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f"User {user.first_name} ({user.id}) canceled the conversation.")
    await update.message.reply_text('Отменено.')
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start_adv', start_adv)],
    states={
        AWAITING_POST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_post_text)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)





