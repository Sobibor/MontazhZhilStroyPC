import sqlite3
from sqlite3 import Error
import os

DATABASE_NAME = "data/montazhzhilstroy.db" 

def create_connection():
    """Создает соединение с базой данных SQLite."""
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_NAME), exist_ok=True)
        conn = sqlite3.connect(DATABASE_NAME)
        conn.execute("PRAGMA foreign_keys = ON;") 
    except Error as e:
        print(f"Ошибка при подключении к БД: {e}")
    return conn

def create_table(conn, create_table_sql):
    """Создает таблицу по предоставленному SQL-запросу."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")

def initialize_database():
    """Инициализирует базу данных, создает таблицы, если они не существуют."""
    sql_create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        article_number TEXT UNIQUE,
        category TEXT,
        description TEXT,
        price REAL DEFAULT 0.0,
        stock_quantity INTEGER DEFAULT 0 CHECK(stock_quantity >= 0), -- Остаток не может быть отрицательным
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""
    sql_create_clients_table = """
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT UNIQUE,
        address TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""
    sql_create_orders_table = """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Новый' CHECK(status IN ('Новый', 'В обработке', 'Комплектуется', 'Готов к выдаче', 'Выполнен', 'Отменен')),
        total_amount REAL DEFAULT 0.0,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE RESTRICT 
    );"""
    sql_create_order_items_table = """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        price_per_unit REAL NOT NULL, -- Цена на момент заказа
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
    );"""
    
    conn = create_connection()
    if conn is not None:
        create_table(conn, sql_create_products_table)
        create_table(conn, sql_create_clients_table)
        create_table(conn, sql_create_orders_table)
        create_table(conn, sql_create_order_items_table)
        conn.close()
    else:
        print("Ошибка! Не удалось создать соединение с базой данных.")

if __name__ == '__main__':
    initialize_database()
    print(f"База данных '{DATABASE_NAME}' инициализирована (или уже существовала).")
