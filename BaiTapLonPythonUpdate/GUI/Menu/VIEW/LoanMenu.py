import tkinter as tk
from tkinter import ttk, messagebox
import pymssql
# GHI CHÚ: Import Font (Đảm bảo đường dẫn đúng)
from GUI.Font.font import FONT_PIXELS
from tkmacosx import Button as macButton
import sys
import os

# GHI CHÚ: Thêm đường dẫn (đi lên 2 cấp: VIEW -> GUI -> root)
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)

# GHI CHÚ: Import các controller
from GUI.Menu.VIEW.LoanDetailView import LoanDetailView
from controller.view_controller.Loan_controller import create_new_loan, return_book_copy, delete_loan, get_loan_details, \
    _load_combobox_data
from database.db_connector import get_db_connection
import datetime


class LoanMenu(tk.Frame):
    # =========Cài đặt VIEW============

    def __init__(self, parent):
        super().__init__(parent)
        self.font = ("Arial", 13)
        self.font_bold = ("Arial", 17, 'bold')
        self.pixel_font = (FONT_PIXELS, 10)  # GHI CHÚ: Thêm định nghĩa pixel_font

        # === TAB 1 (MƯỢN SÁCH) ===
        self.reader_id_var = tk.StringVar()  # Chứa dữ liệu người dùng chọn ở combobox
        self.staff_id_var = tk.StringVar()
        default_due_datetime = datetime.datetime.now() + datetime.timedelta(days=7)
        self.due_date_date_var = tk.StringVar(value=default_due_datetime.strftime("%Y-%m-%d"))
        # GHI CHÚ: Sửa lại logic lấy giờ phút
        self.due_date_hour_var = tk.StringVar(value=default_due_datetime.strftime("%H"))
        self.due_date_min_var = tk.StringVar(value=default_due_datetime.strftime("%M"))
        self.copy_id_to_add_var = tk.StringVar()  # Chứa dữ liệu ở combo box chọn ID sách mượn

        # === TAB 2 (TRẢ SÁCH) ===
        self.copy_id_to_return_var = tk.StringVar()
        self.return_date_date_var = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d"))  # Mặc định là bây giờ
        self.return_date_hour_var = tk.StringVar(value=datetime.datetime.now().strftime("%H"))
        self.return_date_min_var = tk.StringVar(value=datetime.datetime.now().strftime("%M"))

        self.temp_loan_list = []
        self.readers_list = []
        self.staff_list = []
        self.copies_list = []  # Chứa danh sách copy còn mượn được

        self._setup_widgets()
        self._load_combobox_data()

    # ======CÁC HÀM PHỤ TRỢ=========
    # Load các dữ liệu vào các combobox
    def _load_combobox_data(self):
       #Gọi controller
        self.readers_list, self.staff_list, self.copies_list, onloan_list = _load_combobox_data()

        # 1. Tải các độc giả
        #Định nghĩa lại chuỗi thông tin cho độc giả để gửi lên combobox
        reader_display_list = [f"ID: {r['ReaderId']} - Tên: {r['FullName']}" for r in self.readers_list]
        if hasattr(self, 'reader_combobox'):
            self.reader_combobox['values'] = reader_display_list

        # 2. Tải Nhân viên
        staff_display_list = [f"ID: {s['StaffId']} - Tên: {s['FullName']}" for s in self.staff_list]
        if hasattr(self, 'staff_combobox'):
            self.staff_combobox['values'] = staff_display_list

        # 3. Tải Sách  - Chỉ những sách "Available" (Status = 0)
        copy_display_list = [f"CopyID: {c['CopyId']} - Tên: {c['Title']}" for c in self.copies_list]
        if hasattr(self, 'copy_id_combobox'):
            self.copy_id_combobox['values'] = copy_display_list

        # 4. Tải sách ĐANG MƯỢN (Status = 1) cho tab TRẢ SÁCH
        onloan_display = [f"CopyID: {c['CopyId']} - {c['Title']}" for c in onloan_list]
        if hasattr(self, 'copy_id_return_combobox'):
            self.copy_id_return_combobox['values'] = onloan_display


     # HÀM  HỖ TRỢ LẤY DỮ LIỆU ID TỪ COMBOBOX
    def _get_id_from_combobox(self, combo_var, data_list, key_name):
        # Lấy ID từ text combobox
        display_text = combo_var.get()  # Combo_var là các combobox có chứa ID để chọn
        if not display_text:
            return None

        # Tách ID từ chuỗi ví dụ "ID: 123 - ..."
        try:
            id_part = display_text.split("-")[0].strip()
            # GHI CHÚ: Sửa lại để lấy cả "CopyID"
            id_value = id_part.split(":")[-1].strip()
            return int(id_value)
        except Exception as e:
            print(f"Lỗi khi lấy ID từ combobox: {e}, Text: {display_text}")
            return None


    # HÀM SET UP GIAO DIỆN
    def _setup_widgets(self):
        # Khung
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Vẽ giao diện cho tạo Loan
        loan_frame = ttk.Frame(notebook, padding=10)
        notebook.add(loan_frame, text="Tạo phiếu mượn")
        self._create_loan_tab(loan_frame)

        # Vẽ giao diện trả sách
        return_frame = ttk.Frame(notebook, padding=10)
        notebook.add(return_frame, text="Trả sách")
        self._create_return_tab(return_frame)

        # Vẽ giap diện in ra tất cả
        view_all_frame = ttk.Frame(notebook, padding=10)
        notebook.add(view_all_frame, text="Hiện thị chi tiết")
        self._create_view_all_tab(view_all_frame)

    # ======================== 3 TAB CHỨC NĂNG CỦA QUẢN LÝ MƯỢN TRẢ===============================
    # Tab tạo phiếu mượn
    def _create_loan_tab(self, parent):
        info_frame = tk.LabelFrame(parent, text="Thông tin phiếu mượn", font=self.font_bold)
        info_frame.pack(fill="x", pady=5, side="top")

        info_frame.columnconfigure(1, weight=1)

        # Label cho chọn reader
        ttk.Label(info_frame, text="Độc giả:", font=self.font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Combobox chứa tất cả các readerID
        self.reader_combobox = ttk.Combobox(info_frame, textvariable=self.reader_id_var, state="readonly", width=40,
                                            font="Arial")
        self.reader_combobox.grid(row=0, column=1, padx=5, pady=5, columnspan=5, sticky="we")

        # Label chọn Staff
        ttk.Label(info_frame, text="Nhân viên:", font=self.font).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        # Combobox chọn StaffId
        self.staff_combobox = ttk.Combobox(info_frame, textvariable=self.staff_id_var, state="readonly", width=40,
                                           font="Arial")
        self.staff_combobox.grid(row=1, column=1, padx=5, pady=5, columnspan=5, sticky="we")

        # Ngày hẹn trả
        ttk.Label(info_frame, text="Hạn trả:", font=self.font).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(info_frame, textvariable=self.due_date_date_var, width=15).grid(row=2, column=1, padx=5, pady=5,
                                                                                  sticky="w")

        # Frame cho thời gian
        time_frame = ttk.Frame(info_frame)
        time_frame.grid(row=2, column=2, columnspan=4, sticky="w")  # vị trí
        ttk.Label(time_frame, text="Giờ:", font=self.font).pack(side="left", padx=(5, 2))
        ttk.Spinbox(time_frame, textvariable=self.due_date_hour_var, from_=0, to=23, width=3).pack(
            side="left")  # Giờ hiện tại
        ttk.Label(time_frame, text="Phút:", font=self.font).pack(side="left", padx=(5, 2))
        ttk.Spinbox(time_frame, textvariable=self.due_date_min_var, from_=0, to=59, width=3).pack(
            side="left")  # phút hiện tại

        # Dùng tk.Frame và pack() nó xuống DƯỚI CÙNG
        button_label = tk.Frame(parent)
        button_label.pack(fill="x", ipady=10, pady=10, padx=10, side="bottom")

        # : Cấu hình 3 cột  để 3 nút giãn đều
        button_label.columnconfigure(0, weight=1)
        button_label.columnconfigure(1, weight=1)
        button_label.columnconfigure(2, weight=1)

        confirm_button = macButton(button_label, text="HOÀN TẤT", command=self._on_confirm_loan, bg="green", fg="white",
                                   font=self.font_bold, borderwidth=4, relief="raised")
        #  sticky="we" để nút lấp đầy cột
        confirm_button.grid(row=0, column=0, padx=5, sticky="we")

        addBookButton = macButton(button_label, text="THÊM", command=self._on_add_book_to_list, bg="#BA0000",
                                  relief="raised",
                                  font=self.font_bold, fg="white", borderwidth=4)
        addBookButton.grid(row=0, column=1, padx=5, sticky="we")

        removeBook = macButton(button_label, text="SỬA", command=self._on_remove_book_from_list, bg="orange",
                               relief="raised", font=self.font_bold, fg="white", borderwidth=4)
        removeBook.grid(row=0, column=2, padx=5, sticky="we")

        # Book frame
        book_frame = tk.LabelFrame(parent, text="Thêm sách vào giỏ hàng", font=self.font_bold)
        book_frame.pack(fill="both", expand=True, pady=5, side="top")

        # 1. Cấu hình grid cho book_frame
        book_frame.columnconfigure(1, weight=1)  # Cột 1 (Combobox) sẽ giãn
        book_frame.rowconfigure(1, weight=1)  # Hàng 1 (Treeview) sẽ giãn

        # 2. Hàng 0: ComboBox
        tk.Label(book_frame, text="Những sách có thể mượn:", font=self.font_bold).grid(row=0, column=0, padx=5, pady=5,
                                                                                       sticky="w")
        self.copy_id_combobox = ttk.Combobox(book_frame, textvariable=self.copy_id_to_add_var, state="readonly",
                                             width=40, font="Arial")

        self.copy_id_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # 3. Hàng 1: Treeview (Giỏ hàng)
        self.loan_tree = ttk.Treeview(book_frame, columns=("CopyId", "Title"), show="headings", height=5)
        self.loan_tree.heading("CopyId", text="ID bản sao")
        self.loan_tree.heading("Title", text="Tiêu đề")
        self.loan_tree.column("CopyId", width=300, anchor="center")
        self.loan_tree.column("Title", width=500)
        self.loan_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    # Tab Trả sách
    def _create_return_tab(self, parent):
        main_frame = ttk.LabelFrame(parent, text="Trả sách", padding=20)
        main_frame.pack(fill="x", expand=False, padx=10, pady=10)  # GHI CHÚ: Sửa lại layout
        main_frame.columnconfigure(1, weight=1)

        tk.Label(main_frame, text="ID bản sao (Đang được mượn):", font=self.font).grid(row=0, column=0, padx=5, pady=10,
                                                                                       sticky="w")
        self.copy_id_return_combobox = ttk.Combobox(main_frame, textvariable=self.copy_id_to_return_var,
                                                    state="readonly", width=30, font="Arial")
        self.copy_id_return_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(main_frame, text="Ngày trả thực tế (Y-M-D):", font=self.font).grid(row=1, column=0, padx=5, pady=10,
                                                                                     sticky="w")
        return_date_entry = tk.Entry(main_frame, textvariable=self.return_date_date_var, width=30,
                                     font=self.font)
        return_date_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # GHI CHÚ: Gộp Giờ và Phút
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Label(time_frame, text="Giờ (0-23):", font=self.font).pack(side="left", padx=5)
        ttk.Spinbox(time_frame, textvariable=self.return_date_hour_var, from_=0, to=23, width=5
                    ).pack(side="left", padx=5)

        ttk.Label(time_frame, text="Phút (0-59):", font=self.font).pack(side="left", padx=5)
        ttk.Spinbox(time_frame, textvariable=self.return_date_min_var, from_=0, to=59, width=5
                    ).pack(side="left", padx=5)

        macButton(main_frame, text="HOÀN TẤT TRẢ", command=self._on_return_book, bg="blue", fg="white", borderwidth=4,
                  relief="raised",
                  font=self.font_bold, ).grid(row=3, column=0, columnspan=2, pady=20, ipady=10, sticky="nsew")

    # Tab Hiện tât cả
    def _create_view_all_tab(self, parent):
        tree_frame = ttk.Frame(parent)

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10, padx=10)

        refresh_button = macButton(button_frame, text="Làm mới dữ liệu", command=self._load_all_loan_details,
                                   bg="#007BFF", fg="white", font=self.font_bold,
                                   borderwidth=4, relief="raised")
        refresh_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        #  THÊM NÚT XÓA
        delete_button = macButton(button_frame, text="Xoá phiếu mượn được chọn", command=self._on_delete_loan_click,
                                  bg="#F44336", fg="white", font=self.font_bold,
                                  borderwidth=4, relief="raised")
        delete_button.pack(side="left", fill="x", expand=True, padx=(5, 0))



        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")

        columns = ("LoanId", "CopyId", "BookTitle", "ReturnedDate",
                   "StaffName", "ReaderName", "ReaderId", "Fine", "Deposit")
        self.view_all_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.view_all_tree.yview)

        self.view_all_tree.heading("LoanId", text="ID Phiếu")
        self.view_all_tree.heading("CopyId", text="ID bản sao")
        self.view_all_tree.heading("BookTitle", text="Tiêu đề")
        self.view_all_tree.heading("ReturnedDate", text="Ngày trả")
        self.view_all_tree.heading("StaffName", text="Tên nhân viên")
        self.view_all_tree.heading("ReaderName", text="Tên độc giả")
        self.view_all_tree.heading("ReaderId", text="ID độc giả")
        self.view_all_tree.heading("Fine", text="Tiền phạt")
        self.view_all_tree.heading("Deposit", text="Tiền cọc")

        self.view_all_tree.column("LoanId", width=80, anchor="center")
        self.view_all_tree.column("CopyId", width=80, anchor="center")
        self.view_all_tree.column("BookTitle", width=200)
        self.view_all_tree.column("ReturnedDate", width=150, anchor="center")
        self.view_all_tree.column("StaffName", width=150)
        self.view_all_tree.column("ReaderName", width=150)
        self.view_all_tree.column("ReaderId", width=100)
        self.view_all_tree.column("Fine", width=100, anchor="e")
        self.view_all_tree.column("Deposit", width=100, anchor="e")

        scrollbar.pack(side="right", fill="y")
        self.view_all_tree.pack(side="left", fill="both", expand=True)

        self.view_all_tree.bind("<Double-1>", self._on_tree_double_click)
        self._load_all_loan_details()

    # ====================================== CÁC HÀM CHỨC NĂNG ==========================================================
    # ==CÁC HÀM CHO TAB VIEW ALL==
    # HÀM LOAD LẠI TẤT CẢ DATA PHỤ TRỢ CHO TAB VIEW ALL
    def _load_all_loan_details(self):
        # Tải tất cả chi tiết phiếu mượn với thông tin đầy đủ."""
        for item in self.view_all_tree.get_children():
            self.view_all_tree.delete(item)

        #Gọi controller
        rows = get_loan_details()
        for row in rows:  # insert vào tree
            self.view_all_tree.insert("", tk.END, values=row)


    # hàm hỗ trợ click đúp
    def _on_tree_double_click(self, event):

        # Được gọi khi người dùng double-click vào một hàng trong Tab View All.

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

        # 6. Tải lại dữ liệu
        self._load_all_loan_details()

    # Hàm cho nút xoá 1 phiếu mượn ở tab view all
    def _on_delete_loan_click(self):
        # Được gọi khi nhấn nút 'Delete Selected Loan' ở Tab Chi tiết
        # 1. Lấy hàng được chọn
        selected_item = self.view_all_tree.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một phiếu mượn từ bảng để xóa.", parent=self)
            return

        # 2. Lấy dữ liệu của hàng đó
        values = self.view_all_tree.item(selected_item, "values")

        try:
            # Cột 1 (index 0) là LoanId
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



    # */===============================/**/===============================/**/===============================/*
    # CÁC HÀM SỰ KIỆN CHO TAB MƯỢN SÁCH
    # SỰ KIỆN CHO NÚT THÊM SÁCH MƯỢN
    def _on_add_book_to_list(self):
        # Lấy copy id từ combobox
        copy_id = self._get_id_from_combobox(self.copy_id_to_add_var, self.copies_list, 'CopyId')
        # truyền copy_id từ combobox đc chọn được lấy từ list các copy được nhận từ câu lệnh truy vấn
        if not copy_id:
            messagebox.showwarning("ID không hợp lệ", "Hãy chọn 1 cuốn sách.", parent=self)
            return

        # GHI CHÚ: Chuyển sang dùng INT cho nhất quán
        if copy_id in self.temp_loan_list:
            messagebox.showinfo("Trùng lặp", "Sách đã có trong giỏ hàng", parent=self)
            return

        # Nếu Copy_chưa trong danh sách mượn thì thêm vào
        self.temp_loan_list.append(copy_id)
        title = "N/A"

        for c in self.copies_list:
            if c['CopyId'] == copy_id:
                title = c['Title']  # lấy Title có CopyId tương đương
                break

        self.loan_tree.insert("", "end", values=(copy_id, title))  # Thêm vào cây
        self.copy_id_to_add_var.set("")
        self.copy_id_combobox.focus()

    # SỰ KIỆN XOÁ SÁCH KHỎI DANH SÁCH
    def _on_remove_book_from_list(self):
        # Xoá sách khỏi danh sách
        selected_item = self.loan_tree.focus()  # Chọn 1 sách để xoá trong loan tree để xoá bao gồm cả id và tên

        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Hãy chọn 1 cuốn sách để xoá", parent=self)
            return

        values = self.loan_tree.item(selected_item, "values")
        copy_id = int(values[0])  # GHI CHÚ: Dùng INT
        # Xoá copy_id đó ra khỏi danh sách sách mượn cho 1 độc giả
        self.temp_loan_list.remove(copy_id)
        # Xoá cho tree
        self.loan_tree.delete(selected_item)

    # HÀM SỰ KIỆN CHO NÚT CONFIRM LOAN
    def _on_confirm_loan(self):
        # 1. Lấy 2 ID từ 2 combobox reader và staff  được chọn
        reader_id = self._get_id_from_combobox(self.reader_id_var, self.readers_list, 'ReaderId')
        staff_id = self._get_id_from_combobox(self.staff_id_var, self.staff_list, 'StaffId')

        if not reader_id or not staff_id:
            messagebox.showwarning("Thông tin không hợp lệ", "Hãy chọn nhân viên và độc giả", parent=self)
            return

        # 2. Lấy Ngày Giờ Hẹn Trả từ combobox
        try:
            due_date_str = self.due_date_date_var.get()
            due_hour_str = self.due_date_hour_var.get()
            due_min_str = self.due_date_min_var.get()

            # GHI CHÚ: Sửa lại theo CSDL (datetime2)
            full_due_date_str = f"{due_date_str} {due_hour_str}:{due_min_str}:00"
            datetime.datetime.strptime(full_due_date_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            messagebox.showwarning("Ngày/Giờ không hợp lệ",
                                   "Kiểu ngày tháng không đúng.\nPhải là YYYY-MM-DD và Giờ/Phút hợp lệ.",
                                   parent=self)
            return

        if not self.temp_loan_list:
            messagebox.showwarning("Chưa có sách", "Hãy chọn ít nhất 1 cuốn sách vào giỏ hàng.", parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Xác nhận Mượn",
                                   f"Tạo phiếu mượn cho Độc giả ID: {reader_id}\n"
                                   f"Hẹn trả lúc: {full_due_date_str}\n"
                                   f"Tổng số sách: {len(self.temp_loan_list)}\n"
                                   "Bạn có chắc chắn không?", parent=self):
            return

        # 4. Gọi controller ĐỂ TẠO PHIẾU MƯỢN
        success, message = create_new_loan(
            reader_id=int(reader_id),
            staff_id=int(staff_id),
            due_date=full_due_date_str,
            list_of_copy_ids=self.temp_loan_list  # GHI CHÚ: Đã là list các int
        )

        if success:
            messagebox.showinfo("Thành công", message, parent=self)
            self._clear_loan_form()
            self._load_combobox_data()  # Reload combobox để cập nhật danh sách sách
            self._load_all_loan_details()  # Reload bảng View All
        else:
            messagebox.showerror("Lỗi", message, parent=self)

    # =======HÀM SỰ KIÊN CHO TAB TRẢ SÁCH======
    def _on_return_book(self):
        # 1. Lấy Copy ID từ combobox
        copy_id = self._get_id_from_combobox(self.copy_id_to_return_var, [], 'CopyId')

        if not copy_id:
            messagebox.showwarning("ID không hợp lệ", "Hãy chọn 1 ID sách để trả", parent=self)
            return

        # 2. Lấy Ngày Giờ Trả
        try:
            return_date_str = self.return_date_date_var.get()
            return_hour_str = self.return_date_hour_var.get()
            return_min_str = self.return_date_min_var.get()

            full_return_date_str = f"{return_date_str} {return_hour_str}:{return_min_str}:00"
            datetime.datetime.strptime(full_return_date_str, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            messagebox.showwarning("Ngày/Giờ không hợp lệ",
                                   "Kiểu ngày tháng không đúng.\nPhải là YYYY-MM-DD và Giờ/Phút hợp lệ.",
                                   parent=self)
            return

        # 3. Hỏi xác nhận
        if not messagebox.askyesno("Xác nhận Trả",
                                   f"Xác nhận trả sách (Mã Bản sao: {copy_id})\nVào lúc: {full_return_date_str}?",
                                   parent=self):
            return

        # 4. Gọi controller
        success, message = return_book_copy(int(copy_id), full_return_date_str)

        # 5. Xử lý kết quả
        if success:
            messagebox.showinfo("Thành công", message, parent=self)
            self.copy_id_to_return_var.set("")
            self._load_combobox_data()  # Reload combobox
            self._load_all_loan_details()  # Reload bảng View All
        else:
            messagebox.showerror("Lỗi", message, parent=self)



    def _clear_loan_form(self):
        """Xóa form sau khi tạo loan thành công."""
        self.reader_id_var.set("")
        self.staff_id_var.set("")

        # GHI CHÚ: Sửa lại logic reset ngày
        default_due_datetime = datetime.datetime.now() + datetime.timedelta(days=7)
        self.due_date_date_var.set(default_due_datetime.strftime("%Y-%m-%d"))
        self.due_date_hour_var.set(default_due_datetime.strftime("%H"))
        self.due_date_min_var.set(default_due_datetime.strftime("%M"))

        self.copy_id_to_add_var.set("")
        self.temp_loan_list.clear()
        for item in self.loan_tree.get_children():
            self.loan_tree.delete(item)