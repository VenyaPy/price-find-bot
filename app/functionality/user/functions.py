import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InputMediaPhoto, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from app.scrap.scraperyandex import WebScraper
from app.scrap.wb import WebBrowser
from app.scrap.dns import DNS
from app.scrap.mvideo import Mvideo
import re
from db import save_user, save_requests, history, check_email, save_user_email, find_public, save_count, is_admin
from app.functionality.admin.functions import admin_start
from app.keyboard.inline import *
import time


# Главная команда /start
async def start(update: Update, context: CallbackContext, check_admin=True):
    user_id = update.effective_chat.id
    save_user(user_id)

    # Проверяем подписку пользователя
    if check_admin and await is_admin(user_id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, администратор!🖐️")
        await admin_start(update, context)
    else:
        publics = await find_public()
        subscribed = True
        for public in publics:
            chat_id = public['id_public']
            try:
                # Проверяем статус подписки пользователя
                status = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if status.status not in ['creator', 'administrator', 'member']:
                    subscribed = False
                    break  # Если пользователь не подписан на один из пабликов, прерываем проверку
            except Exception as e:
                print(f"Ошибка при проверке подписки пользователя {user_id} на паблик {chat_id}: {e}")
                subscribed = False
                break

        if subscribed:
            await main_start(update, context)
        else:
            await subscription(update, context)


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
    txt = ("Привет 🤚\n\nЯ — твой помощник в анализе цен на популярных маркетплейсах,"
            " включая Ozon, Wildberries, DNS и другие!"
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


executor = ThreadPoolExecutor(10)

# Константы состояний
AWAITING_EMAIL, AWAITING_PRODUCT_NAME = range(2)


async def start_email(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    if await check_email(user_id):
        await request_product_name(update, context)
        return AWAITING_PRODUCT_NAME
    else:
        await update.message.reply_text("Чтобы пользоваться данной функцией без ограничений - отправьте свой email")
        return AWAITING_EMAIL


async def save_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    user_id = update.effective_chat.id
    await save_user_email(user_id, email)
    # После сохранения email, запросите название товара
    await update.message.reply_text("Введи название товара для анализа:")
    return AWAITING_PRODUCT_NAME


async def request_product_name(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Введи название товара для анализа:")
    return AWAITING_PRODUCT_NAME


# Функция, вызываемая кнопкой АНАЛИЗ ТОВАРА
async def analyze_product(update: Update, context: CallbackContext) -> int:
    product_name = update.message.text.strip()  # Получаем название товара, удаляя лишние пробелы
    user_id = update.effective_chat.id
    chat_id = update.effective_chat.id

    # Запись запроса в историю запросов пользователя
    save_requests(user_id, product_name)  # Предполагаем, что эта функция существует и корректно работает
    await save_count()
    await context.bot.send_message(chat_id, "Ожидайте. Идёт получение цен...\n"
                                            "Обычно это не занимает больше 10-15 секунд😉")

    scraper = WebScraper()
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, lambda: perform_parsing(scraper, product_name))

    seen_stores = set()
    unique_results = []
    for store_name, price, link in results:
        if store_name not in seen_stores:
            unique_results.append((store_name, price, link))
            seen_stores.add(store_name)

    response_text = ""
    for index, (store_name, price, link) in enumerate(unique_results, start=1):
        formatted_store_name = store_name.title() if not store_name.isupper() else store_name
        price_numeric = int(re.sub(r'\D', '', price))
        price_formatted = f"{price_numeric:,.0f}".replace(",", ".").strip() + " ₽"
        response_text += f"{index}. {formatted_store_name}: <a href='{link}'>{price_formatted}</a>\n"

    if not response_text:
        response_text = "К сожалению, не удалось найти товар."

    await update.message.reply_text(response_text, parse_mode='HTML', disable_web_page_preview=True)
    return ConversationHandler.END


analyt_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Анализ товара🔎'), start_email)],
        states={
            AWAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_email)],
            AWAITING_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_product)],
        },
        fallbacks=[],
    )


# Запуск парсинга
def perform_parsing(scraper, product_name):
    scraper.open_page('https://market.yandex.ru/')
    scraper.search_product(product_name)
    time.sleep(5)  # Даем время для загрузки результатов поиска
    results = scraper.find_products()
    scraper.close_browser()

    # Фильтруем результаты и возвращаем их
    filtered_results = [
        (store_name, price, link)
        for store_name, price, link in results
        if price and link and 'Цена не найдена' not in price and 'Ссылка не найдена' not in link
    ]

    # Сортировка результатов по цене
    sorted_results = sorted(filtered_results,
                            key=lambda x: int(re.sub(r'\D', '', x[1])) if re.sub(r'\D', '', x[1]).isdigit() else float(
                                'inf'))

    return sorted_results




# Функция реализующая историю запросов с базы данных каждого пользователя
async def history_requests(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    chat_id = update.effective_chat.id
    mes = history(user_id)
    requests_list = mes.split(",")
    numbered_requests = "\n".join(f"{i + 1}. {request.strip()}"
                                  for i, request in enumerate(requests_list))
    await context.bot.send_message(text=numbered_requests, chat_id=chat_id)


# Функция связи с поддержкой
async def callback(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    call_text = 'Возник вопрос или проблема? 👌\nОпиши проблему сюда👇'
    contact_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Техническая поддержка", url="https://t.me/venyapopov")]
    ])

    await context.bot.send_message(chat_id=chat_id, text=call_text, reply_markup=contact_button)

