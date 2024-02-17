from telegram import (Update)
from app.keyboard.inline import *
from telegram.ext import (CallbackContext)
from db import (show_user,
                show_emails,
                show_views)



async def users(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    mes = await show_user()
    requests_list = mes.split(",")

    numbered_requests = "\n".join(f"{i + 1}. {request.strip()}"
                                  for i, request in enumerate(requests_list))

    # Отправляем сообщение асинхронно
    await context.bot.send_message(chat_id=chat_id, text=numbered_requests)


async def emails(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    mes = await show_emails()
    requests_list = mes.split(",")

    email = "\n".join(f"{i + 1}. {request.strip()}"
                                  for i, request in enumerate(requests_list))

    # Отправляем сообщение асинхронно
    await context.bot.send_message(chat_id=chat_id, text=email)


async def views(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    views_count = await show_views()
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"✅ Анализом товаров пользовались: {views_count} раз")