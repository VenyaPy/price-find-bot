from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


# Функция связи с поддержкой
async def callback(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    call_text = 'Возник вопрос или проблема? 👌\nОпиши проблему сюда👇'
    contact_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Техническая поддержка", url="https://t.me/venyapopov")]
    ])

    await context.bot.send_message(chat_id=chat_id, text=call_text, reply_markup=contact_button)