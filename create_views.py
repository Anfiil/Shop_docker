import psycopg2
from psycopg2 import sql

def create_views(dbname, user, password, host, port):
    # Підключення до БД
    try:
        conn = psycopg2.connect(
            dbname=dbname, 
            user=user, 
            password=password, 
            host=host, 
            port=port
        )
        cursor = conn.cursor()

        # Створення першого View - cash_sales_view
        create_cash_sales_view = """
        DROP VIEW IF EXISTS cash_sales_view CASCADE;
        CREATE VIEW cash_sales_view AS
        SELECT 
            s.sale_id AS "Ідентифікатор продажу",
            s.sale_date AS "Дата продажу",
            c.company_name AS "Назва клієнта",
            p.product_name AS "Назва продукту",
            s.quantity AS "Кількість",
            s.discount AS "Знижка",
            s.payment_method AS "Спосіб оплати",
            s.delivery_needed AS "Потрібна доставка",
            ROUND(s.delivery_cost, 2) AS "Вартість доставки",
            ROUND((p.price * s.quantity * (1 - s.discount / 100)), 2) AS "Загальна сума"
        FROM 
            sales s
        JOIN 
            clients c ON s.client_id = c.client_id
        JOIN 
            products p ON s.product_id = p.product_id
        WHERE 
            s.payment_method = 'готівковий'
        ORDER BY 
            c.company_name;
        """
        
        # Створення другого View - delivery_sales_view
        create_delivery_sales_view = """
        DROP VIEW IF EXISTS delivery_sales_view CASCADE;
        CREATE VIEW delivery_sales_view AS
        SELECT 
            s.sale_id AS "Ідентифікатор продажу",
            s.sale_date AS "Дата продажу",
            c.company_name AS "Назва клієнта",
            p.product_name AS "Назва продукту",
            s.quantity AS "Кількість",
            s.discount AS "Знижка",
            s.payment_method AS "Спосіб оплати",
            s.delivery_needed AS "Потрібна доставка",
            ROUND(s.delivery_cost, 2) AS "Вартість доставки",
            ROUND((p.price * s.quantity * (1 - s.discount / 100)), 2) AS "Загальна сума"
        FROM 
            sales s
        JOIN 
            clients c ON s.client_id = c.client_id
        JOIN 
            products p ON s.product_id = p.product_id
        WHERE 
            s.delivery_needed = TRUE;
        """


        count_client_purchases_view = """
        DROP VIEW IF EXISTS count_client_purchases_view CASCADE;
        CREATE OR REPLACE VIEW count_client_purchases_view AS
        SELECT 
            c.client_id AS "Ідентифікатор клієнта",
            c.company_name AS "Назва компанії",
            COUNT(s.sale_id) AS "Загальна кількість покупок"
        FROM 
            clients c
        LEFT JOIN 
            sales s ON c.client_id = s.client_id
        GROUP BY 
            c.client_id, c.company_name
        ORDER BY 
            "Загальна кількість покупок" DESC;
        """



        # Виконання SQL запитів для створення View
        cursor.execute(create_delivery_sales_view)
        cursor.execute(create_cash_sales_view)
        cursor.execute(count_client_purchases_view)

        # Підтвердження змін
        conn.commit()

        # Перевірка чи View створено (необов'язково)
        cursor.execute("SELECT * FROM cash_sales_view LIMIT 1;")
        cursor.fetchall()

        cursor.execute("SELECT * FROM delivery_sales_view LIMIT 1;")
        cursor.fetchall()

        print("Views successfully created.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Закриваємо з'єднання
        cursor.close()
        conn.close()



def create_functions(dbname, user, password, host, port):
    # Підключення до БД
    try:
        conn = psycopg2.connect(
            dbname=dbname, 
            user=user, 
            password=password, 
            host=host, 
            port=port
        )
        cursor = conn.cursor()

        # Функція для обчислення загальної суми і суми з урахуванням знижки
        create_calculate_total_and_discounted_amount = """
        CREATE OR REPLACE FUNCTION calculate_total_and_discounted_amount(client_id_input INT)
        RETURNS TABLE (
            client_name VARCHAR,
            total_amount DECIMAL(10, 2),
            discounted_amount DECIMAL(10, 2)
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                c.company_name AS "Назва клієнта",
                SUM(p.price * s.quantity) AS "Загальна сума",  -- Загальна сума без знижки
                SUM(p.price * s.quantity * (1 - s.discount / 100)) AS "Сума зі знижкою"  -- Сума з урахуванням знижки
            FROM 
                sales s
            JOIN 
                clients c ON s.client_id = c.client_id
            JOIN 
                products p ON s.product_id = p.product_id
            WHERE 
                s.client_id = client_id_input
            GROUP BY 
                c.company_name;
        END;
        $$ LANGUAGE plpgsql;
        """

        # Функція для отримання всіх покупок клієнта
        create_get_client_purchases = """
        CREATE OR REPLACE FUNCTION get_client_purchases(client_id_input INT)
        RETURNS TABLE (
            sale_id INT,
            sale_date DATE,
            product_name VARCHAR,
            quantity INT,
            discount DECIMAL(5, 2),
            payment_method VARCHAR,
            delivery_needed BOOLEAN,
            delivery_cost DECIMAL(10, 2)
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                s.sale_id AS "Ідентифікатор продажу",
                s.sale_date AS "Дата продажу",
                p.product_name AS "Назва продукту",
                s.quantity AS "Кількість",
                s.discount AS "Знижка",
                s.payment_method AS "Спосіб оплати",
                s.delivery_needed AS "Потрібна доставка",
                s.delivery_cost AS "Вартість доставки"
            FROM 
                sales s
            JOIN 
                products p ON s.product_id = p.product_id
            WHERE 
                s.client_id = client_id_input
            ORDER BY 
                s.sale_date;
        END;
        $$ LANGUAGE plpgsql;
        """

        

        # Функція для обчислення суми платежів за готівковий і безготівковий розрахунок
        create_calculate_payment_sum = """
        CREATE OR REPLACE FUNCTION calculate_payment_sum()
        RETURNS TABLE (
            client_id INT,
            company_name VARCHAR,
            cash_payment DECIMAL(10, 2),
            non_cash_payment DECIMAL(10, 2)
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                c.client_id AS "Ідентифікатор клієнта",
                c.company_name AS "Назва компанії",
                COALESCE(SUM(CASE WHEN s.payment_method = 'готівковий' THEN p.price * s.quantity ELSE 0 END), 0) AS "Оплата готівкою",
                COALESCE(SUM(CASE WHEN s.payment_method = 'безготівковий' THEN p.price * s.quantity ELSE 0 END), 0) AS "Безготівкова оплата"
            FROM 
                clients c
            LEFT JOIN 
                sales s ON c.client_id = s.client_id
            LEFT JOIN 
                products p ON s.product_id = p.product_id
            GROUP BY 
                c.client_id, c.company_name
            ORDER BY 
                c.client_id;
        END;
        $$ LANGUAGE plpgsql;
        """

        # Виконання SQL запитів для створення функцій
        cursor.execute(create_calculate_total_and_discounted_amount)
        cursor.execute(create_get_client_purchases)
        cursor.execute(create_calculate_payment_sum)

        # Підтвердження змін
        conn.commit()

        print("Functions successfully created.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Закриваємо з'єднання
        cursor.close()
        conn.close()


# Параметри підключення
dbname = "shop_db"
user = "postgres"
password = "123"
host = "localhost"
port = "5433"

# Викликаємо функцію для створення View
create_views(dbname, user, password, host, port)
# Викликаємо функцію для створення функцій в БД
create_functions(dbname, user, password, host, port)
