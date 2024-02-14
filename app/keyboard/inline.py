from telegram import (KeyboardButton,
                      InlineKeyboardButton)

keyboard = [
            [KeyboardButton("Анализ товара🔎"), KeyboardButton("Как пользоваться❓")],
            [KeyboardButton("История запросов📒"), KeyboardButton("Связаться с поддержкой📞")]
        ]


keyboardMarkup = [
    [
        InlineKeyboardButton("Новый анализ🔎", callback_data="1"),
        InlineKeyboardButton("Вернуться назад👈", callback_data="2")
    ]
]


keyboard_for_admin = [
    [KeyboardButton("Аналитика📂"), KeyboardButton("Пост🚀")],
    [KeyboardButton("Подписки🤖"), KeyboardButton("Функция🔒")],
    [KeyboardButton("Пользовательское меню‍🤓")]
]

advertising_menu = [
    [KeyboardButton("Написать пост✏️"), KeyboardButton("Показать пост🔍")],
    [KeyboardButton("Отправить сейчас🌍"), KeyboardButton("Удалить пост❌")],
    [KeyboardButton("Вернуться в админ-меню👈")],
]

pub_admin = [
    [KeyboardButton("Активные паблики✅"), KeyboardButton("Добавить паблик❗")],
    [KeyboardButton("Удалить паблик⛔"), KeyboardButton("Проверить♻️")],
    [KeyboardButton("Назад👈")]
]



