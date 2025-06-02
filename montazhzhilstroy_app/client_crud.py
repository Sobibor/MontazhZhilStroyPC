import sqlite3
from database import create_connection 

def add_client(full_name, phone_number=None, email=None, address=None):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    sql = ''' INSERT INTO clients(full_name, phone_number, email, address) VALUES(?,?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (full_name, phone_number, email, address))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed: clients.email' in str(e) and email: return "EmailExistsError"
        return f"IntegrityError: {e}"
    except sqlite3.Error as e: return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()

def get_client_by_id(client_id):
    conn = create_connection()
    if conn is None: return None
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "full_name": row[1], "phone_number": row[2], 
                "email": row[3], "address": row[4], "registration_date": row[5]}
    return None

def get_all_clients():
    conn = create_connection()
    if conn is None: return []
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, email FROM clients ORDER BY full_name ASC") # Для комбобокса достаточно id и имени
    rows = cur.fetchall()
    conn.close()
    clients = []
    for row in rows:
        clients.append({"id": row[0], "full_name": row[1], "email": row[2]})
    return clients

def update_client(client_id, full_name=None, phone_number=None, email=None, address=None):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    cur = conn.cursor()
    fields_to_update, params = [], []
    if full_name is not None: fields_to_update.append("full_name = ?"); params.append(full_name)
    if phone_number is not None: fields_to_update.append("phone_number = ?"); params.append(phone_number)
    if email is not None: fields_to_update.append("email = ?"); params.append(email)
    if address is not None: fields_to_update.append("address = ?"); params.append(address)
    if not fields_to_update: return "NoDataToUpdate"
    sql = f"UPDATE clients SET {', '.join(fields_to_update)} WHERE id = ?"
    params.append(client_id)
    try:
        cur.execute(sql, tuple(params))
        conn.commit()
        return True if cur.rowcount > 0 else "NotFound"
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed: clients.email' in str(e) and email: return "EmailExistsError"
        return f"IntegrityError: {e}"
    except sqlite3.Error as e: return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()

def delete_client(client_id):
    conn = create_connection()
    if conn is None: return "ConnectionError"
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM clients WHERE id=?', (client_id,))
        conn.commit()
        return True if cur.rowcount > 0 else "NotFound"
    except sqlite3.IntegrityError as e: 
        if "FOREIGN KEY constraint failed" in str(e):
            return "HasOrdersError"
        return f"IntegrityError: {e}"
    except sqlite3.Error as e: return f"SQLiteError: {e}"
    finally:
        if conn: conn.close()
