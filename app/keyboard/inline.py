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
    [KeyboardButton("Пользовательское меню‍🤓")]
]

advertising_menu = [
    [KeyboardButton("Написать пост✏️"), KeyboardButton("Показать пост🔍")],
    [KeyboardButton("Отправить сейчас🌍"), KeyboardButton("Удалить пост❌")],
    [KeyboardButton("Вернуться в админ-меню🔙")],
]



