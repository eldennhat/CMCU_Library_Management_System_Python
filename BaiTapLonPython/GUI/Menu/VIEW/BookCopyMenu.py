import tkinter as tk
from tkinter import ttk, messagebox
from tkmacosx import Button as macButton

from controller.view_controller.Book_copy_controller import add_book_copy, fetch_book_ids, update_book_copy, \
    delete_book_copy, get_all_copies, search_book_copies
from database.db_connector import get_db_connection

BG_COLOR = "#EEEEEE"
WINDOW_BG = "#54C5E8"

# --- CÀI ĐẶT CHUNG ---
APP_FONT = ("Press Start 2P", 10, "bold")
APP_FONT_LARGE = ("Press Start 2P", 12, "bold")

class BookCopyMenuView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.app_font = APP_FONT
        self.app_font_large = APP_FONT_LARGE
        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        # Bạn có thể tạo các tab khác ở đây
        tab_book_copy = tk.Frame(tab_control)  # Tab chính
        tab_control.add(tab_book_copy, text='Book Copy Manager')
        tab_control.pack(expand=1, fill="both")

        # === Frame chính chứa toàn bộ nội dung ===
        main_frame = tk.Frame(tab_book_copy, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== IV. Khung nút bấm =======
        frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
        frame_buttons.pack(fill="x", padx=5, pady=5, side= "bottom")

        self.btn_add = macButton(
            frame_buttons, text="ADD", font=self.app_font_large,
            bg="#4CAF50", fg="white", width=4, command=self.on_add_book_copy_click, relief="raised", borderwidth=4
        )
        self.btn_add.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_update = macButton(
            frame_buttons, text="UPDATE", font=self.app_font_large,
            bg="#F44336", fg="white", width=4, command=self.on_update_book_copy,relief= "raised", borderwidth=4
        )
        self.btn_update.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_remove = macButton(
            frame_buttons, text="REMOVE", font=self.app_font_large,
            bg="#2196F3", fg="white", width=4, command=self.on_delete_book_copy_click,relief= "raised", borderwidth=4
        )
        self.btn_remove.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_load = macButton(
            frame_buttons, text="LOAD FORM", font=self.app_font_large,
            bg="#FF9800", fg="white", width=6, command=self.clear_form_and_reload,relief= "raised", borderwidth=4
        )
        self.btn_load.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # == I. Khung Search ======
        frame_search = tk.LabelFrame(main_frame, text="Search Book Copy", )
        frame_search.pack(fill="x", padx=10, pady=10, side="top")

        lbl_search = tk.Label(frame_search, text="Enter text:")
        lbl_search.pack(side= "left", padx= 5)

        self.entry_search = tk.Entry(frame_search, font=self.app_font, width=40)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_search = macButton(frame_search, text="Search", command = self.search_copies)
        self.btn_search.pack(side= "left", padx=(5, 0))

        #  == II. Khung Book Copy Details =======
        frame_details = tk.LabelFrame(main_frame, text="Book Copy Details")
        frame_details.pack(fill="x", padx=10, pady=5)

        frame_details.columnconfigure(1, weight=1)
        frame_details.columnconfigure(3, weight=1)

        # Hàng 0: Copy ID & Book ID
        lbl_copy_id = tk.Label(frame_details, text="Copy ID:", font=APP_FONT)
        lbl_copy_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_copy_id = tk.Entry(frame_details, font=APP_FONT, state="readonly")
        self.entry_copy_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        lbl_book_id = tk.Label(frame_details, text="Book ID:", font=APP_FONT)
        lbl_book_id.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_book_id = ttk.Combobox(frame_details, state="readonly", width=1)
        self.combo_book_id.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        #  Gán sự kiện cho combobox
        self.combo_book_id.bind("<<ComboboxSelected>>", self.on_book_id_select)
        #Hàng 1: TItle
        lbl_book_title = tk.Label(frame_details, text="Book Title:", font=APP_FONT)
        lbl_book_title.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_book_title = tk.Entry(frame_details, width=40, state="readonly")
        self.entry_book_title.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        # Hàng 2: Publisher & Barcode
        lbl_publisher = tk.Label(frame_details, text="Publisher:", font=self.app_font)
        lbl_publisher.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_publisher = tk.Entry(frame_details)
        self.entry_publisher.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        lbl_barcode = tk.Label(frame_details, text="Barcode:", font=self.app_font)
        lbl_barcode.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_barcode = tk.Entry(frame_details)
        self.entry_barcode.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Hàng 3: Price & Status
        lbl_price = tk.Label(frame_details, text="Price:", font=self.app_font)
        lbl_price.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_price = tk.Entry(frame_details)
        self.entry_price.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        lbl_status = tk.Label(frame_details, text="Status:", font=self.app_font)
        lbl_status.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        status_values = ['-1', '0 ', '1', '2']
        self.combo_status = ttk.Combobox(frame_details, values=status_values, state="readonly")
        self.combo_status.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # Hàng 4: Storage Note
        lbl_storage_note = tk.Label(frame_details, text="Storage Note:", font=self.app_font)
        lbl_storage_note.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_storage_note = ttk.Entry(frame_details)
        self.entry_storage_note.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # ====== III. Bảng danh sách (Treeview) =======
        frame_tree = tk.Frame(main_frame)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10, side="top")

        scrollbar = ttk.Scrollbar(frame_tree, orient= "vertical")
        columns = ("CopyId", "BookId","Title", "Publisher", "Status", "Barcode", "Price", "StorageNote")
        self.tree_copies = ttk.Treeview(
            frame_tree,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set
        )

        # Đặt tiêu đề cột
        self.tree_copies.heading("CopyId", text="Copy ID")
        self.tree_copies.heading("BookId", text="Book ID")
        self.tree_copies.heading("Title", text="Title")
        self.tree_copies.heading("Publisher", text="Publisher")
        self.tree_copies.heading("Status", text="Status")
        self.tree_copies.heading("Barcode", text="Barcode")
        self.tree_copies.heading("Price", text="Price")
        self.tree_copies.heading("StorageNote", text="Storage Note")

        # Căn chỉnh độ rộng cột
        self.tree_copies.column("CopyId", width=60, anchor="center")
        self.tree_copies.column("BookId", width=60, anchor="center")
        self.tree_copies.column("Title", width=60, anchor="center")
        self.tree_copies.column("Publisher", width=150)
        self.tree_copies.column("Status", width=50, anchor="center")
        self.tree_copies.column("Barcode", width=120)
        self.tree_copies.column("Price", width=80, anchor="e")
        self.tree_copies.column("StorageNote", width=150)

        scrollbar.config(command=self.tree_copies.yview)
        scrollbar.pack(side= "right", fill= "y")
        self.tree_copies.pack(side="left", fill="both", expand=True)

        self.tree_copies.bind("<<TreeviewSelect>>", self.on_tree_select)


        # --- Tải dữ liệu ban đầu ---

        self.book_id_title_map = self.load_book_id_and_titles()
        self.combo_book_id['values'] = list(self.book_id_title_map.keys())

        self.load_all_copies()
        
    #========= CÁC HÀM ĐỂ CHẠY SỰ KIỆN ===========
    def on_tree_select(self, event):
        #Điền dữ liệu vào form khi nhấp vào bảng
        try:
            selected_item = self.tree_copies.selection()[0]
            values = self.tree_copies.item(selected_item, 'values')

            self.clear_form()  # Xóa form cũ

            self.entry_copy_id.config(state="normal")
            self.entry_copy_id.insert(0, values[0])  # CopyId
            self.entry_copy_id.config(state="readonly")
            self.combo_book_id.set(str(values[1]))  # BookId
            self.entry_book_title.config(state="normal")
            self.entry_book_title.insert(0, values[2])  # Book Title
            self.entry_book_title.config(state="readonly")
            self.entry_publisher.insert(0, values[3])  # PublisherName

            status_val = str(values[4])
            status_text = f"{status_val} ({'Available' if status_val == '0' else 'OnLoan' if status_val == '1' else 'Damaged' if status_val == '2' else 'Lost'})"
            self.combo_status.set(status_text)

            self.entry_barcode.insert(0, values[5])  # Barcode
            self.entry_price.insert(0, str(values[6]))  # BookMoney
            self.entry_storage_note.insert(0, values[7])  # StorageNote

        except (IndexError, tk.TclError):
            pass  # Bỏ qua nếu click lỗi



    # CÁC HÀM LOAD DỮ LIỆU
    def clear_form(self):
        #Xoá trắng ô nhập liệu
        self.entry_copy_id.config(state="normal")
        self.entry_copy_id.delete(0, tk.END)
        self.entry_copy_id.config(state="readonly")

        self.combo_book_id.set("")

        self.entry_book_title.config(state="normal")
        self.entry_book_title.delete(0, tk.END)
        self.entry_book_title.config(state="readonly")

        self.entry_publisher.delete(0, tk.END)
        self.combo_status.set("")
        self.entry_storage_note.delete(0, tk.END)
        self.entry_barcode.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)

        if self.tree_copies.selection():
            try:
                self.tree_copies.selection_remove(self.tree_copies.selection()[0])
            except IndexError:
                pass
        print("Form refreshed.")

    #Xoá dữ liệu cũ và update cho dữ liệu copy mới
    def load_all_copies(self ,book_list = None):
        #
        # Xóa Treeview và tải dữ liệu mới vào.
        # Nếu 'book_list' được cung cấp từ tìm kiếm, tải list sách.
        # Nếu không, gọi CSDL để lấy tất cả.
        #
        for item in self.tree_copies.get_children():
            self.tree_copies.delete(item)

        if book_list is None:
            rows = get_all_copies()
        else:
            rows = book_list
        if rows:
            for row in rows:
                self.tree_copies.insert("", tk.END, values=row)

    def load_book_id_and_titles(self):
        #Lấy BookId VÀ Title từ CSDL.
        conn = get_db_connection()
        if not conn: return {}
        cursor = conn.cursor(as_dict=True)
        book_map = {}
        try:
            cursor.execute("SELECT BookId, Title FROM Book")
            for row in cursor.fetchall():
                book_map[row['BookId']] = row['Title']
            return book_map
        except Exception as e:
            print(f"Error when collecting Book IDs: {e}")
            return {}
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def on_book_id_select(self, event):
        #Tự động điền Title khi chọn BookID
        try:
            selected_book_id = int(self.combo_book_id.get())
            title = self.book_id_title_map.get(selected_book_id, "Không tìm thấy")

            self.entry_book_title.config(state="normal")
            self.entry_book_title.delete(0, tk.END)
            self.entry_book_title.insert(0, title)
            self.entry_book_title.config(state="readonly")
        except ValueError:
            pass  # Bỏ qua nếu ID không hợp lệ

    #Kết hợp 2 hàm để xoá và load lại
    def clear_form_and_reload(self):
        print("Refreshing form and data...")
        self.clear_form()
        self.load_all_copies()

    # CÁC HÀM CHỨC NĂNG
    #Thêm
    def on_add_book_copy_click(self):
        # Lấy dữ liệu
        book_id = self.combo_book_id.get()
        publisher = self.entry_publisher.get()
        status_text = self.combo_status.get()
        storage_note = self.entry_storage_note.get()
        barcode = self.entry_barcode.get()
        price = self.entry_price.get()

        # 2. Kiểm tra các ô bắt buộc
        if not book_id or not status_text or not price or not publisher or not barcode:
            messagebox.showerror("Error", "Book ID, Publisher, Status, Barcode và Price là bắt buộc!", parent=self)
            return

        # 3. KIỂM TRA BOOK ID
        try:
            book_id_int = int(book_id)
        except ValueError:
            messagebox.showerror("Error", "Book ID không hợp lệ. Vui lòng chọn từ danh sách.", parent=self)
            return

        # 4. KIỂM TRA STATUS
        try:
            status_int = int(status_text.split(" ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Status không hợp lệ. Vui lòng chọn Status từ danh sách.", parent=self)
            return

        # 5. KIỂM TRA PRICE
        try:
            # 5a. Xóa dấu phẩy (,) (ví dụ: "30,000")
            price_no_commas = price.replace(",", "")

            # 5b. Xóa dấu chấm
            price_cleaned = price_no_commas.replace(".", "")

            # 5c. Chuyển đổi chuỗi SẠCH
            book_money = float(price_cleaned)
        except ValueError:
            messagebox.showerror("Error", "Price phải là một số hợp lệ (ví dụ: 30000 hoặc 30.000)", parent=self)
            return

        # Gọi controller (bỏ CopyID)
        success = add_book_copy(book_id, publisher, status_int, storage_note, barcode, book_money)
        if success:
            messagebox.showinfo("Success", "Book Copy Successfully Added!", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Error", "Add Book Copy Failed! (Barcode might exist)", parent=self)

    #Update
    def on_update_book_copy(self):
        # Lấy dữ liệu từ GUI
        copy_id = self.entry_copy_id.get()
        book_id = self.combo_book_id.get()
        publisher = self.entry_publisher.get()
        status = self.combo_status.get()
        storage_note = self.entry_storage_note.get()
        barcode = self.entry_barcode.get()
        book_money = self.entry_price.get()

        # --- Kiểm tra dữ liệu ---
        # 2. Kiểm tra các ô bắt buộc
        if not book_id or not status or not book_money or not publisher or not barcode:
            messagebox.showerror("Error", "Book ID, Publisher, Status, Barcode and Price", parent=self)
            return

        # 3. KIỂM TRA BOOK ID
        try:
            book_id_int = int(book_id)
        except ValueError:
            messagebox.showerror("Error", "Book ID Not Found", parent=self)
            return

        # 4. KIỂM TRA STATUS
        try:
            status_int = int(status.split(" ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Status Not Found.", parent=self)
            return

        # 5. KIỂM TRA PRICE
        try:
            # 5a. Xóa dấu phẩy (,)
            price_no_commas = book_money.replace(",", "")

            # 5b. Xóa dấu chấm (.)
            price_cleaned = price_no_commas.replace(".", "")

            # 5c. Chuyển đổi chuỗi
            book_money = float(price_cleaned)

        except ValueError:
            messagebox.showerror("Error", "Price must a numer", parent=self)
            return
        # --- Kết thúc kiểm tra ---

        #Gọi controller
        success = update_book_copy(copy_id,book_id, publisher, status_int, storage_note, barcode, book_money)

        if success:
            messagebox.showinfo("Success", "Book Copy Successfully Updated!")
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Error", "Update Book Copy Failed!")

    #Xoá
    def on_delete_book_copy_click(self):
        copy_id = self.entry_copy_id.get()
        if not copy_id:
            messagebox.showerror("Error", "Chose a book copy to delete!")
            return
        try:
            copy_id = int(copy_id)
        except ValueError:
            messagebox.showerror("Error", "CopyId is invalid!")
            return
        if not messagebox.askyesno("Confirm", f"Do you want to delete book copy with Copy Id: {copy_id}?"):
            return
        success = delete_book_copy(copy_id)
        if success:
            messagebox.showinfo("Success", "Book Copy Deleted Successfully!")
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Error", "Delete Book Copy Failed!", parent=self)

    def search_copies(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            messagebox.showwarning("Chưa nhập", "Please enter title to search.", parent=self)
            return

        # 1. Gọi controller
        results = search_book_copies(keyword)

        if results is None:
            messagebox.showerror("Database Error", "Can not search", parent=self)
        elif not results:
            messagebox.showinfo("Can not Find", f"Can Find a copy with '{keyword}'.", parent=self)
            # 2. Tải bảng trống
            self.load_all_copies(book_list=[])
        else:
            # 3. Tải kết quả tìm kiếm vào bảng
            self.load_all_copies(book_list=results)








