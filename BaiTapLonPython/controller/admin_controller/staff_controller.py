import pymssql
from database.db_connector import get_db_connection


##*********************HÀM CHECK ĐĂNG KÝ*********************
def register_new_user(username, password, role):
    conn = get_db_connection()
    if conn is None:
        print("Không thể kết nối CSDL")
        return "DB_ERROR"

    cursor = conn.cursor()


    #2. Cập nhập câu query để insert
    query = "INSERT INTO Account(Username, PasswordHash, Role) VALUES (%s, %s, %s)"

    try:
        #3. Chèn (Username, mã băm, role)
        cursor.execute(query, (username, password, role))
        conn.commit() #commit lại bảng
        return "SUCCESS"
    except pymssql.Error as e:
        # 4. Xử lý lỗi TRÙNG USERNAME (Violation of UNIQUE KEY constraint)
        error_code = str(e.args[0])
        # Mã lỗi 2627 hoặc 2601 của SQL Server là lỗi vi phạm UNIQUE
        if '2627' in error_code or '2601' in error_code:
            print(f"Lỗi: Tên đăng nhập '{username}' đã tồn tại.")
            return "USERNAME_EXISTS"
        else:
            # Các lỗi SQL khác
            print(f"Lỗi truy vấn SQL (register): {e}")
            return "DB_ERROR"

    finally:
        if conn:
            conn.close()
            cursor.close()