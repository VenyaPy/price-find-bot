from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from openai import AsyncOpenAI
from app.keyboard.inline import comparison_menu



# Константы состояний диалога
ITEM1, ITEM2 = range(2)


# Асинхронная функция для начала сравнения
async def start_comparison(update: Update, context: CallbackContext) -> int:
    item_text = await update.message.reply_text("1️⃣Введите первое название товара:")
    return ITEM1


# Асинхронная функция для обработки первого товара
async def item1(update: Update, context: CallbackContext) -> int:
    context.user_data['item1'] = update.message.text
    item_txt = await update.message.reply_text("2️⃣Введите второе название товара:")
    # Сохраняем message_id сообщения, которое нужно будет удалить позже
    context.user_data['item_txt_message_id'] = item_txt.message_id
    return ITEM2


# Асинхронная функция для обработки второго товара и вывода результата сравнения
async def item2(update: Update, context: CallbackContext) -> int:
    # Удаляем предыдущее сообщение, используя сохраненный message_id
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=context.user_data['item_txt_message_id'])
    reply_markup = ReplyKeyboardMarkup(comparison_menu, one_time_keyboard=False, resize_keyboard=True)

    item1 = context.user_data['item1']
    item2 = update.message.text

    process = await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Идёт процесс сравнения...♻️")
    comparison_result = await compare_items(item1, item2)

    await update.message.reply_text(comparison_result)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup,
                                   text="Что делаем дальше?🤔👇")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=process.message_id)
    return ConversationHandler.END


# Асинхронная функция сравнения товаров через ChatGPT
async def compare_items(item1, item2):
    client = AsyncOpenAI(
        api_key='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'
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content" : "Ты сравнивающая машина! Ты можешь сравнить всё что угодно, даже не совместимые вещи. Если это вещи объективно сравнимые - то без перечисления преимуществ ты в срочку пишешь преимущества одной над другой. Если эти вещи несравнимые, то ты субъективно рассуди, какая вещь будет лучше и почему, тут прояви фантазию в сравнении и примерах почему лучше одна вещь, а не другая. К примеру,  два телефона можно сравнить по характеристикам и другим параметрам. А тату-машинку и ракету Илона Маска нельзя объективно сравнить и ты рассуждаешь и фантазируешь. Условия: первое - не делай перечисления, пиши все просто текстом. Второе условие - обращайся на ты."},
            {'role': 'user', 'content': f"Сравни мне {item1} и {item2}."},
    ],
        temperature=0.5
    )
    english_text = response.choices[0].message.content
    return english_text


# Асинхронная функция для отмены диалога
async def cancel(update: Update, _: CallbackContext) -> int:
    await update.message.reply_text('Сравнение отменено.')
    return ConversationHandler.END


gpt_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('Сравнить🚀'), start_comparison)],
    states={
        ITEM1: [MessageHandler(filters.TEXT & ~filters.COMMAND, item1)],
        ITEM2: [MessageHandler(filters.TEXT & ~filters.COMMAND, item2)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

