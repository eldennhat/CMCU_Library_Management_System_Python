from tkinter import messagebox

import pymssql
from database.db_connector import get_db_connection

#======HÀM TẠO PHIẾU MƯỢN========
def create_new_loan(reader_id, staff_id, due_date, list_of_copy_ids):
    #Tham số ID độc giả, ID nhân viên, hạn trả sách, và list các copyID
    # Tạo phiếu mượn mới và cập nhật trạng thái sách.
    #     reader_id (int): ID của độc giả
    #     staff_id (int): ID của nhân viên (người cho mượn)
    #     due_date (str): Ngày hẹn trả (YYYY-MM-DD HH:MI:SS)
    #     list_of_copy_ids (list): Danh sách các CopyId (sách) được mượn
    #
    # Returns:
    #     tuple: (success: bool, message: str)

    conn = get_db_connection()
    if conn is None:
        return (False, "Lỗi kết nối CSDL")

    cursor = conn.cursor()

    try:
        # 1. KIỂM TRA XEM CÁC SÁCH CÓ SẴN SÀNG KHÔNG (Status = 0)
        for copy_id in list_of_copy_ids:
            cursor.execute("SELECT Status FROM BookCopy WHERE CopyId = %s", (copy_id,))
            result = cursor.fetchone()

            if not result:
                conn.rollback()
                return (False, f"Không tìm thấy sách với CopyId: {copy_id}")

            if result[0] != 0:  # Status phải = 0 (Available)
                conn.rollback()
                return (False, f"Sách CopyId {copy_id} không sẵn sàng để mượn (Status: {result[0]})")

        # 2. TẠO PHIẾU MƯỢN (Bảng Loan)
        loan_query = """
                     INSERT INTO Loan (ReaderId, StaffId, LoanDate, DueDate)
                     VALUES (%s, %s, SYSDATETIME(), %s); \
                     """
        cursor.execute(loan_query, (reader_id, staff_id, due_date))

        # 3. LẤY LoanId VỪA MỚI ĐƯỢC Tăng
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_loan_id = cursor.fetchone()[0]

        if not new_loan_id:
            conn.rollback()
            return (False, "Không thể tạo LoanId mới.")

        # 4. THÊM TỪNG CUỐN SÁCH vào LoanDetail VÀ CẬP NHẬT BookCopy
        for copy_id in list_of_copy_ids:
            # 4a. Lấy BookMoney để tính tiền cọc
            cursor.execute("SELECT BookMoney FROM BookCopy WHERE CopyId = %s", (copy_id,))
            book_money_result = cursor.fetchone() #Để tính tiền cọc

            if not book_money_result or book_money_result[0] is None:
                book_money = 0
            else:
                book_money = book_money_result[0]

            deposit = book_money * 2  # Deposit = BookMoney * 2 tiền cọc

            # 4b. Thêm vào LoanDetail (ReturnedDate = NULL ban đầu)
            detail_query = """
                           INSERT INTO LoanDetail (LoanId, CopyId, ReturnedDate, Deposit)
                           VALUES (%s, %s, NULL, %s) \
                           """
            cursor.execute(detail_query, (new_loan_id, copy_id, deposit))

            # 4c. Cập nhật trạng thái sách thành "OnLoan" (Status = 1)
            update_copy_query = "UPDATE BookCopy SET Status = 1 WHERE CopyId = %s"
            cursor.execute(update_copy_query, (copy_id,))

        # 5. LƯU TẤT CẢ THAY ĐỔI
        conn.commit()
        return (True, f"Tạo phiếu mượn thành công! Loan ID: {int(new_loan_id)}")

    except pymssql.Error as e:
        conn.rollback()
        print(f"Lỗi SQL (create_new_loan): {e}")
        return (False, f"Lỗi CSDL: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Lỗi (create_new_loan): {e}")
        return (False, f"Lỗi hệ thống: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def return_book_copy(copy_id, returned_datetime_str):
    # Xử lý việc trả một bản sao sách với ngày giờ chỉ định.
    # Trigger trong CSDL sẽ tự động tính tiền phạt (Fine).
    # Args:
    #     copy_id (int): ID của sách cần trả
    #     returned_datetime_str (str): Ngày giờ trả (YYYY-MM-DD HH:MI:SS)
    # Returns:
    #     tuple: (success: bool, message: str)
    conn = get_db_connection()
    if conn is None:
        return (False, "Lỗi kết nối CSDL")

    cursor = conn.cursor()

    try:
        # 3. CẬP NHẬT NGÀY TRẢ SÁCH (ReturnedDate)
        # Trigger sẽ tự động tính Fine dựa trên ReturnedDate
        update_detail_query = """
                              UPDATE LoanDetail
                              SET ReturnedDate = %s
                              WHERE CopyId = %s \
                                AND ReturnedDate IS NULL; \
                              """
        cursor.execute(update_detail_query, (returned_datetime_str, copy_id))

        # 4. CẬP NHẬT TRẠNG THÁI SÁCH (Status = 0, 'Available')
        update_copy_query = "UPDATE BookCopy SET Status = 0 WHERE CopyId = %s"
        cursor.execute(update_copy_query, (copy_id,))

        # 5. LƯU THAY ĐỔI
        conn.commit()

        # 6. LẤY THÔNG TIN FINE ĐÃ TÍNH (nếu có)
        cursor.execute("""
                       SELECT Fine
                       FROM LoanDetail
                       WHERE CopyId = %s
                        AND ReturnedDate = %s
                       """, (copy_id, returned_datetime_str))

        fine_result = cursor.fetchone()
        fine = fine_result[0] if fine_result and fine_result[0] else 0

        message = f"Trả sách thành công! CopyId: {copy_id}"
        if fine > 0:
            message += f"\nTiền phạt: {fine:,.0f} VNĐ"

        return (True, message)

    except pymssql.Error as e:
        conn.rollback()
        print(f"Lỗi SQL (return_book_copy): {e}")
        return (False, f"Lỗi CSDL: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Lỗi (return_book_copy): {e}")
        return (False, f"Lỗi hệ thống: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ========HÀM  ĐỂ LẤY CHI TIẾT CHO LOAN DETAILS VIEW =======
def get_loan_details_by_id(loan_id):
    #
    # Lấy tất cả thông tin chi tiết của MỘT phiếu mượn.
    # Trả về 2 phần: (thông_tin_phiếu, danh_sách_sách)
    #
    conn = get_db_connection()
    if conn is None:
        return (None, None)  # Trả về 2 giá trị None nếu lỗi

    cursor = conn.cursor(as_dict=True)  # Dùng as_dict=True cho dễ

    loan_info = None #Chứa tất cả thông tin
    book_list = [] #chứa các sách mượn

    try:
        # Query 1: Lấy thông tin chung của Phiếu Mượn
        # Sử dụng View đã thêm ở CSDL
        query_info = "SELECT * FROM v_LoanInfo WHERE LoanId = %s"
        cursor.execute(query_info, (loan_id,))
        loan_info = cursor.fetchone()  # Chỉ có 1 hàng


        # Query 2: Lấy danh sách Sách trong phiếu mượn đó
        query_books = "Select * FROM v_LoanBookDetails WHERE LoanId = %s"
        cursor.execute(query_books, (loan_id,))
        book_list = cursor.fetchall()  # Có thể có nhiều hàng

        return (loan_info, book_list)

    except pymssql.Error as e:
        print(f"Lỗi SQL (get_loan_details_by_id): {e}")
        return (None, None)
    finally:
        if conn:
            cursor.close()
            conn.close()

#Hàm Controller hỗ trợ Cho hàm load_all_loan_details
def get_loan_details():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Không thể kết nối với CSDL")
            return

        cursor = conn.cursor()
        # Query lấy tất cả dữ liệu có liên quan từ view đã làm
        sql_query = """
                    SELECT * FROM v_LoanDetails
                    ORDER BY LoanId DESC
                    """
        cursor.execute(sql_query)
        details = cursor.fetchall()
        return (details)
    except pymssql.Error as e:
        messagebox.showerror("Database Error", f"Không thể load dữ liệu:\n{e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



def delete_loan(loan_id):
    #
    # Xóa toàn bộ Phiếu Mượn (Loan) VÀ tự động xóa (cascade) LoanDetail.
    # Đồng thời, cập nhật lại Status của các sách đã mượn về 'Available'.
    #
    conn = get_db_connection()
    if conn is None:
        return (False, "Lỗi kết nối CSDL")

    cursor = conn.cursor()

    try:
        # BƯỚC 1: Tìm tất cả CopyId trong phiếu mượn này (mà chưa trả)
        cursor.execute("SELECT CopyId FROM LoanDetail WHERE LoanId = %s AND ReturnedDate IS NULL", (loan_id,))
        # GHI CHÚ: Lấy danh sách ID
        copy_ids_to_update = [row[0] for row in cursor.fetchall()]

        # BƯỚC 2: Cập nhật trạng thái các sách đó về 'Available' (Status = 0)
        if copy_ids_to_update:
            # GHI CHÚ: Tạo chuỗi placeholder (%s, %s, %s)
            placeholders = ', '.join(['%s'] * len(copy_ids_to_update))
            update_query = f"UPDATE BookCopy SET Status = 0 WHERE CopyId IN ({placeholders})"
            cursor.execute(update_query, tuple(copy_ids_to_update))

        # BƯỚC 3: Xóa Phiếu mượn (Loan).
        # CSDL sẽ tự động (cascade) xóa LoanDetail.
        cursor.execute("DELETE FROM Loan WHERE LoanId = %s", (loan_id,))

        # BƯỚC 4: Commit (Chốt đơn)
        conn.commit()
        return (True, f"Đã xóa thành công Phiếu mượn ID: {loan_id} và cập nhật {len(copy_ids_to_update)} cuốn sách.")

    except pymssql.Error as e:
        conn.rollback()  # Hủy bỏ nếu có lỗi
        print(f"Lỗi SQL (delete_loan): {e}")
        # GHI CHÚ: Báo lỗi nếu nó đang bị khóa bởi FK khác (ít xảy ra)
        return (False, f"Lỗi CSDL: Không thể xóa phiếu mượn. {e.args[0]}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()




# Hàm phụ trợ để chạy truy vấn
def _fetch_data_from_db(query):
        # Hàm phụ trợ để chạy truy vấn SELECT."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query)
            return cursor.fetchall()
        except pymssql.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi truy vấn dữ liệu:\n{e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


def _load_combobox_data():
    # Tải dữ liệu cho cả các combobox.
    # 1. Tải Độc giả ( vào readerlist bằng lệnh truy vấn)
    readers_list = _fetch_data_from_db("SELECT ReaderId, FullName FROM Reader ORDER BY FullName")

    # 2. Tải Nhân viên (Staff)
    # Tải các nhân viên vào list
    staff_list = _fetch_data_from_db("SELECT StaffId, FullName FROM Staff ORDER BY FullName")


    # 3. Tải Sách  - Chỉ những sách "Available" (Status = 0)
    query_available = """
                          SELECT c.CopyId, b.Title
                          FROM BookCopy c
                                   JOIN Book b ON c.BookId = b.BookId
                          WHERE c.Status = 0
                          ORDER BY b.Title
                          """
    # Lưu các copy mà còn mượn được
    copies_list = _fetch_data_from_db(query_available)


    # 4. Tải sách ĐANG MƯỢN (Status = 1) cho tab TRẢ SÁCH
    query_onloan = """
                       SELECT c.CopyId, b.Title
                       FROM BookCopy c
                        JOIN Book b ON c.BookId = b.BookId
                       WHERE c.Status = 1
                       ORDER BY c.CopyId
                       """
    # Trả ra các sách đang được mượn
    onloan_list = _fetch_data_from_db(query_onloan)

    return (readers_list, staff_list, copies_list, onloan_list)
