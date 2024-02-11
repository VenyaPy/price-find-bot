import psycopg2
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