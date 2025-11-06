import pymssql
#Mấy bố nhớ phải kết nối sql server đấy và tạo bảng theo như của Hưng
SQL_SERVER_CONFIG = { #theo server và database của ae
    #
    'server': 'localhost',
    'port': '1433',
    'database': 'QLyThuVien',
    'username': 'sa',
    'password': 'An1552006@' #tự điền của ae
}


#-------Kết nối mysql
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
