from config import OPENAI_API_KEY
from openai import AsyncOpenAI
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler,
                          CallbackContext)
from app.keyboard.inline import keyboard_comparison


# Константы состояний диалога
ITEM1, ITEM2 = range(2)


# Функция для повторения сравнения через кнопку
async def start_comparison_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    # Удаляем сообщение, на которое была нажата кнопка
    await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)

    # Отправляем новое сообщение и сохраняем его message_id для последующего редактирования
    message = await context.bot.send_message(chat_id=chat_id, text="🤖 Сравни мне ____ и ____\n\n👉 Напиши первую вещь для сравнения")
    context.user_data['comparison_message_id'] = message.message_id

    return ITEM1


# Асинхронная функция для начала сравнения
async def start_comparison(update: Update, context: CallbackContext):
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo="https://imgur.com/BIDKrR9")
    message = await update.message.reply_text("🤖 Сравни мне ____ и ____\n\n👉 Напиши первую вещь для сравнения")
    context.user_data['comparison_message_id'] = message.message_id
    return ITEM1


async def item1(update: Update, context: CallbackContext) -> int:
    first_item = update.message.text
    context.user_data['item1'] = first_item

    # Удаляем сообщение пользователя с первой вещью
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

    # Редактируем сообщение бота с обновленным текстом
    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data['comparison_message_id'],
                                        text=f"🤖 Сравни мне {first_item} и ____\n\n👉 Напиши вторую вещь для сравнения")
    return ITEM2


# Асинхронная функция для обработки второго товара и вывода результата сравнения
async def item2(update: Update, context: CallbackContext) -> int:
    second_item = update.message.text
    first_item = context.user_data['item1']

    # Удаляем сообщение пользователя со второй вещью
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

    # Редактируем сообщение бота с окончательным текстом сравнения
    comparison_message = f"🤖 Сравни мне {first_item} и {second_item}\n\nИдёт процесс сравнения...♻️"
    await context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data['comparison_message_id'],
                                        text=comparison_message)

    # Предположим, что compare_items - это ваша функция сравнения
    comparison_result = await compare_items(first_item,
                                            second_item)

    # Определите клавиатуру для дальнейших действий
    reply_markup = InlineKeyboardMarkup(keyboard_comparison)  # Убедитесь, что keyboard_comparison правильно определена

    # Удаляем сообщение с процессом сравнения
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=context.user_data['comparison_message_id'])

    # Отправляем результат сравнения с кнопками для дальнейших действий
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=comparison_result,
                                   reply_markup=reply_markup)

    return ConversationHandler.END


# Асинхронная функция сравнения товаров через ChatGPT
async def compare_items(item1, item2):
    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты сравнивающая машина! "
                                          "Ты можешь сравнить всё что угодно, даже не "
                                          "совместимые вещи. Если это вещи объективно "
                                          "сравнимые - то ты объективно по пунктам- по "
                                          "цифрам сравниваешь преимущества и недостатки. "
                                          "Если эти вещи несравнимые, то ты субъективно "
                                          "рассуди, какая вещь будет лучше и почему, тут "
                                          "прояви фантазию в сравнении и примерах почему "
                                          "лучше одна вещь, а не другая, но в этом случае "
                                          "без перечислений через цифры, все в одну строчку "
                                          "расписывай. К примеру,  два телефона можно сравнить "
                                          "по характеристикам и другим параметрам. "
                                          "А тату-машинку и ракету Илона Маска нельзя "
                                          "объективно сравнить и ты рассуждаешь и "
                                          "фантазируешь. Главное не говори про то, что "
                                          "это совершенно разные темы и тому подобное, "
                                          "сразу приступай к делу."},
            {'role': 'user', 'content': f"Сравни мне {item1} и {item2}."},
    ],
        temperature=0.4
    )
    english_text = response.choices[0].message.content
    return english_text


# Асинхронная функция для отмены диалога
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Сравнение отменено.')
    return ConversationHandler.END


gpt_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex('Сравнить🚀'), start_comparison),
        CallbackQueryHandler(start_comparison_callback, pattern='^repeat$')
    ],
    states={
        ITEM1: [MessageHandler(filters.TEXT & ~filters.COMMAND, item1)],
        ITEM2: [MessageHandler(filters.TEXT & ~filters.COMMAND, item2)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

