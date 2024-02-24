import asyncio
import time
import re
from db import save_requests, save_count, check_email, save_user_email
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (MessageHandler,
                          filters,
                          ConversationHandler,
                          CallbackQueryHandler,
                          CallbackContext)
from app.scraping.tech import WebScraper
from app.keyboard.inline import keyboard_analyze, parsing_menu


executor = ThreadPoolExecutor(10)

# Константы состояний
AWAITING_EMAIL, AWAITING_PRODUCT_NAME = range(2)


async def start_email_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    await context.bot.send_message(chat_id=chat_id, text="Введи название товара для анализа:")
    return AWAITING_PRODUCT_NAME


async def start_email(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_chat.id
    if await check_email(user_id):
        await request_product_name(update, context)
        return AWAITING_PRODUCT_NAME
    else:
        await update.message.reply_text("👮‍♂️Для доступа к этой функции нужно ввести свой EMAIL:\n\n"
                                        "1. Ваш адрес электронной почты используется исключительно "
                                        "для обеспечения безопасного доступа к функции и не будет передан третьим "
                                        "лицам или использован в коммерческих целях.\n"
                                        "2. Мы не отправляем нежелательную почту (спам). "
                                        "Ваш адрес электронной почты не будет использоваться для "
                                        "рассылки рекламных материалов.\n"
                                        "3. Мы строго следим за использованием информации о "
                                        "пользователях в соответствии с нашими политиками "
                                        "и законодательством о защите данных.\n\nВведите EMAIL ниже👇")
        return AWAITING_EMAIL


async def save_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    user_id = update.effective_chat.id
    await save_user_email(user_id, email)
    # После сохранения email, запросите название товара
    await update.message.reply_text("Введи название товара для анализа:")
    return AWAITING_PRODUCT_NAME


async def parsing(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(parsing_menu, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(reply_markup=reply_markup,
                                   chat_id=chat_id,
                                   text="Выбери категорию товаров👇")


async def request_product_name(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Введи название товара для анализа:")
    return AWAITING_PRODUCT_NAME


async def split_message(chat_id, text, context, reply_markup=None, max_length=9300):
    parts = []
    while len(text) > max_length:
        part = text[:max_length]
        last_newline = part.rfind('\n')
        if last_newline != -1:
            parts.append(part[:last_newline])
            text = text[last_newline+1:]
        else:
            parts.append(part)
            text = text[:max_length]
    parts.append(text)

    reply_markup = InlineKeyboardMarkup(keyboard_analyze)

    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            await context.bot.send_message(chat_id=chat_id, text=part, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await context.bot.send_message(chat_id=chat_id, text=part, parse_mode='HTML', disable_web_page_preview=True,
                                           reply_markup=reply_markup)


# Функция, вызываемая кнопкой АНАЛИЗ ТОВАРА
async def analyze_product(update: Update, context: CallbackContext) -> int:
    try:
        if not context.bot_data.get('is_bot_active', True):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Бот временно отключен.")

        product_name = update.message.text.strip()  # Получаем название товара, удаляя лишние пробелы
        user_id = update.effective_chat.id
        chat_id = update.effective_chat.id

        # Запись запроса в историю запросов пользователя
        save_requests(user_id, product_name)  # Предполагаем, что эта функция существует и корректно работает
        await save_count()
        # Отправляем фото и текст, сохраняем message_id этих сообщений
        photo_message = await context.bot.send_photo(chat_id=chat_id, photo="https://imgur.com/G1zON7g")
        text_message = await context.bot.send_message(chat_id, "Ожидайте. Идёт получение цен...♻️\n"
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
            response_text = ("Извини, не получилось найти товар😔\n"
                             "Возможно эта категория сейчас не обслуживается, но скоро мы это исправим🫡")

        reply_markup = InlineKeyboardMarkup(keyboard_analyze)

        if len(response_text) > 9300:
            await split_message(chat_id, response_text, context, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text=response_text, parse_mode='HTML',
                                           disable_web_page_preview=True, reply_markup=reply_markup)

        await context.bot.delete_message(chat_id=chat_id, message_id=photo_message.message_id)
        await context.bot.delete_message(chat_id=chat_id, message_id=text_message.message_id)
        return ConversationHandler.END

    except Exception as e:
        reply_markup = InlineKeyboardMarkup(keyboard_analyze)
        await context.bot.send_message(text="Извини, не получилось найти товар😔\n"
                                            "Возможно эта категория сейчас не обслуживается, но скоро мы это исправим🫡",
                                       chat_id=update.effective_chat.id,
                                       reply_markup=reply_markup)
        return ConversationHandler.END


analyt_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Техника и гаджеты🤖'), start_email),
                      CallbackQueryHandler(start_email_callback, pattern='^repeater$')],
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
    time.sleep(6)  # Даем время для загрузки результатов поиска
    results = scraper.find_products()
    time.sleep(6)
    scraper.close_browser()

    # Извлекаем цифры из названия продукта, указанного пользователем, и формируем множество
    user_product_numbers_set = set(re.findall(r'\d+', product_name))

    # Фильтруем результаты с учетом нового условия
    filtered_results = []
    for store_name, price, link, product_title in results:
        product_numbers_set = set(re.findall(r'\d+', product_title))


        # Проверяем совпадение множеств цифр и пересечение множеств слов
        if (user_product_numbers_set == product_numbers_set and
                price and link and
                'Цена не найдена' not in price and
                'Ссылка не найдена' not in link):
            filtered_results.append((store_name, price, link))

    # Сортировка результатов по цене
    sorted_results = sorted(filtered_results,
                            key=lambda x: int(re.sub(r'\D', '', x[1])) if re.sub(r'\D', '',
                                                                                 x[1]).isdigit() else float('inf'))

    return sorted_results