import pymssql
from database.db_connector import get_db_connection


def create_new_loan(reader_id, staff_id, due_date, list_of_copy_ids):
    """
    Tạo phiếu mượn mới và cập nhật trạng thái sách.

    Args:
        reader_id (int): ID của độc giả
        staff_id (int): ID của nhân viên (người cho mượn)
        due_date (str): Ngày hẹn trả (YYYY-MM-DD HH:MI:SS)
        list_of_copy_ids (list): Danh sách các CopyId (sách) được mượn

    Returns:
        tuple: (success: bool, message: str)
    """
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

        # 3. LẤY LoanId VỪA MỚI ĐƯỢC TẠO
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_loan_id = cursor.fetchone()[0]

        if not new_loan_id:
            conn.rollback()
            return (False, "Không thể tạo LoanId mới.")

        # 4. THÊM TỪNG CUỐN SÁCH vào LoanDetail VÀ CẬP NHẬT BookCopy
        for copy_id in list_of_copy_ids:
            # 4a. Lấy BookMoney để tính Deposit
            cursor.execute("SELECT BookMoney FROM BookCopy WHERE CopyId = %s", (copy_id,))
            book_money_result = cursor.fetchone()

            if not book_money_result or book_money_result[0] is None:
                book_money = 0
            else:
                book_money = book_money_result[0]

            deposit = book_money * 2  # Deposit = BookMoney * 2

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
    """
    Xử lý việc trả một bản sao sách với ngày giờ chỉ định.
    Trigger trong CSDL sẽ tự động tính tiền phạt (Fine).

    Args:
        copy_id (int): ID của sách cần trả
        returned_datetime_str (str): Ngày giờ trả (YYYY-MM-DD HH:MI:SS)

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    if conn is None:
        return (False, "Lỗi kết nối CSDL")

    cursor = conn.cursor()

    try:
        # 1. KIỂM TRA XEM SÁCH CÓ ĐANG ĐƯỢC MƯỢN KHÔNG (Status = 1)
        cursor.execute("SELECT Status FROM BookCopy WHERE CopyId = %s", (copy_id,))
        result = cursor.fetchone()

        if not result:
            conn.rollback()
            return (False, f"Không tìm thấy sách với CopyId: {copy_id}")

        if result[0] != 1:  # Status phải = 1 (OnLoan)
            conn.rollback()
            return (False, f"Sách CopyId {copy_id} không đang được mượn (Status: {result[0]})")

        # 2. KIỂM TRA XEM CÓ LOANDETAIL NÀO CHƯA TRẢ KHÔNG
        cursor.execute("""
                       SELECT LoanDetailId
                       FROM LoanDetail
                       WHERE CopyId = %s
                         AND ReturnedDate IS NULL
                       """, (copy_id,))

        loan_detail_result = cursor.fetchone()
        if not loan_detail_result:
            conn.rollback()
            return (False, f"Không tìm thấy phiếu mượn chưa trả cho sách CopyId: {copy_id}")

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