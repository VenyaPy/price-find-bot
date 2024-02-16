import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InputMediaPhoto, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from app.scrap.ozon import WebScraper
from app.scrap.wb import WebBrowser
from app.scrap.dns import DNS
from app.scrap.mvideo import Mvideo
import re
from db import save_user, save_requests, history, check_email, save_user_email, find_public, save_count, is_admin
from app.functionality.admin.functions import admin_start
from app.keyboard.inline import *


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
    await save_count()
    product_name = update.message.text
    user_id = update.effective_chat.id
    save_requests(user_id, new_request=product_name)

    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text="Ожидайте. Идёт получение цен...\nОбычно это не занимает больше 20-30 секунд😉"
    )

    # Запуск парсинга сайтов
    scraper = WebScraper()
    scraper_2 = WebBrowser()
    scraper_3 = DNS()
    scraper_4 = Mvideo()

    loop = asyncio.get_running_loop()

    # Запуск всех задач параллельно для ускоренного парсинга сайтов
    tasks = [
        loop.run_in_executor(executor, lambda: perform_parsing(scraper,
                                                               'https://www.ozon.ru/', product_name)),
        loop.run_in_executor(executor, lambda: perform_parsing(scraper_2,
                                                               'https://www.wildberries.ru/', product_name)),
        loop.run_in_executor(executor, lambda: perform_parsing(scraper_3,
                                                               'https://www.dns-shop.ru/', product_name)),
        loop.run_in_executor(executor, lambda: perform_parsing(scraper_4,
                                                               'https://www.mvideo.ru/', product_name))
    ]

    # Ожидание завершения всех задач
    results = await asyncio.gather(*tasks)

    # Преобразование результатов
    sortable_results = []
    for name, (price, url) in zip(["Ozon", "Wildberries", "DNS", "М.Видео"], results):
        if price != 'Цена не найдена':
            # Удаляем нечисловые символы и преобразуем в число
            price_number = int(re.sub(r'\D', '', price))
            sortable_results.append((name, price_number, url))

    # Сортировка от меньшей цены к большей
    sortable_results.sort(key=lambda x: x[1])

    # Формирование ответа с форматированными ценами
    response_text = ""
    for name, price, url in sortable_results:
        formatted_price = f"{price:,}".replace(",", ".") + " ₽"  # Форматирование цены
        response_text += f"[Цена товара на {name}: {formatted_price}]({url})\n"  # Гипперссылка

    if not response_text:
        response_text = "К сожалению, не удалось найти товар в указанных магазинах."

    await update.message.reply_text(response_text, parse_mode='Markdown')
    reply_markup = InlineKeyboardMarkup(keyboardMarkup)
    await update.message.reply_text("Спасибо!\n\nХочешь найти новый товар? Нажми «АНАЛИЗ ТОВАРА»",
                                    reply_markup=reply_markup)
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
def perform_parsing(scraper, url, product_name):
    scraper.open_page(url)
    scraper.search_product(product_name)
    price = scraper.find_price()
    product_url = scraper.show_url()
    scraper.close_browser()
    return price, product_url


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

