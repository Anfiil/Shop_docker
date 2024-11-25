import psycopg2

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '123', 
    'host': 'localhost',
    'port': "5433"
}

def create_database():
    connection = None
    cursor = None
    try:
        # Підключення до PostgreSQL
        connection = psycopg2.connect(**DB_CONFIG)
        connection.autocommit = True
        cursor = connection.cursor()

        # Створення бази даних
        cursor.execute("CREATE DATABASE shop_db;")
        print("База даних 'shop_db' успішно створена!")

    except psycopg2.OperationalError as e:
        print("Помилка підключення до PostgreSQL:", e)

    except psycopg2.errors.DuplicateDatabase:
        print("База даних 'shop_db' вже існує!")

    except Exception as e:
        print("Невідома помилка:", e)

    finally:
        # Закриття підключення
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    create_database()
