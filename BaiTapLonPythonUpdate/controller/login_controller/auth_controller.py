from tkinter import messagebox

from database.db_connector import get_db_connection
import pymssql


#*********************HÀM CHECK ĐĂNG NHẬP*********************
def check_login(username, password): #hàm nhận vào 3 tham số để check thông tin ở table
    conn = get_db_connection() #hàm này ở file db_connector
    #database kết nối
    if conn is None:
        messagebox.showwarning("Lỗi: Không thể kết nối tới CSDL. ")
        return False

    cursor = conn.cursor() #hàm để dịch sql


    #câu lệnh sql
    query = "SELECT Role FROM Account WHERE Username = %s AND PasswordHash = %s"

    #
    try:
        #truyền các đối số %s ở query với 3 đối số được truyền vào check_login
        cursor.execute(query, (username, password)) #thực thi
        results = cursor.fetchone() #chọn 1

        if results:
            return results[0]
        else:
            return False
    except pymssql.Error as e:
        messagebox.showwarning(f"Lỗi truy vấn sql {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

