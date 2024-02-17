from telegram import (Update,
                      ReplyKeyboardMarkup,
                      InlineKeyboardMarkup)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)


# Функция вызывающая главную панель администратора с клавиатурой
async def admin_start(update, context):
    reply_markup = ReplyKeyboardMarkup(keyboard_for_admin, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Основные функции👇",
                                   reply_markup=reply_markup)


# Функция возвращающая администратора в пользовательское меню
async def personal_menu(update: Update, context: CallbackContext):
    from app.functionality.user.functions import start
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в пользовательское меню!")
    await start(update, context, check_admin=False)


async def analytic_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(analytic, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=chat_id,
                                   text="Выберите опцию:",
                                   reply_markup=reply_markup)


async def admin_menu(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(admins, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите опцию",
                                   reply_markup=reply_markup)




















