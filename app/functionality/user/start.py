from db import save_user, find_public, is_admin
from telegram import (Update,
                      InputMediaPhoto,
                      ReplyKeyboardMarkup,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import CallbackContext
from app.functionality.admin.admin_start import admin_start
from app.keyboard.inline import keyboard


async def start_menu(update: Update, context: CallbackContext, check_admin=True):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(reply_markup=reply_markup,
                                   chat_id=chat_id,
                                   text="Выбери функцию:")


# Главная функция /start
async def start(update: Update, context: CallbackContext, check_admin=True):
    user_id = update.effective_chat.id
    save_user(user_id)  # Предполагаемая функция для сохранения информации о пользователе

    # Запускаем проверку на работоспособность бота (определяет админ в своей панели switcher)
    if not context.bot_data.get('is_bot_active', True):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Бот временно отключен.")
        return

    # Продолжение логики команды start
    if check_admin and await is_admin(user_id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, администратор!🖐️")
        await admin_start(update, context)  # Предполагаемая функция для специфической логики администратора
    else:
        publics = await find_public()  # Предполагаемая функция для получения пабликов
        subscribed = True
        for public in publics:
            chat_id = public['id_public']
            try:
                status = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if status.status not in ['creator', 'administrator', 'member']:
                    subscribed = False
                    break
            except Exception as e:
                print(f"Ошибка при проверке подписки пользователя {user_id} на паблик {chat_id}: {e}")
                subscribed = False
                break

        if subscribed:
            await main_start(update, context)  # Предполагаемая функция основной логики старта
        else:
            await subscription(update, context)  # Предполагаемая функция для управления подписками


# Создание кнопок для подписки
async def generate_start(context: CallbackContext):
    # Получаем список пабликов из базы данных асинхронно
    publics = await find_public()
    # Генерируем клавиатуру
    keyboard_publics = [
        [InlineKeyboardButton(text=f"Подпишись👈", url=public['url'])]
        for public in publics
    ]
    return InlineKeyboardMarkup(keyboard_publics)


# Подписка на паблики
async def subscription(update: Update, context: CallbackContext):
    # Повторно отправляем клавиатуру для подписки
    reply_markup = await generate_start(context)
    await update.message.reply_text(
        text="Привет! Подпишись на паблики, чтобы использовать этого бота😉",
        reply_markup=reply_markup
    )


async def main_start(update: Update, context: CallbackContext):
    txt = ("Привет 🤚\n\nЯ — твой помощник в анализе цен на популярных маркетплейсах!"
            "\n\nДавай покажу, как мной пользоваться 👇")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)

    # Формирование списка изображений для альбома
    media_group = [
        InputMediaPhoto('https://i.imgur.com/rDXKI9X.jpeg'),
        InputMediaPhoto('https://i.imgur.com/0qgWiNS.jpeg'),
        InputMediaPhoto('https://i.imgur.com/UKhgEuY.jpeg'),
        InputMediaPhoto('https://i.imgur.com/Dv5OIRp.jpeg'),
        InputMediaPhoto('https://i.imgur.com/nIWPAS8.jpeg')
    ]

    # Отправка альбома
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Отправка сообщения с клавиатурой
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выбери кнопку:",
                                   reply_markup=reply_markup)
