import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InputMediaPhoto, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from app.scrap.ozon import WebScraper
from app.scrap.wb import WebBrowser
from app.scrap.dns import DNS
from app.scrap.mvideo import Mvideo
import re
from db import save_user, save_requests, history
from config import admin
from app.func.admin.functions import admin_start
from app.keyboard.inline import *


async def start(update: Update, context: CallbackContext, check_admin=True):
    user_id = update.effective_chat.id
    save_user(user_id)

    if check_admin and user_id in admin:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, администратор!")
        await admin_start(update, context)
    else:
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


# Функция для запроса названия товара
async def request_product_name(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        chat_id = query.message.chat_id
        message = await context.bot.send_message(chat_id=chat_id, text="Введи название товара для анализа:")
    else:
        message = await update.message.reply_text("Введи название товара для анализа:")

    context.user_data['state'] = 'AWAITING_PRODUCT_NAME'
    context.user_data['message_id_to_edit'] = message.message_id


async def analyze_product(update: Update, context: CallbackContext):
    product_name = update.message.text
    user_id = update.effective_chat.id
    save_requests(user_id, new_request=product_name)

    chat_id = update.effective_chat.id
    message_id = context.user_data.get('message_id_to_edit')

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Ожидайте. Идёт получение цен...\nОбычно это не занимает больше 20-30 секунд😉"
    )

    scraper = WebScraper()
    scraper_2 = WebBrowser()
    scraper_3 = DNS()
    scraper_4 = Mvideo()

    loop = asyncio.get_running_loop()

    # Запуск всех задач параллельно
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

    # Преобразование результатов и сортировка
    sortable_results = []
    for name, (price, url) in zip(["Ozon", "Wildberries", "DNS", "М.Видео"], results):
        if price != 'Цена не найдена':
            # Удаляем нечисловые символы и преобразуем в число
            price_number = int(re.sub(r'\D', '', price))
            sortable_results.append((name, price_number, url))

    sortable_results.sort(key=lambda x: x[1])  # Сортировка по цене

    # Формирование ответа с форматированными ценами
    response_text = ""
    for name, price, url in sortable_results:
        formatted_price = f"{price:,}".replace(",", ".") + " ₽"  # Форматирование цены
        response_text += f"[Цена товара на {name}: {formatted_price}]({url})\n"  # Markdown ссылка

    if not response_text:
        response_text = "К сожалению, не удалось найти товар в указанных магазинах."

    await update.message.reply_text(response_text, parse_mode='Markdown')
    reply_markup = InlineKeyboardMarkup(keyboardMarkup)
    await update.message.reply_text("Спасибо!\n\nХочешь найти новый товар? Нажми «АНАЛИЗ ТОВАРА»",
                                    reply_markup=reply_markup)



def perform_parsing(scraper, url, product_name):
    scraper.open_page(url)
    scraper.search_product(product_name)
    price = scraper.find_price()
    product_url = scraper.show_url()
    scraper.close_browser()
    return price, product_url


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

