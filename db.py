import psycopg2
import asyncpg
from config import host, user, password, db_name, port

connection = None

def Start():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port,
        )


        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )

            print(f"Server version: {cursor.fetchone()}")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def save_user(user_id):
    with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port,
        ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
                conn.commit()


import asyncpg

dsn = {
    'user': "postgres",
    'password': "0000",
    'database': "tg",
    'host': "127.0.0.1",
    'port': "5432"
}


async def check_email(user_id):
    # Создаем соединение с базой данных
    conn = await asyncpg.connect(**dsn)
    try:
        # Выполняем запрос к базе данных
        result = await conn.fetch("SELECT email FROM user_emails WHERE user_id = $1", user_id)
        # Проверяем, нашли ли мы email для данного user_id
        return len(result) > 0
    finally:
        # Закрываем соединение с базой данных
        await conn.close()


async def save_user_email(user_id, email):
    # Создаем соединение с базой данных
    conn = await asyncpg.connect(**dsn)
    try:
        # Сначала проверяем, существует ли уже email для этого user_id
        result = await conn.fetch("SELECT email FROM user_emails WHERE user_id = $1", user_id)
        if len(result) == 0:
            # Если нет, вставляем новый email
            await conn.execute("INSERT INTO user_emails (user_id, email) VALUES ($1, $2)", user_id, email)
    finally:
        # Закрываем соединение с базой данных
        await conn.close()


def save_requests(user_id, new_request):
    with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port,
        ) as conn:
        with conn.cursor() as cursor:
            # Получаем текущее значение requests для пользователя
            cursor.execute("SELECT requests FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if result is not None:
                # Если у пользователя уже есть запросы, добавляем новый запрос к существующим
                current_requests = result[0] if result[0] else ""
                updated_requests = current_requests + ", " + new_request if current_requests else new_request
                cursor.execute("UPDATE users SET requests = %s WHERE user_id = %s", (updated_requests, user_id))
            else:
                pass
            conn.commit()

def history(user_id):
    with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port,
        ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT requests FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if result is not None:
                return result[0]
            else:
                return "Извините, у вас ещё нет истории запросов"


def get_all_user_chat_ids():
    chat_ids = []
    try:
        with psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=db_name,
                port=port,
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id FROM users")
                chat_ids = [record[0] for record in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении user_id из базы данных: {e}")
    return chat_ids


def get_text():
    text = []
    try:
        with psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=db_name,
                port=port,
            ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT message_text FROM admin_messages")
                text += [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении: {e}")
    return text


def add_admin_message(text):

    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO admin_messages (message_text) VALUES (%s)", (text,))
    except Exception as e:
        print(f"Ошибка при добавлении сообщения в базу данных: {e}")


def delete_admin_message():
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM admin_messages")
    except Exception as e:
        print(f"Ошибка при удалении сообщения из базы данных: {e}")


def get_admin_message():
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT message_text FROM admin_messages LIMIT 1")
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при получении сообщения админа из базы данных: {e}")
        return None