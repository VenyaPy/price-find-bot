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
    conn = await asyncpg.connect(**dsn)  # Убедитесь, что dsn настроен корректно
    try:
        result = await conn.fetchrow("SELECT email FROM user_emails WHERE user_id = $1", user_id)
        if result:
            return True  # Email найден
        else:
            return False  # Email не найден
    finally:
        await conn.close()


async def show_user():
    users = []
    conn = await asyncpg.connect(**dsn)
    try:
        result = await conn.fetch("SELECT user_id FROM users")
        users = [str(record['user_id']) for record in result]
        return ",".join(users)
    finally:
        await conn.close()


async def show_emails():
    emails = []
    conn = await asyncpg.connect(**dsn)
    try:
        result = await conn.fetch("SELECT email FROM user_emails")
        emails = [str(record['email']) for record in result]
        return ",".join(emails)
    finally:
        await conn.close()


async def save_user_email(user_id, email):
    conn = await asyncpg.connect(**dsn)  # Убедитесь, что dsn настроен корректно
    try:
        # Используем fetchrow для поиска существующего email
        result = await conn.fetchrow("SELECT email FROM user_emails WHERE user_id = $1", user_id)
        if not result:
            # Если email не найден, вставляем новый
            await conn.execute("INSERT INTO user_emails (user_id, email) VALUES ($1, $2)", user_id, email)
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
    finally:
        await conn.close()


async def save_count():
    conn = await asyncpg.connect(**dsn)
    try:
        # Проверяем, существует ли запись
        result = await conn.fetchrow("SELECT quantity FROM counter WHERE id = 1")
        if result:
            # Если запись существует, увеличиваем quantity
            await conn.execute("UPDATE counter SET quantity = quantity + 1 WHERE id = 1")
        else:
            # Если запись не существует, создаем ее с начальным значением quantity
            await conn.execute("INSERT INTO counter (id, quantity) VALUES (1, 1)")
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
    finally:
        await conn.close()


async def show_views():
    conn = await asyncpg.connect(**dsn)  # Предполагается, что dsn заранее определен
    try:
        # Использование await для асинхронного получения результата
        result = await conn.fetchrow("SELECT quantity FROM counter WHERE id = 1")
        if result:
            # Возврат значения quantity напрямую
            return result['quantity']
    except Exception as e:
        print("Ошибка при получении просмотров:", e)
    finally:
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


async def add_admin(id_admin):
    try:
        # Преобразование id_admin из строки в целое число
        id_admin_int = int(id_admin)

        conn = await asyncpg.connect(host=host, user=user, password=password, database=db_name, port=port)
        # Использование id_admin_int как аргумента для запроса
        await conn.execute("INSERT INTO admins (id_admin) VALUES ($1)", id_admin_int)
        print("Администратор добавлен.")
        await conn.close()
    except ValueError:
        # Ошибка преобразования типа, если id_admin не является числом
        print("Ошибка: ID администратора должен быть целым числом.")
    except Exception as e:
        print(f"Ошибка при добавлении администратора в базу данных: {e}")


async def delete_admin(id_admin):
    try:
        # Преобразование id_admin из строки в целое число
        id_admin_int = int(id_admin)

        conn = await asyncpg.connect(host=host, user=user, password=password, database=db_name, port=port)
        # Использование id_admin_int как аргумента для запроса
        await conn.execute("DELETE FROM admins WHERE id_admin = $1", id_admin_int)
        print("Администратор удален.")
        await conn.close()
    except ValueError:
        # Ошибка преобразования типа, если id_admin не является числом
        print("Ошибка: ID администратора должен быть целым числом.")
    except Exception as e:
        print(f"Ошибка при удалении администратора из базы данных: {e}")


async def show_admins():
    try:
        conn = await asyncpg.connect(host=host, user=user, password=password, database=db_name, port=port)
        records = await conn.fetch("SELECT id_admin FROM admins")
        admins_list = [str(record['id_admin']) for record in records]
        await conn.close()
        return ", ".join(admins_list)
    except Exception as e:
        print(f"Ошибка при получении списка администраторов из базы данных: {e}")
        return ""


async def is_admin(id_admin):
    try:
        # Преобразование id_admin из строки в целое число, если это необходимо
        id_admin_int = int(id_admin)

        conn = await asyncpg.connect(host=host, user=user, password=password, database=db_name, port=port)
        exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM admins WHERE id_admin = $1)", id_admin_int)
        await conn.close()
        return exists
    except ValueError:
        # Если id_admin не может быть преобразован в int, значит, он некорректен
        print("Ошибка: ID администратора должен быть числом.")
        return False
    except Exception as e:
        print(f"Ошибка при проверке статуса администратора в базе данных: {e}")
        return False





