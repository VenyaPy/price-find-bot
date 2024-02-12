from telegram import (Update,
                      InputMediaPhoto,
                      ReplyKeyboardMarkup)
from app.keyboard.inline import *

from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, ConversationHandler
from db import (get_all_user_chat_ids,
                add_admin_message,
                delete_admin_message,
                get_admin_message,
                get_text)
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


TEXT_INPUT, PHOTO_INPUT = range(2)


async def adv(update: Update, context: CallbackContext):
    reply_mark = ReplyKeyboardMarkup(advertising_menu, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите опцию:",
                                   reply_markup=reply_mark)


async def start_add_message(update: Update, context: CallbackContext):
    # Запрашиваем у пользователя текст сообщения
    await update.message.reply_text('Введите текст сообщения:')
    return TEXT_INPUT


async def receive_message_text(update: Update, context: CallbackContext):
    context.user_data['post_text'] = update.message.text
    await update.message.reply_text('Теперь отправьте фото для поста:')
    return PHOTO_INPUT


async def receive_photo(update: Update, context: CallbackContext):
    try:
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive("user_photo.jpg")
        context.user_data['post_photo_file_id'] = photo_file.file_id
        await update.message.reply_text('Сообщение с фото добавлено')
        logger.info("Фото получено и сохранено")
    except Exception as e:
        logger.error(f"Ошибка при получении фото: {e}")
    return ConversationHandler.END


async def show_post(update: Update, context: CallbackContext):
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=context.user_data['post_photo_file_id'],
                                     caption=context.user_data['post_text'])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет сообщения")


async def send_message_to_all_users(update: Update, context: CallbackContext):
    chat_ids = get_all_user_chat_ids()
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data:
        for chat_id in chat_ids:
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=context.user_data['post_photo_file_id'],
                                         caption=context.user_data['post_text'])
    else:
        await update.message.reply_text('Спасибо за то, что вы используете данный бот')


async def delete_message(update, context):
    if 'post_text' in context.user_data and 'post_photo_file_id' in context.user_data:
        del context.user_data['post_text']
        del context.user_data['post_photo_file_id']
        await update.message.reply_text('Пост удален.')
    else:
        await update.message.reply_text('Нет сохраненного поста для удаления.')


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Операция отменена.')
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Написать пост✏️'), start_add_message)],
    states={
        TEXT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message_text)],
        PHOTO_INPUT: [MessageHandler(filters.PHOTO, receive_photo)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)















