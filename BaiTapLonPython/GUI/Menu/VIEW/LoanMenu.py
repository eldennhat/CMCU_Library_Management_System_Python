import tkinter as tk
from tkinter import ttk, messagebox
import pymssql
from GUI.Font.font import FONT_PIXELS
from tkmacosx import Button as macButton

from GUI.Menu.VIEW.LoanDetailView import LoanDetailView
from controller.view_controller.Loan_controller import create_new_loan, return_book_copy, delete_loan
from database.db_connector import get_db_connection
import datetime


class LoanMenu(tk.Frame):
    # =========Cài đặt VIEW============

    def __init__(self, parent):
        super().__init__(parent)
        self.pixel_font = (FONT_PIXELS, 10)
        self.pixel_font_bold = (FONT_PIXELS, 11, 'bold')

        # === TAB 1 (MƯỢN SÁCH) ===
        self.reader_id_var = tk.StringVar() #Chứa dữ liệu người dùng chọn ở combobox
        self.staff_id_var = tk.StringVar()
        default_due_datetime = datetime.datetime.now() + datetime.timedelta(days=7)
        self.due_date_date_var = tk.StringVar(value=default_due_datetime.strftime("%Y-%m-%d"))
        self.due_date_hour_var = tk.StringVar(value=default_due_datetime.strftime("%H"))
        self.due_date_min_var = tk.StringVar(value=default_due_datetime.strftime("%M"))
        self.copy_id_to_add_var = tk.StringVar() #Chứa dữ liệu ở combo box chọn ID sách mượn

        # === TAB 2 (TRẢ SÁCH) ===
        self.copy_id_to_return_var = tk.StringVar()
        self.return_date_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d")) #Mặc định là bây giờ
        self.return_date_hour_var = tk.StringVar(value=datetime.datetime.now().strftime("%H"))
        self.return_date_min_var = tk.StringVar(value=datetime.datetime.now().strftime("%M"))

        self.temp_loan_list = []
        self.readers_list = []
        self.staff_list = []
        self.copies_list = [] #Chứa danh sách copy còn mượn được

        self._setup_widgets()
        self._load_combobox_data()

    #======CÁC HÀM PHỤ TRỢ CHO DATABASE=========
    #Hàm phụ trợ để chạy truy vấn
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

    # Để load dữ liệu từ bảng sau khi thực hiện các câu lệnh Add
    def _load_combobox_data(self):
        #Tải dữ liệu cho cả 3 combobox.
        # 1. Tải Độc giả ( vào readerlist bằng lệnh truy vấn
        self.readers_list = self._fetch_data_from_db("SELECT ReaderId, FullName FROM Reader ORDER BY FullName")
        reader_display_list = [f"ID: {r['ReaderId']} - Tên: {r['FullName']}" for r in self.readers_list]
        if hasattr(self, 'reader_combobox'):
            self.reader_combobox['values'] = reader_display_list

        # 2. Tải Nhân viên (Staff)
        #Tải các nhân viên vào list
        self.staff_list = self._fetch_data_from_db("SELECT StaffId, FullName FROM Staff ORDER BY FullName")
        staff_display_list = [f"ID: {s['StaffId']} - Tên: {s['FullName']}" for s in self.staff_list]
        if hasattr(self, 'staff_combobox'):
            self.staff_combobox['values'] = staff_display_list

        # 3. Tải Sách  - Chỉ những sách "Available" (Status = 0)
        query_available = """
                          SELECT c.CopyId, b.Title
                          FROM BookCopy c
                                   JOIN Book b ON c.BookId = b.BookId
                          WHERE c.Status = 0
                          ORDER BY b.Title \
                          """
        # Lưu các copy mà còn mượn được
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
        #Trả ra các
        onloan_list = self._fetch_data_from_db(query_onloan)
        onloan_display = [f"CopyID: {c['CopyId']} - {c['Title']}" for c in onloan_list]
        if hasattr(self, 'copy_id_return_combobox'):
            self.copy_id_return_combobox['values'] = onloan_display

    #Hàm set up các widgets cho giao diện
    def _setup_widgets(self):
        #Khung
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        #Vẽ giao diện cho tạo Loan
        loan_frame = ttk.Frame(notebook, padding=10)
        notebook.add(loan_frame, text="Create New Loan")
        self._create_loan_tab(loan_frame)

        #Vẽ giao diện trả sách
        return_frame = ttk.Frame(notebook, padding=10)
        notebook.add(return_frame, text="Return Book")
        self._create_return_tab(return_frame)

        #Vẽ giap diện in ra tất cả
        view_all_frame = ttk.Frame(notebook, padding=10)
        notebook.add(view_all_frame, text="View All Details")
        self._create_view_all_tab(view_all_frame)

    #======================== 3 TAB CHỨC NĂNG CỦA LOAN MANAGER===============================
    #Tab tạo phiếu mượn
    def _create_loan_tab(self, parent):
        info_frame = tk.LabelFrame(parent, text="Loan Information")
        info_frame.pack(fill="x", pady=5, side = "top")

        info_frame.columnconfigure(1, weight=1)

        #Label cho chọn reader
        ttk.Label(info_frame, text="Reader:", font = (FONT_PIXELS, 9)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        #Combobox chứa tất cả các readerID
        self.reader_combobox = ttk.Combobox(info_frame, textvariable=self.reader_id_var, state="readonly", width=40, font= "Arial")
        self.reader_combobox.grid(row=0, column=1, padx=5, pady=5, columnspan=5, sticky="we")

        #Label chọn Staff
        ttk.Label(info_frame, text="Staff:", font = (FONT_PIXELS, 9)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        #Combobox chọn StaffId
        self.staff_combobox = ttk.Combobox(info_frame, textvariable=self.staff_id_var, state="readonly", width=40, font= "Arial")
        self.staff_combobox.grid(row=1, column=1, padx=5, pady=5, columnspan=5, sticky="we")

        # Ngày hẹn trả
        ttk.Label(info_frame, text="Due Date:", font = (FONT_PIXELS, 9)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.due_date_date_var, width=15).grid(row=2, column=1, padx=5, pady=5)

        #Frame cho thời gian
        time_frame = ttk.Frame(info_frame)
        time_frame.grid(row=2, column=2, columnspan=4, sticky="w")#vị trí
        ttk.Label(time_frame, text="Hour:", font= (FONT_PIXELS, 8)).pack(side="left", padx=(5, 2))
        ttk.Spinbox(time_frame, textvariable=self.due_date_hour_var, from_=0, to=23, width=3).pack(side="left") #Giờ hiện tại
        ttk.Label(time_frame, text="Minutes:", font = (FONT_PIXELS, 8)).pack(side="left", padx=(5, 2))
        ttk.Spinbox(time_frame, textvariable=self.due_date_min_var, from_=0, to=59, width=3).pack(side="left")#phút hiện tại



        # Dùng tk.Frame và pack() nó xuống DƯỚI CÙNG
        button_label = tk.Frame(parent)
        button_label.pack(fill="x", ipady=10, pady=10, padx=10, side="bottom")

        # : Cấu hình 3 cột  để 3 nút giãn đều
        button_label.columnconfigure(0, weight=1)
        button_label.columnconfigure(1, weight=1)
        button_label.columnconfigure(2, weight=1)

        confirm_button = macButton(button_label, text="CONFIRM", command=self._on_confirm_loan, bg="green", fg="white",
                                   font=self.pixel_font, borderwidth=4, relief="raised")
        #  sticky="we" để nút lấp đầy cột
        confirm_button.grid(row=0, column=0, padx=5, sticky="we")

        addBookButton = macButton(button_label, text="Add", command=self._on_add_book_to_list, bg="#BA0000",
                                  relief="raised",
                                  font=self.pixel_font, fg="white", borderwidth=4)
        addBookButton.grid(row=0, column=1, padx=5, sticky="we")

        removeBook = macButton(button_label, text="Remove", command=self._on_remove_book_from_list, bg="orange",
                               relief="raised", font=self.pixel_font, fg="white", borderwidth=4)
        removeBook.grid(row=0, column=2, padx=5, sticky="we")


        #Book frame
        book_frame = tk.LabelFrame(parent, text="Add Books to Loan")
        book_frame.pack(fill="both", expand=True, pady=5, side="top")


        # 1. Cấu hình grid cho book_frame
        book_frame.columnconfigure(1, weight=1)  # Cột 1 (Combobox) sẽ giãn
        book_frame.rowconfigure(1, weight=1)  # Hàng 1 (Treeview) sẽ giãn

        # 2. Hàng 0: ComboBox
        tk.Label(book_frame, text="Available Copy:", font=(FONT_PIXELS, 10)).grid(row=0, column=0, padx=5, pady=5,
                                                                                  sticky="w")
        self.copy_id_combobox = ttk.Combobox(book_frame, textvariable=self.copy_id_to_add_var, state="readonly",
                                             width=40, font="Arial")

        self.copy_id_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # 3. Hàng 1: Treeview (Giỏ hàng)
        self.loan_tree = ttk.Treeview(book_frame, columns=("CopyId", "Title"), show="headings", height=5)
        self.loan_tree.heading("CopyId", text="Book Copy ID")
        self.loan_tree.heading("Title", text="Book Title")
        self.loan_tree.column("CopyId", width=300, anchor="center")
        self.loan_tree.column("Title", width=500)
        #   grid(), columnspan=2 (chiếm 2 cột), sticky="nsew"
        self.loan_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")



    #Tab Trả sách
    def _create_return_tab(self, parent):
        main_frame = ttk.LabelFrame(parent, text="Return a Book", padding=20)
        main_frame.pack(expand=True, padx=50, pady=30)
        main_frame.columnconfigure(1, weight=1)

        tk.Label(main_frame, text="Copy ID (On Loan):", font=self.pixel_font).grid(row=0, column=0, padx=5, pady=10,
                                                                                    sticky="w")
        self.copy_id_return_combobox = ttk.Combobox(main_frame, textvariable=self.copy_id_to_return_var,
                                                    state="readonly", width=30)
        self.copy_id_return_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(main_frame, text="Return Date (Y-M-D):", font=self.pixel_font).grid(row=1, column=0, padx=5, pady=10,
                                                                                      sticky="w")
        return_date_entry = tk.Entry(main_frame, textvariable=self.return_date_date_var, width=30)
        return_date_entry.grid(row=1,column=1,padx=5, pady=10, sticky="ew")

        hour_frame = ttk.Frame(main_frame)
        hour_frame.grid(row=2, column=0, pady=5)
        ttk.Label(hour_frame, text="Hour (0-23):", font=self.pixel_font).pack(side="left", padx=5)
        ttk.Spinbox(hour_frame, textvariable=self.return_date_hour_var, from_=0, to=23, width=5
                   ).pack(side="left", padx=5)

        minute_frame = ttk.Frame(main_frame)
        minute_frame.grid(row=2, column=1, pady=5)
        ttk.Label(minute_frame, text="Minute (0-59):", font=self.pixel_font).pack(side="left", padx=5)
        ttk.Spinbox(minute_frame, textvariable=self.return_date_min_var, from_=0, to=59, width=5
                    ).pack(side="left", padx=5)

        macButton(main_frame, text="SUBMIT RETURN", command=self._on_return_book, bg="blue", fg="white", borderwidth = 4 , relief="raised",
                  font=self.pixel_font_bold, ).grid(row=3, column=0, columnspan=2, pady=20, ipady=10, sticky="nsew")

    #Tab Hiện tât cả
    def _create_view_all_tab(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True)

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10, padx=10)

        refresh_button = macButton(button_frame, text="Refresh Data", command=self._load_all_loan_details,
                                   bg="#007BFF", fg="white", font=self.pixel_font_bold,
                                   borderwidth=4, relief="raised")
        refresh_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        #  THÊM NÚT XÓA
        delete_button = macButton(button_frame, text="Delete Selected Loan", command=self._on_delete_loan_click,
                                  bg="#F44336", fg="white", font=self.pixel_font_bold,
                                  borderwidth=4, relief="raised")
        delete_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

        #Nút refesh được truyền vào command tải lại tất cả thông tin
        refresh_button.pack(pady=10, fill="x")

        scrollbar = ttk.Scrollbar(tree_frame, orient= "vertical")

        columns = ( "LoanId", "CopyId", "BookTitle", "ReturnedDate",
                   "StaffName", "ReaderName","ReaderId", "Fine", "Deposit")
        self.view_all_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.view_all_tree.yview)


        self.view_all_tree.heading("LoanId", text="Loan ID")
        self.view_all_tree.heading("CopyId", text="Copy ID")
        self.view_all_tree.heading("BookTitle", text="Book Title")
        self.view_all_tree.heading("ReturnedDate", text="Returned Date")
        self.view_all_tree.heading("StaffName", text="Staff Name")
        self.view_all_tree.heading("ReaderName", text="Reader Name")
        self.view_all_tree.heading("ReaderId", text="Reader ID")
        self.view_all_tree.heading("Fine", text="Fine")
        self.view_all_tree.heading("Deposit", text="Deposit")


        self.view_all_tree.column("LoanId", width=80, anchor="center")
        self.view_all_tree.column("CopyId", width=80, anchor="center")
        self.view_all_tree.column("BookTitle", width=200)
        self.view_all_tree.column("ReturnedDate", width=150, anchor="center")
        self.view_all_tree.column("StaffName", width=150)
        self.view_all_tree.column("ReaderName", width=150)
        self.view_all_tree.column("ReaderId", width=100)
        self.view_all_tree.column("Fine", width=100, anchor="e")
        self.view_all_tree.column("Deposit", width=100, anchor="e")

        scrollbar.pack(side="right", fill= "y")
        self.view_all_tree.pack(side="left", fill="both", expand=True)

        self.view_all_tree.bind("<Double-1>", self._on_tree_double_click)
        self._load_all_loan_details()


    #====================================== CÁC HÀM CHỨC NĂNG ==========================================================
    #HÀM LOAD LẠI TẤT CẢ DATA PHỤ TRỢ CHO TAB VIEW ALL
    def _load_all_loan_details(self):
        #Tải tất cả chi tiết phiếu mượn với thông tin đầy đủ."""
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
            #Query lấy tất cả dữ liệu có liên quan
            sql_query = """
                        SELECT 
                               l.LoanId, \
                               d.CopyId,\
                               b.Title    AS BookTitle, \
                               d.ReturnedDate, \
                               s.FullName AS StaffName, \
                               r.FullName AS ReaderName, \
                               r.ReaderId,\
                               d.Fine, \
                               d.Deposit
                        FROM LoanDetail AS d
                                 JOIN Loan AS l ON d.LoanId = l.LoanId
                                 JOIN BookCopy AS c ON d.CopyId = c.CopyId
                                 JOIN Book AS b ON c.BookId = b.BookId
                                 JOIN Staff AS s ON l.StaffId = s.StaffId
                                 JOIN Reader AS r ON l.ReaderId = r.ReaderId
                        ORDER BY l.LoanId DESC \
                        """
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            for row in rows: #insert vào tree
                self.view_all_tree.insert("", tk.END, values=row)
        except pymssql.Error as e:
            messagebox.showerror("Database Error", f"Error loading loan details:\n{e}", parent=self)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    #hàm hỗ trợ click đúp
    def _on_tree_double_click(self, event):

        #Được gọi khi người dùng double-click vào một hàng trong Tab 'View All'.

        # 1. Lấy hàng được chọn
        selected_item = self.view_all_tree.focus()
        if not selected_item:
            return  # Bỏ qua nếu click vào vùng trống

        # 2. Lấy dữ liệu của hàng đó
        values = self.view_all_tree.item(selected_item, "values")

        # 3. Lấy LoanId (Cột thứ 1, index 0)
        # (columns = , "LoanId", ...)
        try:
            loan_id = int(values[0])
        except (IndexError, ValueError):
            print("Error")
            return

        # 4. Tạo và mở cửa sổ pop-up
        detail_window = LoanDetailView(self, loan_id=loan_id)

        # 5. Chờ cho đến khi cửa sổ pop-up bị đóng
        self.wait_window(detail_window)


    #HÀM LẤY DỮ LIỆU ID  TỪ COMBOBOX
    def _get_id_from_combobox(self, combo_var, data_list, key_name):
        #Lấy ID từ text combobox
        display_text = combo_var.get() #Combo_var là các combobox có chứa ID để chọn
        if not display_text:
            return None

        # Tách ID từ chuỗi ví dụ "ID: 123 - ..."
        try:
            id_part = display_text.split("-")[0].strip()
            id_value = id_part.split(":")[-1].strip()
            return int(id_value)
        except:
            return None

    #*/===============================/**/===============================/**/===============================/*
    # SỰ KIỆN CHO NÚT THÊM SÁCH MƯỢN
    def _on_add_book_to_list(self):
        #Lấy copy id từ combobox
        copy_id = self._get_id_from_combobox(self.copy_id_to_add_var , self.copies_list, 'CopyId')
                                    #truyền copy_id từ combobox đc chọn được lấy từ list các copy được nhận từ câu lệnh truy vấn
        if not copy_id:
            messagebox.showwarning("Invalid ID", "Please chooese a book.", parent=self)
            return

        copy_id_str = str(copy_id)
        #Kiểm tra xem có trong danh sách mượn chưa
        if copy_id_str in self.temp_loan_list:
            messagebox.showinfo("Duplicate", "This book are in loan list", parent=self)
            return
        #Nếu Copy_chưa trong danh sách mượn thì thêm vào
        self.temp_loan_list.append(copy_id_str)
        title = "N/A"

        for c in self.copies_list:
            if c['CopyId'] == copy_id:
                title = c['Title'] #lấy Title có CopyId tương đương
                break

        self.loan_tree.insert("", "end", values=(copy_id_str, title)) #Thêm vào cây
        self.copy_id_to_add_var.set("")
        self.copy_id_combobox.focus()

    #SỰ KIỆN XOÁ SÁCH KHỎI DANH SÁCH
    def _on_remove_book_from_list(self):
        #Xoá sách khỏi danh sách
        selected_item = self.loan_tree.focus() #Chọn 1 sách để xoá trong loan tree để xoá bao gồm cả id và tên

        if not selected_item:
            messagebox.showwarning("No Selection", "Please chosse a book", parent=self)
            return

        values = self.loan_tree.item(selected_item, "values")
        copy_id = values[0]
        #Xoá copy_id đó ra khỏi danh sách sách mượn cho 1 độc giả
        self.temp_loan_list.remove(copy_id)
        #Xoá cho tree
        self.loan_tree.delete(selected_item)

    # HÀM SỰ KIỆN CHO NÚT CONFIRM LOAN
    def _on_confirm_loan(self):
        # 1. Lấy 2 ID từ 2 combobox reader và staff  được chọn
        reader_id = self._get_id_from_combobox(self.reader_id_var, self.readers_list, 'ReaderId')
        staff_id = self._get_id_from_combobox(self.staff_id_var, self.staff_list, 'StaffId')

        if not reader_id or not staff_id:
            messagebox.showwarning("Invalid Info", "Please choose reader and staff.", parent=self)
            return

        # 2. Lấy Ngày Giờ Hẹn Trả từ combobox
        try:
            due_date_str = self.due_date_date_var.get()
            due_hour_str = self.due_date_hour_var.get()
            due_min_str = self.due_date_min_var.get()

            full_due_date_str = f"{due_date_str} {due_hour_str}:{due_min_str}:00"
            datetime.datetime.strptime(full_due_date_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            messagebox.showwarning("Invalid Date/Time",
                                   "Date type are not true.\nMust be YYYY-MM-DD and hour/minutes ilegal.",
                                   parent=self)
            return

        if not self.temp_loan_list:
            messagebox.showwarning("No Books", "Please choose at least 1 book into loan list.", parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Confirm Loan",
                                   f"Create Loan Reader ID: {reader_id}\n"
                                   f"Due date at: {full_due_date_str}\n"
                                   f"Total Books: {len(self.temp_loan_list)}\n"
                                   "Are you sure?", parent=self):
            return

        # 4. Gọi controller ĐỂ TẠO PHIẾU MƯỢN
        success, message = create_new_loan(
            reader_id=int(reader_id),
            staff_id=int(staff_id),
            due_date=full_due_date_str,
            list_of_copy_ids=[int(cid) for cid in self.temp_loan_list] #load các list sách cho readerID đó
        )

        if success:
            messagebox.showinfo("Success", message, parent=self)
            self._clear_loan_form()
            self._load_combobox_data()  # Reload combobox để cập nhật danh sách sách
            self._load_all_loan_details()  # Reload bảng View All
        else:
            messagebox.showerror("Error", message, parent=self)

    #HÀM SỰ KIÊN CHO MENU TRẢ SÁCH
    def _on_return_book(self):
        # 1. Lấy Copy ID từ combobox
        copy_id = self._get_id_from_combobox(self.copy_id_to_return_var, [], 'CopyId')

        if not copy_id:
            messagebox.showwarning("Invalid ID", "Please chosse Id to return", parent=self)
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
                                   "Date type are not true.\nMust be YYYY-MM-DD and hour/minutes ilegal.",
                                   parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Confirm Return",
                                   f"Confirm return (Copy ID: {copy_id})\n IN: {full_return_date_str}?",
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

    def _on_delete_loan_click(self):

       #Được gọi khi nhấn nút 'Delete Selected Loan' ở Tab 3.

        # 1. Lấy hàng được chọn
        selected_item = self.view_all_tree.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một phiếu mượn từ bảng để xóa.", parent=self)
            return

        # 2. Lấy dữ liệu của hàng đó
        values = self.view_all_tree.item(selected_item, "values")

        try:
            # Cột 2 (index 1) là LoanId
            loan_id = int(values[0])
        except (IndexError, ValueError):
            messagebox.showerror("Lỗi", "Không thể lấy LoanId từ hàng đã chọn.", parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Xác nhận XÓA",
                                   f"Bạn có chắc muốn xóa TOÀN BỘ Phiếu Mượn ID: {loan_id}?\n\n"
                                   "CẢNH BÁO: Mọi chi tiết mượn/trả của phiếu này sẽ bị xóa VĨNH VIỄN, "
                                   "và các sách liên quan (nếu chưa trả) sẽ được trả về 'Available'.",
                                   parent=self, icon='warning'):
            return

        # 4. Gọi Controller
        success, message = delete_loan(loan_id)

        if success:
            messagebox.showinfo("Thành công", message, parent=self)
            # 5. Tải lại MỌI THỨ
            self._load_all_loan_details()  # Tải lại Tab 3
            self._load_combobox_data()  # Tải lại sách 'Available' và 'OnLoan'
        else:
            messagebox.showerror("Lỗi CSDL", message, parent=self)

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