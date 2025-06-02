import sqlite3
from database import create_connection 

def add_product(name, article_number, category, description, price, stock_quantity):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    sql = ''' INSERT INTO products(name, article_number, category, description, price, stock_quantity)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (name, article_number, category, description, price, stock_quantity))
        conn.commit()
        return cur.lastrowid 
    except sqlite3.IntegrityError as e: 
        if "UNIQUE constraint failed: products.article_number" in str(e):
            return "IntegrityErrorArticle" 
        return f"IntegrityError: {e}"
    except sqlite3.Error as e:
        return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()

def get_product_by_id(product_id):
    conn = create_connection()
    if conn is None: return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, article_number, category, description, price, stock_quantity FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "article_number": row[2], "category": row[3], 
                "description": row[4], "price": row[5], "stock_quantity": row[6]}
    return None

def get_all_products():
    conn = create_connection()
    if conn is None: return []
    cur = conn.cursor()
    # Выбираем только товары с положительным остатком для добавления в заказ, или все для каталога
    # Для добавления в заказ лучше фильтровать в GUI или при выборе
    cur.execute("SELECT id, name, article_number, price, stock_quantity FROM products ORDER BY name ASC") 
    rows = cur.fetchall()
    conn.close()
    products = []
    for row in rows:
        products.append({"id": row[0], "name": row[1], "article_number": row[2], 
                         "price": row[3], "stock_quantity": row[4]})
    return products

def update_product_stock(product_id, quantity_change, conn=None):
    """
    Обновляет остаток товара. quantity_change может быть положительным (возврат) или отрицательным (продажа).
    Если conn передан, используется существующее соединение (для транзакций).
    """
    close_conn_locally = False
    if conn is None:
        conn = create_connection()
        if conn is None: return "ConnectionError"
        close_conn_locally = True
    
    cur = conn.cursor()
    try:
        # Сначала получаем текущий остаток, чтобы избежать отрицательных значений через CHECK constraint
        cur.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
        current_stock_row = cur.fetchone()
        if not current_stock_row:
            return "ProductNotFoundForStockUpdate"
        
        current_stock = current_stock_row[0]
        new_stock = current_stock + quantity_change # quantity_change будет отрицательным для уменьшения

        if new_stock < 0:
            return "InsufficientStockError" # Недостаточно товара

        cur.execute("UPDATE products SET stock_quantity = ? WHERE id = ?", (new_stock, product_id))
        # conn.commit() будет вызван в вызывающей функции, если conn был передан
        if close_conn_locally:
            conn.commit()
        return True
    except sqlite3.IntegrityError as e: # Сработает на CHECK(stock_quantity >= 0)
        return "InsufficientStockError" # Или другая ошибка целостности
    except sqlite3.Error as e:
        return f"SQLiteErrorStockUpdate: {e}"
    finally:
        if close_conn_locally and conn:
            conn.close()


def update_product(product_id, name=None, article_number=None, category=None, description=None, price=None, stock_quantity=None):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    cur = conn.cursor()
    fields_to_update, params = [], []
    if name is not None: fields_to_update.append("name = ?"); params.append(name)
    if article_number is not None: fields_to_update.append("article_number = ?"); params.append(article_number)
    if category is not None: fields_to_update.append("category = ?"); params.append(category)
    if description is not None: fields_to_update.append("description = ?"); params.append(description)
    if price is not None: fields_to_update.append("price = ?"); params.append(price)
    if stock_quantity is not None: 
        if int(stock_quantity) < 0: return "StockCannotBeNegative"
        fields_to_update.append("stock_quantity = ?"); params.append(stock_quantity)
    if not fields_to_update: return "NoDataToUpdate"
    sql = f"UPDATE products SET {', '.join(fields_to_update)} WHERE id = ?"
    params.append(product_id)
    try:
        cur.execute(sql, tuple(params))
        conn.commit()
        return True if cur.rowcount > 0 else "NotFound"
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: products.article_number" in str(e): return "IntegrityErrorArticle"
        if "CHECK constraint failed: products" in str(e): return "StockCannotBeNegative" # Из-за stock_quantity >= 0
        return f"IntegrityError: {e}"
    except sqlite3.Error as e: return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()

def delete_product(product_id):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM products WHERE id=?', (product_id,))
        conn.commit()
        return True if cur.rowcount > 0 else "NotFound"
    except sqlite3.IntegrityError as e: 
        if "FOREIGN KEY constraint failed" in str(e):
            return "HasOrderItemsError" 
        return f"IntegrityError: {e}"
    except sqlite3.Error as e: return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()
