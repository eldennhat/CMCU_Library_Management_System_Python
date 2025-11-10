import pymssql
SQL_SERVER_CONFIG = {
    #
    'server': 'PHAMTUANHUNG',
    # 'port': '1433', # Sửa lại nếu cổng Docker của bạn khác
    'database': 'LibraryDB',
    # 'username': 'sa',
    # 'password': 'An1552006@'
}


#-------Kết nối sql
def get_db_connection():
    try:
        #hàm để trả về database kết nối
        conn = pymssql.connect(
            server=SQL_SERVER_CONFIG['server'],
            # port=int(SQL_SERVER_CONFIG['port']),
            # user=SQL_SERVER_CONFIG['username'],
            # password=SQL_SERVER_CONFIG['password'],
            database=SQL_SERVER_CONFIG['database']
        )
        return conn
    except pymssql.Error as e:
        print("Lỗi kết nối với SQL Server:", e)
        return None