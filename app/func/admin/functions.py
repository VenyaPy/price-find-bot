from telegram import (Update,
                      ReplyKeyboardMarkup,
                      InlineKeyboardMarkup)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler)
from db import (get_all_user_chat_ids,)


# Функция вызывающая главную панель администратора с клавиатурой
async def admin_start(update, context):
    reply_markup = ReplyKeyboardMarkup(keyboard_for_admin, resize_keyboard=True, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Над чем поработаем?",
                                   reply_markup=reply_markup)


# Функция возвращающая администратора в пользовательское меню
async def personal_menu(update: Update, context: CallbackContext):
    from app.func.user.functions import start
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















