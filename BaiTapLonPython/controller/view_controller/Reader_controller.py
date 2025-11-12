
import pymssql


from database.db_connector import get_db_connection


# ===== CÁC HÀM XỬ LÝ ĐỘC GIẢ ======

def get_all_readers():
    """Lấy tất cả độc giả từ CSDL."""
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    sql = "SELECT ReaderId, FullName, Phone, Address FROM Reader"

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except pymssql.Error as e:
        print(f"Lỗi SQL (get_all_readers): {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def add_reader(full_name, phone, address):
    #Thêm độc giả mới (ReaderId tự tăng)."""
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    sql = """INSERT INTO Reader (FullName, Phone, Address)
             VALUES (%s, %s, %s)"""

    try:
        cursor.execute(sql, (full_name, phone, address))
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi SQL (add_reader): {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def update_reader(reader_id, full_name, phone, address):
    """Cập nhật thông tin độc giả."""
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    sql = """UPDATE Reader
             SET FullName=%s, \
                 Phone=%s, \
                 Address=%s
             WHERE ReaderId = %s"""

    try:
        cursor.execute(sql, (full_name, phone, address, reader_id))
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi SQL (update_reader): {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_reader(reader_id):
    """Xóa độc giả."""
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    sql = "DELETE FROM Reader WHERE ReaderId=%s"

    try:
        cursor.execute(sql, (reader_id,))
        conn.commit()
        return True
    except pymssql.Error as e:
        # GHI CHÚ: Xử lý lỗi nếu độc giả đang mượn sách (Foreign Key)
        print(f"Lỗi SQL (delete_reader): {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def find_reader(search_term):
    """Tìm 1 độc giả bằng FullName hoặc Phone."""
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    sql = """
          SELECT TOP 1 ReaderId, FullName, Phone, Address
          FROM Reader
          WHERE FullName LIKE %s \
             OR Phone LIKE %s
          """
    search_pattern = f'%{search_term}%'

    try:
        cursor.execute(sql, (search_pattern, search_pattern))
        row = cursor.fetchone()
        return row  # Trả về (None) nếu không tìm thấy
    except pymssql.Error as e:
        print(f"Lỗi SQL (find_reader): {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()