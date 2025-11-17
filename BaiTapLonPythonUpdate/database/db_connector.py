import pymssql
SQL_SERVER_CONFIG = {
    #
    'server': 'localhost',
    'port': '1433',
    'database': 'LibraryDB2',
    'username': 'sa',
    'password': 'An1552006@'
}


#-------Kết nối sql
def get_db_connection():
    try:
        #hàm để trả về database kết nối
        conn = pymssql.connect(
            server=SQL_SERVER_CONFIG['server'],
            port=int(SQL_SERVER_CONFIG['port']),
            user=SQL_SERVER_CONFIG['username'],
            password=SQL_SERVER_CONFIG['password'],
            database=SQL_SERVER_CONFIG['database']
        )
        return conn
    except pymssql.Error as e:
        print("Lỗi kết nối với mysql")
        return None

#ket noi SQL Server cho Window
#import pymssql
# #Mấy bố nhớ phải kết nối sql server đấy và tạo bảng theo như của Hưng
# SQL_SERVER_CONFIG = { #theo server và database của ae
#     #
#     'server': 'ELDENNHAT',
#     'port': '1433',
#     'database': 'Lib_Mgmt',
#     'username': 'sa',
#     'password': '...'
# }
# 
# #-------Kết nối sql
# def get_db_connection():
#     try:
#         #hàm để trả về database kết nối
#         conn = pymssql.connect(
#             server = SQL_SERVER_CONFIG['server'],
#             port = int(SQL_SERVER_CONFIG['port']),
#             user = SQL_SERVER_CONFIG['username'],
#             password = SQL_SERVER_CONFIG['password'],
#             database = SQL_SERVER_CONFIG['database']
#         )
#         return conn
#     except pymssql.Error as e:
#         print(f"Lỗi kết nối với SQL Server: {e}")
#         return None
# 
# if __name__ == "__main__":
#     conn = get_db_connection()
#     if conn:
#         print("Kết nối thành công!")
#         cursor = conn.cursor()
#         cursor.execute("SELECT @@VERSION")
#         version = cursor.fetchone()
#         print(f"SQL Server version: {version[0][:50]}...")
#         conn.close()
#     else:
#         print("Kết nối thất bại!")
