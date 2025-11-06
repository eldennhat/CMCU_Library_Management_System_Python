from database.db_connector import get_db_connection
import pymssql


#*********************HÀM CHECK ĐĂNG NHẬP*********************
def check_login(username, password, role): #hàm nhận vào 3 tham số để check thông tin ở table
    conn = get_db_connection() #hàm này ở file db_connector
    #database kết nối
    if conn is None:
        print("Lỗi: Không thể kết nối tới CSDL. ")
        return False

    cursor = conn.cursor() #hàm để dịch sql


    #câu lệnh sql
    query = "SELECT * FROM Account WHERE Username = %s AND PasswordHash = %s AND Role = %s;"

    #
    try:
        #truyền các đối số %s ở query với 3 đối số được truyền vào check_login
        cursor.execute(query, (username, password, role)) #thực thi
        results = cursor.fetchone() #chọn 1

        if results:
            return True
        else:
            return False
    except pymssql.Error as e:
        print(f"Lỗi truy vấn sql {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

