from telegram import (KeyboardButton,
                      InlineKeyboardButton)


keyboard = [
            [KeyboardButton("Анализ товара🤖")],
            [KeyboardButton("Сравнить🚀")],
            [KeyboardButton("История запросов📒"), KeyboardButton("Поддержка🧠")]
        ]


keyboard_analyze = [
    [
        InlineKeyboardButton("Повторить🔎", callback_data="repeater"),
        InlineKeyboardButton("Вернуться👈", callback_data="2")
    ]
]


keyboard_comparison = [
    [
        InlineKeyboardButton("Повторить🔎", callback_data="repeat"),
        InlineKeyboardButton("Вернуться👈", callback_data="4")
    ]
]


keyboard_for_admin = [
    [KeyboardButton("Аналитика📂"), KeyboardButton("Пост🚀")],
    [KeyboardButton("Подписки🤖"), KeyboardButton("Доступы🔒")],
    [KeyboardButton("Тумблер⚠️")],
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


analytic = [
    [KeyboardButton("Пользователи🤖"), KeyboardButton("EMAIL📧")],
    [KeyboardButton("Просмотры👁️")],
    [KeyboardButton("Назад👈")]
]


admins = [
    [KeyboardButton("Список администраторов✅")],
    [KeyboardButton("Выдать доступ🔑"), KeyboardButton("Удалить админа🔒")],
    [KeyboardButton("Назад👈")]
]


history_menu = [
    [KeyboardButton("Показать историю👀"), KeyboardButton("Очистить историю❌")],
    [KeyboardButton("Назад👈")],
]


switch_menu = [
    [KeyboardButton("Включить бота✅"), KeyboardButton("Отключить бота⛔")],
    [KeyboardButton("Назад👈")]
]

parsing_menu = [
    [KeyboardButton("Техника и гаджеты🤖"), KeyboardButton("Одежда👜")],
    [KeyboardButton("Вернуться👈")]
]



