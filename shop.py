import psycopg2
from prettytable import PrettyTable

# Функція для підключення до БД
def connect_to_db(dbname, user, password, host, port):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(f"Помилка підключення до БД: {e}")
        return None

# Функція для отримання списку таблиць
def get_tables(cursor):
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    return [row[0] for row in cursor.fetchall()]

# Функція для виводу структури таблиці
def print_table_structure(cursor, table_name):
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}';
    """)
    print(f"\nСтруктура таблиці '{table_name}':")
    table = PrettyTable(["Назва стовпця", "Тип даних"])
    for row in cursor.fetchall():
        table.add_row(row)
    print(table)

# Функція для виводу даних таблиці
def print_table_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print(f"\nДані таблиці '{table_name}':")
    table = PrettyTable(colnames)
    for row in rows:
        formatted_row = [
            f"{val:.2f}" if isinstance(val, float) else val for val in row
        ]
        table.add_row(formatted_row)
    print(table)

# Функція для виконання запиту з параметром
def execute_query_with_param(cursor, query_template, param_name):
    param_value = input(f"Введіть значення для {param_name}: ")
    query = query_template.format(param_value)
    cursor.execute(query)
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print("\nРезультат запиту:")
    table = PrettyTable(colnames)
    for row in rows:
        formatted_row = [
            f"{val:.2f}" if isinstance(val, float) else val for val in row
        ]
        table.add_row(formatted_row)
    print(table)

# Основна функція
def main():
    # Параметри підключення
    dbname = "shop_db"
    user = "postgres"
    password = "123"
    host = "localhost"
    port = "5433"

    conn = connect_to_db(dbname, user, password, host, port)
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Отримання та вивід всіх таблиць
        tables = get_tables(cursor)
        for table in tables:
            print_table_structure(cursor, table)
            print_table_data(cursor, table)

        # Виконання запитів та функцій
        queries = {
            "Вивід усіх продажів за готівку": "SELECT * FROM cash_sales_view;",
            "Вивід усіх продажів з доставкою": "SELECT * FROM delivery_sales_view;",
        }

        parameterized_queries = {
            "Розрахунок загальної суми і зі знижкою": (
                "SELECT * FROM calculate_total_and_discounted_amount({});",
                "id клієнта"
            ),
            "Отримання покупок клієнта": (
                "SELECT * FROM get_client_purchases({});",
                "id клієнта"
            ),
        }

        # Виконання звичайних запитів
        for description, query in queries.items():
            print(f"\n{description}:")
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            table = PrettyTable(colnames)
            for row in rows:
                formatted_row = [
                    f"{val:.2f}" if isinstance(val, float) else val for val in row
                ]
                table.add_row(formatted_row)
            print(table)

        # Виконання запитів з параметрами
        for description, (query_template, param_name) in parameterized_queries.items():
            print(f"\n{description}:")
            execute_query_with_param(cursor, query_template, param_name)

    except Exception as e:
        print(f"Помилка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
