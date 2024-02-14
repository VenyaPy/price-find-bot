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


def add_public(ids, url):
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO publics (id_public, url) VALUES (%s, %s)", (ids, url))
    except Exception as e:
        print(f"Ошибка при добавлении паблика в базу данных: {e}")


async def find_public():
    try:
        conn = await asyncpg.connect(host=host, user=user, password=password, database=db_name, port=port)
        records = await conn.fetch("SELECT id_public, url FROM publics")
        await conn.close()
        return [{'id_public': record['id_public'], 'url': record['url']} for record in records]
    except Exception as e:
        print(f"Ошибка при получении пабликов из базы данных: {e}")
        return []


def show_public():
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, id_public FROM publics")  # Измененный запрос
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    return []
    except Exception as e:
        print(f"Ошибка при получении пабликов из базы данных: {e}")
        return []


def delete_public(id_to_delete):
    try:
        # Преобразуем входной id в целочисленное значение
        id_to_delete = int(id_to_delete)

        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                # Удаляем запись на основе колонки id, а не id_public
                cursor.execute("DELETE FROM publics WHERE id = %s RETURNING id;", (id_to_delete,))
                deleted_id = cursor.fetchone()
                conn.commit()
                if deleted_id:
                    print(f"Паблик с id {deleted_id[0]} успешно удален")
                    return True
                else:
                    print("Паблик с таким id не найден.")
                    return False
    except ValueError:
        print("Ошибка преобразования id в число.")
        return False
    except Exception as e:
        print(f"Ошибка при удалении паблика из базы данных: {e}")
        return False


def save_user_publics(save):
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (publics) VALUES (%s)", (save,))
    except Exception as e:
        print("Не удалось добавить паблик для пользователя")


async def is_user_subscribed(user_id, chat_id):
    try:
        # Создаем асинхронное подключение к базе данных
        conn = await asyncpg.connect(host=host, user=user, password=password, dbname=db_name, port=port)
        # Выполняем запрос на проверку подписки пользователя
        record = await conn.fetchrow("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = $1 AND publics @> $2::bigint[])", user_id, [chat_id])
        await conn.close()
        return record['exists']
    except Exception as e:
        print(f"Ошибка при проверке подписки пользователя: {e}")
        return False


def find_public_id():
    try:
        with psycopg2.connect(host=host, user=user, password=password, dbname=db_name, port=port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_public FROM publics")
                result = cursor.fetchall()
                # Возвращаем список ID пабликов
                return [item[0] for item in result]
    except Exception as e:
        print(f"Ошибка при получении ID пабликов из базы данных: {e}")
        return []

