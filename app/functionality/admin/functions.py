from telegram import (Update,
                      ReplyKeyboardMarkup,
                      InlineKeyboardMarkup)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from db import get_all_user_chat_ids, add_public, find_public, show_public, delete_public
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция вызывающая главную панель администратора с клавиатурой
async def admin_start(update, context):
    reply_markup = ReplyKeyboardMarkup(keyboard_for_admin, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Над чем поработаем?",
                                   reply_markup=reply_markup)


# Функция возвращающая администратора в пользовательское меню
async def personal_menu(update: Update, context: CallbackContext):
    from app.functionality.user.functions import start
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в пользовательское меню!")
    await start(update, context, check_admin=False)


# Функция отправки рекламного поста, реализованная через ConversationHandler
TEXT_INPUT, PHOTO_INPUT, BUTTON_INFO = range(3)


# Функция вызывающая 5 кнопок: написать пост, показать пост, отправить сейчас, удалить пост, вернуться
async def adv(update: Update, context: CallbackContext):
    reply_mark = ReplyKeyboardMarkup(advertising_menu, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите опцию:",
                                   reply_markup=reply_mark)


# Введите текст сообщения:
async def start_add_message(update: Update, context: CallbackContext):
    await update.message.reply_text('Введите текст сообщения:')
    return TEXT_INPUT


# Сохранение состояния текста поста и запрос фото
async def receive_message_text(update: Update, context: CallbackContext):
    context.user_data['post_text'] = update.message.text
    await update.message.reply_text('Теперь отправьте фото для поста:')
    return PHOTO_INPUT


# Сохранение состояния фото и запрос url кнопки
async def receive_photo(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    context.user_data['post_photo_file_id'] = photo_file.file_id
    await update.message.reply_text('Сообщение с фото добавлено')
    await update.message.reply_text('Введите текст для кнопки и URL через пробел:')

    return BUTTON_INFO


# Сохранение кнопки
async def receive_button_info(update: Update, context: CallbackContext):
    try:
        text, url = update.message.text.split(' ', 1)  # Предполагаем, что текст и URL разделены пробелом
        context.user_data['button_text'] = text
        context.user_data['button_url'] = url
        await update.message.reply_text('Информация о кнопке получена.')
    except ValueError:
        await update.message.reply_text('Пожалуйста, отправьте текст и URL для кнопки, разделенные одним пробелом.')
        return BUTTON_INFO
    return ConversationHandler.END


# Функция для просмотра готового поста без отправки
async def show_post_with_button(update: Update, context: CallbackContext):
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data and 'button_text' in context.user_data and 'button_url' in context.user_data:
        keyboard = [[InlineKeyboardButton(context.user_data['button_text'], url=context.user_data['button_url'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=context.user_data['post_photo_file_id'],
                                     caption=context.user_data['post_text'],
                                     reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет сообщения или информации о кнопке")


# Отправка поста для всех пользователей, которые находятся в базе данных
async def send_message_to_all_users(update: Update, context: CallbackContext):
    chat_ids = get_all_user_chat_ids()
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data and 'button_text' in context.user_data and 'button_url' in context.user_data:
        for chat_id in chat_ids:
            keyboard = [[InlineKeyboardButton(context.user_data['button_text'], url=context.user_data['button_url'])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=context.user_data['post_photo_file_id'],
                                         caption=context.user_data['post_text'],
                                         reply_markup=reply_markup)
    else:
        await update.message.reply_text('Нет поста для отправки')


# Удаление поста и контекста
async def delete_message(update, context):
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data:
        del context.user_data['post_text']
        del context.user_data['post_photo_file_id']
        del context.user_data['button_text']
        del context.user_data['button_url']
        await update.message.reply_text('Пост удален.')
        return ConversationHandler.END
    else:
        await update.message.reply_text('Нет сохраненного поста для удаления.')


# Создание ConversationHandler для реализации этого диалога
conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Написать пост✏️'), start_add_message)],
    states={
        TEXT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message_text)],
        PHOTO_INPUT: [MessageHandler(filters.PHOTO, receive_photo)],
        BUTTON_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_button_info)]
    },
    fallbacks=[CommandHandler('cancel', delete_message)]
)


ID_PUB = 1
URL_PUB = 2


async def public(update: Update, context: CallbackContext):
    # Предполагается, что переменная pub_admin уже определена где-то в вашем коде
    reply_markup = ReplyKeyboardMarkup(pub_admin, resize_keyboard=True, one_time_keyboard=False)
    user_id = update.effective_chat.id
    await context.bot.send_message(text="Выберите функцию:",
                                   chat_id=user_id,
                                   reply_markup=reply_markup)


async def start_add_public(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ID паблика")
    return ID_PUB


async def add_pub_url(update: Update, context: CallbackContext):
    # Сохраняем ID в контексте беседы
    context.user_data['pub_id'] = update.message.text.strip()
    await update.message.reply_text("Теперь введите URL паблика")
    return URL_PUB


async def add_pub(update: Update, context: CallbackContext):
    # Извлекаем сохраненный ID из контекста беседы
    pub_id = context.user_data.get('pub_id')
    # Получаем URL из сообщения пользователя
    pub_url = update.message.text.strip()
    if not pub_url:
        await update.message.reply_text("URL паблика не может быть пустым. Попробуйте снова.")
        return URL_PUB
    try:
        add_public(pub_id, pub_url)
        await update.message.reply_text("Паблик успешно добавлен.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при добавлении паблика: {e}")
    return ConversationHandler.END


async def cancel_dd(update: Update, context: CallbackContext):
    await update.message.reply_text("Добавление паблика отменено.")
    return ConversationHandler.END  # Завершаем диалог


add_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Добавить паблик❗'), start_add_public)],
    states={
        ID_PUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_pub_url)],
        URL_PUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_pub)],
    },
    fallbacks=[CommandHandler('cancel', cancel_dd)],
)


async def active_public(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    mes = show_public()  # Получаем список пар (id, id_public)
    if not mes:  # Проверяем, не пустой ли список
        await context.bot.send_message(chat_id=chat_id, text="Извините, у вас ещё нет пабликов")
    else:
        # Преобразуем список пар в строку, где каждый элемент форматируется как "idX - URL"
        publics_info = "\n".join(f"id{public_id[0]} - {public_id[1]}" for public_id in mes)
        await context.bot.send_message(chat_id=chat_id, text=publics_info)




DELETE = 1  # Используем целое число для определения состояния


async def delete_publics(update: Update, context: CallbackContext):
    await update.message.reply_text("Выберите ID паблика для его удаления")
    return DELETE


async def delete(update: Update, context: CallbackContext):
    pub_id = update.message.text
    try:
        id_to_delete = int(pub_id)  # Преобразуем текст в целое число
        delete_public(id_to_delete)
        await update.message.reply_text("Паблик удален.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный числовой ID.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при удалении паблика: {e}")


async def cancel_del(update: Update, context: CallbackContext):
    await update.message.reply_text("Удаление паблика отменено.")
    return ConversationHandler.END


del_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Удалить паблик⛔'), delete_publics)],
    states={
        DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete)],
    },
    fallbacks=[CommandHandler('cancel', cancel_del)]  # Используем стандартную команду /cancel
)





















