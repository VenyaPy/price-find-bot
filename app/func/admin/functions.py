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









