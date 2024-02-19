from telegram import Update, ReplyKeyboardMarkup
from app.keyboard.inline import *
from telegram.ext import CallbackContext


# Функция меню для вкл/откл бота
async def switch(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(switch_menu, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(text="Работа с ботом👇",
                                   reply_markup=reply_markup,
                                   chat_id=chat_id)


# Включение бота
async def enable_start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot_data['is_bot_active'] = True  # Устанавливаем флаг активности в True
    await context.bot.send_message(chat_id=user_id, text="Бот вновь активен!")


# Отключение бота
async def disable_start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    context.bot_data['is_bot_active'] = False  # Устанавливаем флаг активности в False
    await context.bot.send_message(chat_id=user_id, text="Бот временно отключен.")
