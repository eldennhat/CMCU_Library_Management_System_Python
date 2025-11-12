import tkinter as tk
from tkinter import ttk
from tkmacosx import Button as macButton
from controller.view_controller.Loan_controller import get_loan_details_by_id
 #=======ĐÂY LÀ VIEW Ở TAB DETAILS TRONG LOAN MANAGER HỖ TRỌ CLICK ĐÚP VÀO 1 PHIẾU MƯỢN NÀO ĐÓ POP RA MENU THÔNG TIN PHIẾU MƯỢN
class LoanDetailView(tk.Toplevel):
    #Là cửa sổ pop up
    def __init__(self, parent, loan_id):
        super().__init__(parent)
        self.loan_id = loan_id

        self.title(f"Loan Details #{self.loan_id}")
        self.geometry("600x450")
        self.resizable(False, False)

        # --- Khóa cửa sổ cha (giống RegisterView) ---
        self.transient(parent)
        self.grab_set()

        # --- Tạo 2 khung chính ---
        info_frame = ttk.LabelFrame(self, text="Loan Infomation", padding=15)
        info_frame.pack(fill="x", padx=10, pady=10)

        books_frame = ttk.LabelFrame(self, text="Loan List", padding=15)
        books_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Nút Đóng ---
        close_button = macButton(
            self, text="Close", command=self.destroy,
            bg="#f44336", fg="white", borderwidth=4
        )
        close_button.pack(fill="x", ipady=5, padx=10, pady=(0, 10))

        # --- Gọi Controller và nạp dữ liệu ---
        self.load_data(info_frame, books_frame)

    def load_data(self, info_frame, books_frame):
        #Gọi controller
        loan_info, book_list = get_loan_details_by_id(self.loan_id)

        # 2. Nạp dữ liệu vào Khung Thông Tin (dùng grid)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)

        # (Hàng 1)
        ttk.Label(info_frame, text="Reader:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=loan_info['ReaderName']).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text="Phone:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=loan_info['ReaderPhone']).grid(row=0, column=3, sticky="w", padx=5, pady=2)

        # (Hàng 2)
        ttk.Label(info_frame, text="Staff:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=loan_info['StaffName']).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # (Hàng 3)
        ttk.Label(info_frame, text="Loan date:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=str(loan_info['LoanDate'])).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text="Due Date:").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=str(loan_info['DueDate'])).grid(row=2, column=3, sticky="w", padx=5, pady=2)

        #Nạp dữ liệu vào bảng sách
        columns = ("copy_id", "title", 'returned',"deposit","fine")
        tree = ttk.Treeview(books_frame, columns=columns)
        tree.pack(fill="both", expand= True)

        tree.heading("copy_id", text="Copy ID")
        tree.heading("title", text="Book Title")
        tree.heading("returned", text="Returned Date")
        tree.heading("deposit", text = "Deposit")
        tree.heading("fine", text = "Fine")


        tree.column("copy_id", width=80)
        tree.column("title", width=250)
        tree.column("returned", width=100)
        tree.column("deposit", width=100)
        tree.column("fine", width=100)

        for book in book_list:
            #Xử lý ngày trả
            returned_date = book['ReturnedDate'] if book['ReturnedDate'] else "Chưa trả"
            fine = f"{book['Fine']:,.0f}" if book['Fine'] else "0"

            tree.insert("", "end", values=(
                book['CopyId'],
                book['BookTitle'],
                returned_date,
                book['Deposit'],
                fine
            ))


