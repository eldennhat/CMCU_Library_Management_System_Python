import tkinter as tk
from tkinter import ttk, messagebox
import pymssql
from GUI.Font.font import FONT_PIXELS
from tkmacosx import Button as macButton
from controller.view_controller.Loan_controller import create_new_loan, return_book_copy
from database.db_connector import get_db_connection
import datetime


class LoanMenu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pixel_font = (FONT_PIXELS, 10)
        self.pixel_font_bold = (FONT_PIXELS, 11, 'bold')

        # === TAB 1 (MƯỢN SÁCH) ===
        self.reader_id_var = tk.StringVar()
        self.staff_id_var = tk.StringVar()
        default_due_datetime = datetime.datetime.now() + datetime.timedelta(days=7)
        self.due_date_date_var = tk.StringVar(value=default_due_datetime.strftime("%Y-%m-%d"))
        self.due_date_hour_var = tk.StringVar(value=default_due_datetime.strftime("%H"))
        self.due_date_min_var = tk.StringVar(value=default_due_datetime.strftime("%M"))
        self.copy_id_to_add_var = tk.StringVar()

        # === TAB 2 (TRẢ SÁCH) ===
        self.copy_id_to_return_var = tk.StringVar()
        self.return_date_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.return_date_hour_var = tk.StringVar(value=datetime.datetime.now().strftime("%H"))
        self.return_date_min_var = tk.StringVar(value=datetime.datetime.now().strftime("%M"))

        self.temp_loan_list = []
        self.readers_list = []
        self.staff_list = []
        self.copies_list = []

        self._setup_widgets()
        self._load_combobox_data()

    def _fetch_data_from_db(self, query):
        """Hàm phụ trợ để chạy truy vấn SELECT."""
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
            messagebox.showerror("Database Error", f"Lỗi truy vấn dữ liệu:\n{e}", parent=self)
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _load_combobox_data(self):
        """Tải dữ liệu cho cả 3 combobox."""
        # 1. Tải Độc giả (Reader)
        self.readers_list = self._fetch_data_from_db("SELECT ReaderId, FullName FROM Reader ORDER BY FullName")
        reader_display_list = [f"ID: {r['ReaderId']} - Tên: {r['FullName']}" for r in self.readers_list]
        if hasattr(self, 'reader_combobox'):
            self.reader_combobox['values'] = reader_display_list

        # 2. Tải Nhân viên (Staff)
        self.staff_list = self._fetch_data_from_db("SELECT StaffId, FullName FROM Staff ORDER BY FullName")
        staff_display_list = [f"ID: {s['StaffId']} - Tên: {s['FullName']}" for s in self.staff_list]
        if hasattr(self, 'staff_combobox'):
            self.staff_combobox['values'] = staff_display_list

        # 3. Tải Sách (BookCopy) - Chỉ những sách "Available" (Status = 0)
        query_available = """
                          SELECT c.CopyId, b.Title
                          FROM BookCopy c
                                   JOIN Book b ON c.BookId = b.BookId
                          WHERE c.Status = 0
                          ORDER BY b.Title \
                          """
        self.copies_list = self._fetch_data_from_db(query_available)
        copy_display_list = [f"CopyID: {c['CopyId']} - Tên: {c['Title']}" for c in self.copies_list]
        if hasattr(self, 'copy_id_combobox'):
            self.copy_id_combobox['values'] = copy_display_list

        # 4. Tải sách ĐANG MƯỢN (Status = 1) cho tab TRẢ SÁCH
        query_onloan = """
                       SELECT c.CopyId, b.Title
                       FROM BookCopy c
                                JOIN Book b ON c.BookId = b.BookId
                       WHERE c.Status = 1
                       ORDER BY c.CopyId \
                       """
        onloan_list = self._fetch_data_from_db(query_onloan)
        onloan_display = [f"CopyID: {c['CopyId']} - {c['Title']}" for c in onloan_list]
        if hasattr(self, 'copy_id_return_combobox'):
            self.copy_id_return_combobox['values'] = onloan_display

    def _setup_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        loan_frame = ttk.Frame(notebook, padding=10)
        notebook.add(loan_frame, text="Create New Loan")
        self._create_loan_tab(loan_frame)

        return_frame = ttk.Frame(notebook, padding=10)
        notebook.add(return_frame, text="Return Book")
        self._create_return_tab(return_frame)

        view_all_frame = ttk.Frame(notebook, padding=10)
        notebook.add(view_all_frame, text="View All Details")
        self._create_view_all_tab(view_all_frame)

    def _create_loan_tab(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Loan Information", padding=10)
        info_frame.pack(fill="x", pady=5)

        ttk.Label(info_frame, text="Reader:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.reader_combobox = ttk.Combobox(info_frame, textvariable=self.reader_id_var, state="readonly", width=40)
        self.reader_combobox.grid(row=0, column=1, padx=5, pady=5, columnspan=4)

        ttk.Label(info_frame, text="Staff:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.staff_combobox = ttk.Combobox(info_frame, textvariable=self.staff_id_var, state="readonly", width=40)
        self.staff_combobox.grid(row=1, column=1, padx=5, pady=5, columnspan=4)

        # Ngày hẹn trả
        ttk.Label(info_frame, text="Due Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.due_date_date_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(info_frame, text="H:").grid(row=2, column=2, padx=2, pady=5)
        ttk.Spinbox(info_frame, textvariable=self.due_date_hour_var, from_=0, to=23, width=3).grid(row=2, column=3,
                                                                                                   pady=5)
        ttk.Label(info_frame, text="M:").grid(row=2, column=4, padx=2, pady=5)
        ttk.Spinbox(info_frame, textvariable=self.due_date_min_var, from_=0, to=59, width=3).grid(row=2, column=5,
                                                                                                  pady=5)

        # Frame thêm sách
        book_frame = ttk.LabelFrame(parent, text="Add Books to Loan", padding=10)
        book_frame.pack(fill="both", expand=True, pady=5)

        ttk.Label(book_frame, text="Available Copy:").pack(side="left", padx=5)
        self.copy_id_combobox = ttk.Combobox(book_frame, textvariable=self.copy_id_to_add_var, state="readonly",
                                             width=40)
        self.copy_id_combobox.pack(side="left", padx=5, fill="x", expand=True)

        macButton(book_frame, text="Add Book", command=self._on_add_book_to_list, bg="cyan").pack(side="left", padx=5)
        macButton(book_frame, text="Remove Book", command=self._on_remove_book_from_list, bg="orange").pack(side="left",
                                                                                                            padx=5)

        self.loan_tree = ttk.Treeview(book_frame, columns=("CopyId", "Title"), show="headings", height=5)
        self.loan_tree.heading("CopyId", text="Book Copy ID")
        self.loan_tree.heading("Title", text="Book Title")
        self.loan_tree.column("CopyId", width=100, anchor="center")
        self.loan_tree.column("Title", width=300)
        self.loan_tree.pack(fill="both", expand=True, pady=10)

        # Nút xác nhận
        macButton(parent, text="CONFIRM NEW LOAN", command=self._on_confirm_loan, bg="green", fg="white",
                  font=self.pixel_font_bold).pack(fill="x", ipady=10, pady=10)

    def _create_return_tab(self, parent):
        main_frame = ttk.LabelFrame(parent, text="Return a Book", padding=20)
        main_frame.pack(expand=True, padx=50, pady=30)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Copy ID (On Loan):", font=self.pixel_font).grid(row=0, column=0, padx=5, pady=10,
                                                                                    sticky="w")
        self.copy_id_return_combobox = ttk.Combobox(main_frame, textvariable=self.copy_id_to_return_var,
                                                    state="readonly", font=self.pixel_font, width=30)
        self.copy_id_return_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(main_frame, text="Return Date (Y-M-D):", font=self.pixel_font).grid(row=1, column=0, padx=5, pady=10,
                                                                                      sticky="w")
        ttk.Entry(main_frame, textvariable=self.return_date_date_var, font=self.pixel_font, width=30).grid(row=1,
                                                                                                           column=1,
                                                                                                           padx=5,
                                                                                                           pady=10,
                                                                                                           sticky="ew")

        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Label(time_frame, text="Hour (0-23):", font=self.pixel_font).pack(side="left", padx=5)
        ttk.Spinbox(time_frame, textvariable=self.return_date_hour_var, from_=0, to=23, width=5,
                    font=self.pixel_font).pack(side="left", padx=5)

        ttk.Label(time_frame, text="Minute (0-59):", font=self.pixel_font).pack(side="left", padx=5)
        ttk.Spinbox(time_frame, textvariable=self.return_date_min_var, from_=0, to=59, width=5,
                    font=self.pixel_font).pack(side="left", padx=5)

        macButton(main_frame, text="SUBMIT RETURN", command=self._on_return_book, bg="blue", fg="white",
                  font=self.pixel_font_bold).grid(row=3, column=0, columnspan=2, pady=20, ipady=10, sticky="nsew")

    def _create_view_all_tab(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        refresh_button = macButton(parent, text="Refresh Data", command=self._load_all_loan_details,
                                   bg="#007BFF", fg="white")
        refresh_button.pack(pady=10, fill="x")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)

        columns = ("LoanDetailId", "LoanId", "CopyId", "BookTitle", "ReturnedDate",
                   "StaffName", "ReaderName", "Fine", "Deposit")
        self.view_all_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.view_all_tree.yview)

        self.view_all_tree.heading("LoanDetailId", text="Detail ID")
        self.view_all_tree.heading("LoanId", text="Loan ID")
        self.view_all_tree.heading("CopyId", text="Copy ID")
        self.view_all_tree.heading("BookTitle", text="Book Title")
        self.view_all_tree.heading("ReturnedDate", text="Returned Date")
        self.view_all_tree.heading("StaffName", text="Staff Name")
        self.view_all_tree.heading("ReaderName", text="Reader Name")
        self.view_all_tree.heading("Fine", text="Fine")
        self.view_all_tree.heading("Deposit", text="Deposit")

        self.view_all_tree.column("LoanDetailId", width=80, anchor="center")
        self.view_all_tree.column("LoanId", width=80, anchor="center")
        self.view_all_tree.column("CopyId", width=80, anchor="center")
        self.view_all_tree.column("BookTitle", width=200)
        self.view_all_tree.column("ReturnedDate", width=150, anchor="center")
        self.view_all_tree.column("StaffName", width=150)
        self.view_all_tree.column("ReaderName", width=150)
        self.view_all_tree.column("Fine", width=100, anchor="e")
        self.view_all_tree.column("Deposit", width=100, anchor="e")

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_all_tree.pack(side=tk.LEFT, fill="both", expand=True)

        self._load_all_loan_details()

    def _load_all_loan_details(self):
        """Tải tất cả chi tiết phiếu mượn với thông tin đầy đủ."""
        for item in self.view_all_tree.get_children():
            self.view_all_tree.delete(item)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if not conn:
                messagebox.showerror("Error", "Cannot connect to database.", parent=self)
                return

            cursor = conn.cursor()
            sql_query = """
                        SELECT d.LoanDetailId, \
                               l.LoanId, \
                               d.CopyId, \
                               b.Title    AS BookTitle, \
                               d.ReturnedDate, \
                               s.FullName AS StaffName, \
                               r.FullName AS ReaderName, \
                               d.Fine, \
                               d.Deposit
                        FROM LoanDetail AS d
                                 JOIN Loan AS l ON d.LoanId = l.LoanId
                                 JOIN BookCopy AS c ON d.CopyId = c.CopyId
                                 JOIN Book AS b ON c.BookId = b.BookId
                                 JOIN Staff AS s ON l.StaffId = s.StaffId
                                 JOIN Reader AS r ON l.ReaderId = r.ReaderId
                        ORDER BY l.LoanId DESC, d.LoanDetailId ASC \
                        """
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            for row in rows:
                self.view_all_tree.insert("", tk.END, values=row)
        except pymssql.Error as e:
            messagebox.showerror("Database Error", f"Error loading loan details:\n{e}", parent=self)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _get_id_from_combobox(self, combo_var, data_list, key_name):
        """Lấy ID từ text combobox."""
        display_text = combo_var.get()
        if not display_text:
            return None

        # Tách ID từ chuỗi ví dụ "ID: 123 - ..."
        try:
            id_part = display_text.split("-")[0].strip()
            id_value = id_part.split(":")[-1].strip()
            return int(id_value)
        except:
            return None

    def _on_add_book_to_list(self):
        copy_id = self._get_id_from_combobox(self.copy_id_to_add_var, self.copies_list, 'CopyId')
        if not copy_id:
            messagebox.showwarning("Invalid ID", "Vui lòng chọn một sách.", parent=self)
            return

        copy_id_str = str(copy_id)
        if copy_id_str in self.temp_loan_list:
            messagebox.showinfo("Duplicate", "Sách này đã có trong danh sách mượn.", parent=self)
            return

        self.temp_loan_list.append(copy_id_str)
        title = "N/A"
        for c in self.copies_list:
            if c['CopyId'] == copy_id:
                title = c['Title']
                break

        self.loan_tree.insert("", "end", values=(copy_id_str, title))
        self.copy_id_to_add_var.set("")
        self.copy_id_combobox.focus()

    def _on_remove_book_from_list(self):
        selected_item = self.loan_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Vui lòng chọn một sách để xóa.", parent=self)
            return

        values = self.loan_tree.item(selected_item, "values")
        copy_id = values[0]
        self.temp_loan_list.remove(copy_id)
        self.loan_tree.delete(selected_item)

    def _on_confirm_loan(self):
        # 1. Lấy ID
        reader_id = self._get_id_from_combobox(self.reader_id_var, self.readers_list, 'ReaderId')
        staff_id = self._get_id_from_combobox(self.staff_id_var, self.staff_list, 'StaffId')

        if not reader_id or not staff_id:
            messagebox.showwarning("Invalid Info", "Vui lòng chọn Reader và Staff.", parent=self)
            return

        # 2. Lấy Ngày Giờ Hẹn Trả
        try:
            due_date_str = self.due_date_date_var.get()
            due_hour_str = self.due_date_hour_var.get()
            due_min_str = self.due_date_min_var.get()

            full_due_date_str = f"{due_date_str} {due_hour_str}:{due_min_str}:00"
            datetime.datetime.strptime(full_due_date_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            messagebox.showwarning("Invalid Date/Time",
                                   "Định dạng Ngày hẹn trả không hợp lệ.\nPhải là YYYY-MM-DD và Giờ/Phút hợp lệ.",
                                   parent=self)
            return

        if not self.temp_loan_list:
            messagebox.showwarning("No Books", "Vui lòng thêm ít nhất một cuốn sách vào phiếu mượn.", parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Confirm Loan",
                                   f"Tạo phiếu mượn cho Reader ID: {reader_id}\n"
                                   f"Hẹn trả lúc: {full_due_date_str}\n"
                                   f"Tổng số sách: {len(self.temp_loan_list)}\n"
                                   "Bạn có chắc chắn không?", parent=self):
            return

        # 4. Gọi controller
        success, message = create_new_loan(
            reader_id=int(reader_id),
            staff_id=int(staff_id),
            due_date=full_due_date_str,
            list_of_copy_ids=[int(cid) for cid in self.temp_loan_list]
        )

        if success:
            messagebox.showinfo("Success", message, parent=self)
            self._clear_loan_form()
            self._load_combobox_data()  # Reload combobox để cập nhật danh sách sách
            self._load_all_loan_details()  # Reload bảng View All
        else:
            messagebox.showerror("Error", message, parent=self)

    def _on_return_book(self):
        # 1. Lấy Copy ID từ combobox
        copy_id = self._get_id_from_combobox(self.copy_id_to_return_var, [], 'CopyId')

        if not copy_id:
            messagebox.showwarning("Invalid ID", "Vui lòng chọn sách (Copy ID) để trả.", parent=self)
            return

        # 2. Lấy Ngày Giờ Trả
        try:
            return_date_str = self.return_date_date_var.get()
            return_hour_str = self.return_date_hour_var.get()
            return_min_str = self.return_date_min_var.get()

            full_return_date_str = f"{return_date_str} {return_hour_str}:{return_min_str}:00"
            datetime.datetime.strptime(full_return_date_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            messagebox.showwarning("Invalid Date/Time",
                                   "Định dạng Ngày trả không hợp lệ.\nPhải là YYYY-MM-DD và Giờ/Phút hợp lệ.",
                                   parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Confirm Return",
                                   f"Xác nhận trả sách (Copy ID: {copy_id})\nVào lúc: {full_return_date_str}?",
                                   parent=self):
            return

        # 4. Gọi controller
        success, message = return_book_copy(int(copy_id), full_return_date_str)

        # 5. Xử lý kết quả
        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.copy_id_to_return_var.set("")
            self._load_combobox_data()  # Reload combobox
            self._load_all_loan_details()  # Reload bảng View All
        else:
            messagebox.showerror("Error", message, parent=self)

    def _clear_loan_form(self):
        """Xóa form sau khi tạo loan thành công."""
        self.reader_id_var.set("")
        self.staff_id_var.set("")
        self.due_date_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.due_date_hour_var.set("17")
        self.due_date_min_var.set("00")
        self.copy_id_to_add_var.set("")
        self.temp_loan_list.clear()
        for item in self.loan_tree.get_children():
            self.loan_tree.delete(item)