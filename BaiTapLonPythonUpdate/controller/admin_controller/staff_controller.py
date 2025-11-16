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

#
def get_all_staff_details():
    #Lấy danh sách tóm tắt (cho Treeview) bằng cách JOIN Staff và Account.

    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    # GHI CHÚ: Lấy các cột khớp với Treeview
    sql = """
          SELECT s.StaffId, s.FullName, a.[Role], s.Phone, a.Username, a.PasswordHash
          FROM Staff AS s
                   JOIN Account AS a ON s.StaffId = a.StaffId
          ORDER BY s.StaffId
          """
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except pymssql.Error as e:
        print(f"Lỗi SQL (get_all_staff_details): {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_staff_details_by_id(staff_id):
    #Lấy TẤT CẢ thông tin chi tiết (cho Form) của 1 nhân viên.

    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor(as_dict=True)  # Dùng as_dict=True cho dễ
    sql = """
          SELECT s.StaffId, \
                 s.FullName, \
                 s.Phone, \
                 s.DefaultStart, \
                 s.DefaultEnd, \
                 a.Username, \
                 a.[Role],\
                 a.PasswordHash
          FROM Staff AS s
                   JOIN Account AS a ON s.StaffId = a.StaffId
          WHERE s.StaffId = %s
          """
    try:
        cursor.execute(sql, (staff_id,))
        row = cursor.fetchone()
        return row  # Trả về 1 dictionary
    except pymssql.Error as e:
        print(f"Lỗi SQL (get_staff_details_by_id): {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def update_staff_details(staff_id, full_name, phone, start_time, end_time, role):

    #Cập nhật thông tin ở cả 2 bảng Staff và Account (Dùng Transaction).

    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # 1. Cập nhật bảng Staff
        sql_staff = """
                    UPDATE Staff
                    SET FullName=%s, \
                        Phone=%s, \
                        DefaultStart=%s, \
                        DefaultEnd=%s
                    WHERE StaffId = %s
                    """
        cursor.execute(sql_staff, (full_name, phone, start_time, end_time, staff_id))

        # 2. Cập nhật bảng Account
        sql_account = """
                      UPDATE Account
                      SET [Role]=%s
                      WHERE StaffId = %s
                      """
        cursor.execute(sql_account, (role, staff_id))

        # 3. Chốt đơn (Commit)
        conn.commit()
        return True

    except pymssql.Error as e:
        print(f"Lỗi SQL (update_staff_details): {e}")
        conn.rollback()  # Hủy bỏ tất cả
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_staff_and_account(staff_id):
    #Xóa nhân viên (Phải xóa Account trước, rồi xóa Staff).
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # 1. Xóa tài khoản (Account) liên kết trước
        sql_account = "DELETE FROM Account WHERE StaffId=%s"
        cursor.execute(sql_account, (staff_id,))

        # 2. Xóa nhân viên (Staff)
        sql_staff = "DELETE FROM Staff WHERE StaffId=%s"
        cursor.execute(sql_staff, (staff_id,))

        # 3. Chốt đơn
        conn.commit()
        return True

    except pymssql.Error as e:
        print(f"Lỗi SQL (delete_staff_and_account): {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def create_staff_and_account(staff_data, account_data):

    # Thêm Nhân viên VÀ Tài khoản trong cùng 1 Giao dịch (Transaction).
    # staff_data = (FullName, Phone, DefaultStart, DefaultEnd)
    # account_data = (Username, PasswordHash, Role)

    conn = get_db_connection()
    if not conn:
        return (False, "Lỗi kết nối CSDL")

    cursor = conn.cursor()

    try:
        # 1. THÊM VÀO BẢNG STAFF TRƯỚC
        sql_staff = """
                    INSERT INTO Staff (FullName, Phone, DefaultStart, DefaultEnd)
                    VALUES (%s, %s, %s, %s) \
                    """
        cursor.execute(sql_staff, staff_data)

        # 2. LẤY STAFFID VỪA ĐƯỢC TẠO
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_staff_id = cursor.fetchone()[0]

        if not new_staff_id:
            conn.rollback()  # Hủy bỏ
            return (False, "Không thể tạo StaffId mới.")

        # 3. THÊM VÀO BẢNG ACCOUNT (dùng StaffId mới)
        (username, password, role) = account_data

        sql_account = """
                      INSERT INTO Account (Username, PasswordHash, [Role], StaffId)
                      VALUES (%s, %s, %s, %s)
                      """
        cursor.execute(sql_account, (username, password, role, new_staff_id))

        # 4. CHỐT ĐƠN (COMMIT CẢ HAI)
        conn.commit()
        return (True, f"Tạo nhân viên {staff_data[0]} (ID: {new_staff_id}) thành công!")

    except pymssql.Error as e:
        # GHI CHÚ: Xử lý lỗi (ví dụ: Trùng Username)
        conn.rollback()  # Hủy bỏ tất cả
        error_code = str(e.args[0])
        if '2627' in error_code or '2601' in error_code:
            return (False, f"Lỗi: Tên đăng nhập '{account_data[0]}' đã tồn tại.")
        else:
            print(f"Lỗi SQL (create_staff_and_account): {e}")
            return (False, f"Lỗi CSDL: {e}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()