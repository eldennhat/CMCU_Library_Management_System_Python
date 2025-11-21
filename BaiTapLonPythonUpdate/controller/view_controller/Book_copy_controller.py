from tkinter import messagebox

import pymssql
from database.db_connector import get_db_connection

#======= CÁC HÀM XỬ LÝ BOOK COPY =========
def add_book_copy(book_id, publisher, status, storagenote, barcode, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
              INSERT INTO BookCopy (BookId, PublisherName, [Status], StorageNote, Barcode, BookMoney)
              VALUES (%s, %s, %s, %s, %s, %s) \
              """
        cursor.execute(sql, (book_id, publisher, status, storagenote, barcode, price))
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi SQL : {e}")
        conn.rollback()
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_book_copy(copy_id, book_id, publisher, status, storage_note, barcode, price):
    book_money = float(price)
    copy_id_int = int(copy_id)
    status_int = int(status)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
              UPDATE BookCopy
              SET BookId=%s, \
                  PublisherName=%s, Status=%s, StorageNote=%s, Barcode=%s, BookMoney=%s
              WHERE CopyId=%s \
              """
        cursor.execute(sql, (book_id, publisher, status_int, storage_note, barcode, book_money, copy_id_int))
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi SQL: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_book_copy(copy_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM BookCopy WHERE CopyId=%s"
        cursor.execute(sql, (copy_id,))
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Phải xoá ở phần Phiếu mượn trước, đảm bảo không có copy ID nào đang ở trong phiếu mượn")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def fetch_book_ids():
    #Lấy danh sách BookId từ bảng Book để điền vào combobox.
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT BookId, Title FROM Book ORDER BY BookId")

        # GHI CHÚ: fetchall() sẽ trả về list các tuple
        book_id_list = cursor.fetchall()

        return book_id_list

    except Exception as e:
        print(f"Lỗi khi lấy Book IDs: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_copies():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM v_Copies ORDER BY BookId"
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except pymssql.Error as e:
        print("SQL error:", e)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def search_book_copies(keyword):
    #Tìm kiếm Bản sao sách (BookCopy) dựa trên Tên sách (Title)
    #từ bảng Book (yêu cầu JOIN).

    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor()

    #  Query này JOIN 2 bảng và tìm theo Title
    query = """
            SELECT * FROM v_Copies
            WHERE Title LIKE %s
            """
    search_term = f"%{keyword}%"  # Thêm dấu %

    try:
        cursor.execute(query, (search_term,))
        results = cursor.fetchall()
        return results
    except pymssql.Error as e:
        print(f"Lỗi truy vấn SQL (search_book_copies): {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()