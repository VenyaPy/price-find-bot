from telegram import (KeyboardButton,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup)

keyboard = [
            [KeyboardButton("Анализ товара🔎"), KeyboardButton("Как пользоваться❓")],
            [KeyboardButton("История запросов📒"), KeyboardButton("Связаться с поддержкой📞")]
        ]


keyboardMarkup = [
    [
        InlineKeyboardButton("Анализ товара🔎", callback_data="1"),
        InlineKeyboardButton("Вернуться назад🔙", callback_data="2")
    ]
]


keyboard_for_admin = [
    [KeyboardButton("Аналитика📈"), KeyboardButton("Реклама💵")],
    [KeyboardButton("Рассылка📢"), KeyboardButton("Пользовательское меню‍🤓")]
]

content_keyboard = [
    [InlineKeyboardButton("Отправить пост", callback_data='send_post')]
]


