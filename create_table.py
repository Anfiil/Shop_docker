import psycopg2
from psycopg2 import sql

# Параметри підключення до бази даних
conn = psycopg2.connect(
    dbname="shop_db",  # Назва бази даних
    user="postgres",  # Користувач
    password="123",  # Пароль
    host="localhost",  # Хост
    port="5433"  # Порт
)

# Створення курсора для виконання SQL запитів
cursor = conn.cursor()

# Створення таблиці для клієнтів
cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        client_id SERIAL PRIMARY KEY,  -- Лічильник, первинний ключ
        company_name VARCHAR(100) NOT NULL,  -- Назва фірми клієнта
        legal_or_physical VARCHAR(50) CHECK (legal_or_physical IN ('Юридична', 'Фізична')) NOT NULL,  -- Юридична чи фізична особа
        address VARCHAR(255),  -- Адреса
        phone VARCHAR(15) CHECK (phone ~ '^\+?[0-9]{10,15}$'),  -- Маска вводу для телефону
        contact_person VARCHAR(100),  -- Контактна особа
        account_number VARCHAR(20)  -- Розрахунковий рахунок
    );
""")

# Створення таблиці для товарів
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,  -- Лічильник, первинний ключ
        product_name VARCHAR(100) NOT NULL,  -- Назва товару
        price DECIMAL(10, 2) NOT NULL CHECK (price > 0),  -- Ціна товару
        stock_quantity INT NOT NULL CHECK (stock_quantity >= 0)  -- Кількість товару
    );
""")

# Створення таблиці для продажів
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id SERIAL PRIMARY KEY,  -- Лічильник, первинний ключ
        sale_date DATE NOT NULL,  -- Дата продажу
        client_id INT REFERENCES clients(client_id) ON DELETE CASCADE,  -- Зовнішній ключ до таблиці клієнтів
        product_id INT REFERENCES products(product_id) ON DELETE CASCADE,  -- Зовнішній ключ до таблиці товарів
        quantity INT NOT NULL CHECK (quantity > 0),  -- Кількість проданого товару
        discount DECIMAL(5, 2) CHECK (discount BETWEEN 3 AND 20),  -- Знижка від 3% до 20%
        payment_method VARCHAR(20) CHECK (payment_method IN ('готівковий', 'безготівковий')) NOT NULL,  -- Форма оплати
        delivery_needed BOOLEAN NOT NULL,  -- Необхідність доставки
        delivery_cost DECIMAL(10, 2) CHECK (delivery_cost >= 0)  -- Вартість доставки
    );
""")

# Заповнення таблиці клієнтів
cursor.executemany("""
    INSERT INTO clients (company_name, legal_or_physical, address, phone, contact_person, account_number)
    VALUES (%s, %s, %s, %s, %s, %s);
""", [
    ('Фірма 1', 'Юридична', 'Вулиця 1, Київ', '+380501234567', 'Контакт 1', 'UA1234567890'),
    ('Фірма 2', 'Юридична', 'Вулиця 2, Львів', '+380671234567', 'Контакт 2', 'UA9876543210'),
    ('Фізична особа 1', 'Фізична', 'Вулиця 3, Одеса', '+380501234678', 'Контакт 3', 'UA1122334455'),
    ('Фізична особа 2', 'Фізична', 'Вулиця 4, Харків', '+380631234567', 'Контакт 4', 'UA2233445566')
])

# Заповнення таблиці товарів
cursor.executemany("""
    INSERT INTO products (product_name, price, stock_quantity)
    VALUES (%s, %s, %s);
""", [
    ('Товар 1', 100.50, 50),
    ('Товар 2', 200.75, 40),
    ('Товар 3', 150.20, 30),
    ('Товар 4', 75.90, 60),
    ('Товар 5', 50.00, 100),
    ('Товар 6', 120.30, 80),
    ('Товар 7', 250.40, 20),
    ('Товар 8', 99.99, 90),
    ('Товар 9', 300.00, 15),
    ('Товар 10', 150.00, 25)
])

# Заповнення таблиці продажів
cursor.executemany("""
    INSERT INTO sales (sale_date, client_id, product_id, quantity, discount, payment_method, delivery_needed, delivery_cost)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
""", [
    ('2024-11-01', 1, 1, 2, 5.0, 'готівковий', True, 15.00),
    ('2024-11-02', 2, 2, 1, 10.0, 'безготівковий', False, 0.00),
    ('2024-11-03', 3, 3, 3, 15.0, 'готівковий', True, 10.00),
    ('2024-11-04', 4, 4, 1, 20.0, 'безготівковий', True, 20.00),
    ('2024-11-05', 1, 5, 4, 3.0, 'готівковий', False, 0.00),
    ('2024-11-06', 2, 6, 2, 10.0, 'безготівковий', True, 12.00),
    ('2024-11-07', 3, 7, 1, 5.0, 'готівковий', False, 0.00),
    ('2024-11-08', 4, 8, 2, 7.0, 'безготівковий', True, 25.00),
    ('2024-11-09', 1, 9, 1, 5.0, 'готівковий', False, 0.00),
    ('2024-11-10', 2, 10, 3, 10.0, 'безготівковий', True, 5.00)
    # Додати решту продажів
])

# Зберігаємо зміни
conn.commit()

# Закриваємо курсор і з'єднання
cursor.close()
conn.close()

print("Таблиці успішно створено та заповнено даними.")
