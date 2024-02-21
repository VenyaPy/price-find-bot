from app.keyboard.inline import keyboard_for_admin, analytic, admins
from telegram import (Update,
                      ReplyKeyboardMarkup)
from telegram.ext import CallbackContext


# Функция вызывающая главную панель администратора с клавиатурой
async def admin_start(update, context):
    reply_markup = ReplyKeyboardMarkup(keyboard_for_admin, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Основные функции👇",
                                   reply_markup=reply_markup)


# Функция возвращающая администратора в пользовательское меню
async def personal_menu(update: Update, context: CallbackContext):
    from app.functionality.user.start import start_menu
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в пользовательское меню!")
    await start_menu(update, context, check_admin=False)


async def analytic_menu(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(analytic, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_photo(chat_id=chat_id,
                                 photo="https://imgur.com/AeN1Wx2")
    await context.bot.send_message(chat_id=chat_id,
                                   text="Аналитическое меню бота👇",
                                   reply_markup=reply_markup)


async def admin_menu(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(admins, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo="https://imgur.com/UyHC5Zo")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Доступы\nТы можешь добавить или удалить администратора👇",
                                   reply_markup=reply_markup)




















