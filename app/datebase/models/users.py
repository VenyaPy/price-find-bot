import psycopg2
from main import start_handler

# Здесь должна быть инициализация соединения с базой данных
conn = psycopg2.connect(host = "127.0.0.1", dbname='tg', user='postgres', password='0000')
cursor = conn.cursor()


def save_user(user_id=id):
    if start_handler:
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
            conn.commit()

