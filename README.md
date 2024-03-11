**Название продукта:** ЦеноПоиск

**Описание:** Телеграм бот созданный для анализа цен товаров в разных магазинах, также сравнение любых товаров.

**Возможности:**

Библиотека: telegram-python-bot.
База данных: PostgreSQL
Дополнительные библиотеки: Selenium, OpenAI API

_1. Пользовательская сторона:_

- Анализ конретного товара через библиотеку Selenium. Цена сортирует в формате от наименьшего и наибольшему.
- Сравнение любых товаров. Реализовано через ChatGPT. Нет ошибок, промт составлен так, чтобы сравнивало даже письменную ручку с Iphone 15 pro max.
- История запросов пользователя

_2. Админ меню:_

- Добавление/удаление/каналов для обязательной подписки. Хранится в базе данных.
- Рассылка для всех пользователей, которые есть в базе данных.
- Аналитика. Пользователи, email`s и другое.
- Доступы. Выдача прав администратора через админ-панель.

