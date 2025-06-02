import sqlite3
from database import create_connection
from product_crud import update_product_stock # Для обновления остатков

ORDER_STATUSES = ['Новый', 'В обработке', 'Комплектуется', 'Готов к выдаче', 'Выполнен', 'Отменен']

def add_order(client_id, order_items_data, initial_status='Новый'):
    """
    Создает новый заказ и его позиции.
    order_items_data: список словарей [{'product_id': id, 'quantity': qty, 'price_per_unit': price}, ...]
    """
    conn = create_connection()
    if conn is None: return "ConnectionError"
    
    total_amount = sum(item['quantity'] * item['price_per_unit'] for item in order_items_data)
    
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;") # Начинаем транзакцию

        # 1. Проверяем остатки и уменьшаем их
        for item in order_items_data:
            stock_update_result = update_product_stock(item['product_id'], -item['quantity'], conn=conn) # Передаем conn
            if stock_update_result is not True: # Если не True, значит ошибка
                conn.execute("ROLLBACK;")
                if stock_update_result == "InsufficientStockError":
                    # Пытаемся получить имя товара для более информативного сообщения
                    cur.execute("SELECT name FROM products WHERE id = ?", (item['product_id'],))
                    product_name_row = cur.fetchone()
                    product_name = product_name_row[0] if product_name_row else f"ID {item['product_id']}"
                    return f"InsufficientStockError:{product_name}"
                return stock_update_result # Другая ошибка обновления остатков

        # 2. Создаем заказ
        sql_order = '''INSERT INTO orders (client_id, total_amount, status) VALUES (?, ?, ?)'''
        cur.execute(sql_order, (client_id, total_amount, initial_status))
        order_id = cur.lastrowid
        if not order_id:
            conn.execute("ROLLBACK;")
            return "OrderCreationError"

        # 3. Добавляем позиции заказа
        sql_item = '''INSERT INTO order_items (order_id, product_id, quantity, price_per_unit) VALUES (?, ?, ?, ?)'''
        for item in order_items_data:
            cur.execute(sql_item, (order_id, item['product_id'], item['quantity'], item['price_per_unit']))
        
        conn.commit() # Завершаем транзакцию
        return order_id
    except sqlite3.Error as e:
        conn.execute("ROLLBACK;")
        return f"SQLiteErrorOrder: {e}"
    finally:
        if conn: conn.close()

def get_all_orders_with_details():
    """Получает все заказы с именем клиента."""
    conn = create_connection()
    if conn is None: return []
    cur = conn.cursor()
    sql = """
    SELECT o.id, c.full_name, o.order_date, o.status, o.total_amount
    FROM orders o
    JOIN clients c ON o.client_id = c.id
    ORDER BY o.order_date DESC, o.id DESC
    """
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    orders = []
    for row in rows:
        orders.append({
            "id": row[0], "client_name": row[1], "order_date": row[2],
            "status": row[3], "total_amount": row[4]
        })
    return orders

def get_order_details_by_id(order_id):
    """Получает детали заказа, включая информацию о клиенте и все позиции заказа."""
    conn = create_connection()
    if conn is None: return None
    cur = conn.cursor()
    
    order_info = {}
    
    # 1. Информация о заказе и клиенте
    sql_order = """
    SELECT o.id, o.client_id, c.full_name, c.email, c.phone_number, o.order_date, o.status, o.total_amount
    FROM orders o
    JOIN clients c ON o.client_id = c.id
    WHERE o.id = ?
    """
    cur.execute(sql_order, (order_id,))
    order_row = cur.fetchone()
    
    if not order_row:
        conn.close()
        return None # Заказ не найден
        
    order_info = {
        "id": order_row[0], "client_id": order_row[1], "client_full_name": order_row[2],
        "client_email": order_row[3], "client_phone_number": order_row[4],
        "order_date": order_row[5], "status": order_row[6], "total_amount": order_row[7],
        "items": []
    }
    
    # 2. Позиции заказа
    sql_items = """
    SELECT oi.product_id, p.name, p.article_number, oi.quantity, oi.price_per_unit
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    WHERE oi.order_id = ?
    """
    cur.execute(sql_items, (order_id,))
    item_rows = cur.fetchall()
    
    for item_row in item_rows:
        order_info["items"].append({
            "product_id": item_row[0], "product_name": item_row[1], "product_article": item_row[2],
            "quantity": item_row[3], "price_per_unit": item_row[4]
        })
        
    conn.close()
    return order_info

def update_order_status(order_id, new_status):
    """Обновляет статус заказа."""
    if new_status not in ORDER_STATUSES:
        return "InvalidStatusError"

    conn = create_connection()
    if conn is None: return "ConnectionError"
    cur = conn.cursor()
    
    # Логика возврата товаров на склад при отмене
    # Получаем текущий статус и позиции заказа ПЕРЕД обновлением статуса
    current_order_details = None
    if new_status == 'Отменен':
        current_order_details = get_order_details_by_id(order_id) # Использует новое соединение, но это ок для чтения
        if not current_order_details:
             if conn: conn.close()
             return "NotFound" # Заказ не найден для получения деталей перед отменой

    try:
        conn.execute("BEGIN TRANSACTION;")
        sql = "UPDATE orders SET status = ? WHERE id = ?"
        cur.execute(sql, (new_status, order_id))
        
        if cur.rowcount == 0:
            conn.execute("ROLLBACK;")
            return "NotFound"

        # Если заказ отменяется и он не был "Выполнен" или уже "Отменен" ранее
        if new_status == 'Отменен' and current_order_details and \
           current_order_details['status'] not in ['Выполнен', 'Отменен']:
            for item in current_order_details['items']:
                stock_update_result = update_product_stock(item['product_id'], item['quantity'], conn=conn) # Возвращаем товар
                if stock_update_result is not True:
                    conn.execute("ROLLBACK;")
                    # Для простоты возвращаем общую ошибку, но можно детализировать
                    return f"StockReturnErrorOnCancel:{stock_update_result}"
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.execute("ROLLBACK;")
        return f"SQLiteErrorOrderStatus: {e}"
    finally:
        if conn: conn.close()

def delete_order(order_id):
    """Удаляет заказ. Позиции удаляются каскадно. Товары возвращаются на склад, если заказ не 'Выполнен'."""
    conn = create_connection()
    if conn is None: return "ConnectionError"
    
    current_order_details = get_order_details_by_id(order_id) # Получаем детали для возможного возврата товара
    if not current_order_details:
        if conn: conn.close()
        return "NotFound"

    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")
        
        # Если заказ не "Выполнен" и не "Отменен", возвращаем товары на склад
        if current_order_details['status'] not in ['Выполнен', 'Отменен']:
            for item in current_order_details['items']:
                stock_update_result = update_product_stock(item['product_id'], item['quantity'], conn=conn)
                if stock_update_result is not True:
                    conn.execute("ROLLBACK;")
                    return f"StockReturnErrorOnDelete:{stock_update_result}"

        cur.execute("DELETE FROM orders WHERE id = ?", (order_id,)) # order_items удалятся каскадно
        
        if cur.rowcount == 0: # Хотя get_order_details_by_id уже проверил
            conn.execute("ROLLBACK;")
            return "NotFound"
            
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.execute("ROLLBACK;")
        return f"SQLiteErrorOrderDelete: {e}"
    finally:
        if conn: conn.close()
