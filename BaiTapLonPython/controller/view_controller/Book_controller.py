

import pymssql
from database.db_connector import get_db_connection

#----- CÁC HÀM XỬ LÝ SÁCH -------
# Ham lay tat ca cac sach
def get_all_books():
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor()
    query = "SELECT BookId, ISBN, Title, CategoryName, BookAuthor, PublishYear From Book"

    try:
        cursor.execute(query)
        #Tra ve 1 list cac hang
        results = cursor.fetchall()
        return results
    except pymssql.Error as e:
        print("Error while fetching data from MySQL:", e)
        return None
    finally:
        if conn is not None:
            conn.close()
            cursor.close()

# Ham Them sach
def add_book(book_data):
    """
    Thêm một sách mới vào CSDL.
    'book_data' là một tuple: (book_id, isbn, title, category, author, year)
    """
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    query = """
        INSERT INTO Book (BookId,ISBN, Title, CategoryName, BookAuthor, PublishYear) 
        VALUES (%s ,%s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(query, book_data)
        conn.commit() #Luu thay doi
        return True
    except pymssql.Error as e:
        print("Error while inserting data into MySQL:", e)
        return False
    finally:
        if conn is not None:
            conn.close()
            cursor.close()


def update_book(book_data):
    """
    Cập nhật một sách đã có.
    'book_data' là một tuple: (isbn, title, category, author, year, book_id)
    """
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = """
            UPDATE Book
            SET ISBN            = %s, \
                Title           = %s, \
                CategoryName    = %s, \
                BookAuthor          = %s, \
                PublishYear = %s
            WHERE BookId = %s \
            """

    try:
        cursor.execute(query, book_data)
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi truy vấn SQL (update_book): {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()


def delete_book(book_id):
    """
    Xóa một sách khỏi CSDL dựa trên BookID.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = "DELETE FROM Book WHERE BookId = %s"

    try:
        cursor.execute(query, (book_id,))  # Phải truyền vào dạng tuple
        conn.commit()
        return True
    except pymssql.Error as e:
        print(f"Lỗi truy vấn SQL (delete_book): {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()


def search_book(keyword):
    """
    Tìm sách dựa trên Title (Tên sách) hoặc Author (Tác giả).
    """
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    # GHI CHÚ: Dùng LIKE %...% để tìm kiếm
    query = """
            SELECT BookID, ISBN, Title, CategoryName, BookAuthor, PublishYear
            FROM Book
            WHERE Title LIKE %s \
               OR BookAuthor LIKE %s \
            """
    # GHI CHÚ: Thêm dấu % vào từ khóa
    search_term = f"%{keyword}%"

    try:
        cursor.execute(query, (search_term, search_term))
        results = cursor.fetchall()
        return results
    except pymssql.Error as e:
        print(f"Lỗi truy vấn SQL (search_book): {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()