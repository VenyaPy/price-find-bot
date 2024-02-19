from db import history
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from db import delete_user_history
from app.keyboard.inline import history_menu


async def history_men(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(history_menu, resize_keyboard=True, one_time_keyboard=False)
    text = "Управление историей запросов👇"
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo="https://imgur.com/sXV0OiC")
    await context.bot.send_message(text=text,
                                   reply_markup=reply_markup,
                                   chat_id=update.effective_chat.id)




# Функция реализующая историю запросов с базы данных каждого пользователя
async def history_requests(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    chat_id = update.effective_chat.id
    if history(user_id) is not None:
        mes = history(user_id)
        requests_list = mes.split(",")
        numbered_requests = "\n".join(f"{i + 1}. {request.strip()}"
                                      for i, request in enumerate(requests_list))
        await context.bot.send_message(text=numbered_requests, chat_id=chat_id)
    else:
        await context.bot.send_message(chat_id=user_id, text="История пока пуста")


async def delete_history(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    await delete_user_history(user_id)
    await context.bot.send_message(text="История очищена",
                                   chat_id=user_id)