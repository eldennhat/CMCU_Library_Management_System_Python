import tkinter as tk
from tkinter import ttk, messagebox
from tkmacosx import Button as macButton

from controller.view_controller.Book_copy_controller import add_book_copy, fetch_book_ids, update_book_copy, \
    delete_book_copy, get_all_copies, search_book_copies


BG_COLOR = "#EEEEEE"
WINDOW_BG = "#54C5E8"

# --- CÀI ĐẶT CHUNG ---
APP_FONT = ("Arial", 13)
APP_FONT_LARGE = ("Arial", 17, "bold")


class BookCopyMenuView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.app_font = APP_FONT
        self.app_font_large = APP_FONT_LARGE

        # GHI CHÚ: Thêm biến cho OptionMenu
        self.book_id_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.book_id_title_map = {}  # Để lưu {BookID: Title}

        self.create_widgets()

        # --- Tải dữ liệu ban đầu ---
        # 1. Lấy map {ID: Title}
        self.book_id_title_map = self.load_book_id_and_titles()
        # 2. Cập nhật OptionMenu
        self.update_book_id_options()
        # 3. Tải bảng
        self.load_all_copies()

    def only_numbers(self, entry_widget):
        text = entry_widget.get()
        filtered = ''.join(ch for ch in text if ch.isdigit())
        if text != filtered:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filtered)

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        # Bạn có thể tạo các tab khác ở đây
        tab_book_copy = tk.Frame(tab_control, bg=BG_COLOR)  # Tab chính
        tab_control.add(tab_book_copy, text='Quản lý Bản sao Sách')
        tab_control.pack(expand=1, fill="both")

        # === Frame chính chứa toàn bộ nội dung ===
        main_frame = tk.Frame(tab_book_copy, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== IV. Khung nút bấm =======
        frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
        frame_buttons.pack(fill="x", padx=5, pady=5, side="bottom")

        self.btn_add = macButton(
            frame_buttons, text="Thêm", font=self.app_font_large,
            bg="#4CAF50", fg="white", command=self.on_add_book_copy_click, relief="raised", borderwidth=4
        )
        self.btn_add.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_update = macButton(
            frame_buttons, text="Cập nhật", font=self.app_font_large,
            bg="#F44336", fg="white", command=self.on_update_book_copy, relief="raised", borderwidth=4
        )
        self.btn_update.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_remove = macButton(
            frame_buttons, text="Xóa", font=self.app_font_large,
            bg="#2196F3", fg="white", command=self.on_delete_book_copy_click, relief="raised", borderwidth=4
        )
        self.btn_remove.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_load = macButton(
            frame_buttons, text="Làm mới", font=self.app_font_large,
            bg="#FF9800", fg="white", command=self.clear_form_and_reload, relief="raised", borderwidth=4
        )
        self.btn_load.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # == I. Khung Search ======
        frame_search = tk.LabelFrame(main_frame, text="Tìm Bản sao Sách (theo Tên sách)", font=self.app_font_large,
                                     bg=BG_COLOR, padx=10, pady=5)
        frame_search.pack(fill="x", padx=10, pady=10, side="top")

        lbl_search = tk.Label(frame_search, text="Nhập nội dung:", font=self.app_font, bg=BG_COLOR)
        lbl_search.pack(side="left", padx=5)

        self.entry_search = tk.Entry(frame_search, font=self.app_font, width=40)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_search = macButton(frame_search, text="Tìm", command=self.search_copies, font=self.app_font,
                                    borderwidth=4, relief="raised")
        self.btn_search.pack(side="left", padx=(5, 0))

        #  == II. Khung Book Copy Details =======
        frame_details = tk.LabelFrame(main_frame, text="Chi tiết Bản sao Sách", font=self.app_font_large, bg=BG_COLOR,
                                      padx=10, pady=5)
        frame_details.pack(fill="x", padx=10, pady=5, side="top")

        frame_details.columnconfigure(1, weight=1)
        frame_details.columnconfigure(3, weight=1)

        # Hàng 0: Copy ID & Book ID
        lbl_copy_id = tk.Label(frame_details, text="Mã Bản sao:", font=APP_FONT, bg=BG_COLOR)
        lbl_copy_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_copy_id = tk.Entry(frame_details, font=APP_FONT, state="readonly")
        self.entry_copy_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        lbl_book_id = tk.Label(frame_details, text="Mã Đầu sách:", font=APP_FONT, bg=BG_COLOR)
        lbl_book_id.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # GHI CHÚ: Dùng OptionMenu
        self.combo_book_id = tk.OptionMenu(frame_details, self.book_id_var, "Đang tải...")
        self.combo_book_id.config(font=self.app_font, width=15)
        self.combo_book_id.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.book_id_var.trace_add("write", self.on_book_id_select)

        # Hàng 1: TItle
        lbl_book_title = tk.Label(frame_details, text="Tên sách:", font=APP_FONT, bg=BG_COLOR)
        lbl_book_title.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_book_title = tk.Entry(frame_details, width=40, state="readonly", font=self.app_font)
        self.entry_book_title.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        # Hàng 2: Publisher & Barcode
        lbl_publisher = tk.Label(frame_details, text="Nhà XB:", font=self.app_font, bg=BG_COLOR)
        lbl_publisher.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_publisher = tk.Entry(frame_details, font=self.app_font)
        self.entry_publisher.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        lbl_barcode = tk.Label(frame_details, text="Mã vạch:", font=self.app_font, bg=BG_COLOR)
        lbl_barcode.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_barcode = tk.Entry(frame_details, font=self.app_font)
        self.entry_barcode.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Hàng 3: Price & Status
        lbl_price = tk.Label(frame_details, text="Giá tiền (VNĐ):", font=self.app_font, bg=BG_COLOR)
        lbl_price.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_price = tk.Entry(frame_details, font=self.app_font)
        self.entry_price.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.entry_price.bind("<KeyRelease>", lambda e: self.only_numbers(self.entry_price))

        lbl_status = tk.Label(frame_details, text="Trạng thái:", font=self.app_font, bg=BG_COLOR)
        lbl_status.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        status_values = ['0 (Có sẵn)', '1 (Đang mượn)', '2 (Hư hỏng)', '-1 (Đã mất)']
        self.status_var.set(status_values[0])  # Set default
        self.combo_status = tk.OptionMenu(frame_details, self.status_var, *status_values)
        self.combo_status.config(font=self.app_font, width=15)
        self.combo_status.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # Hàng 4: Storage Note
        lbl_storage_note = tk.Label(frame_details, text="Vị trí/Kệ:", font=self.app_font, bg=BG_COLOR)
        lbl_storage_note.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_storage_note = tk.Entry(frame_details, font=self.app_font)
        self.entry_storage_note.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # ====== III. Bảng danh sách (Treeview) =======
        frame_tree = tk.Frame(main_frame, bg=BG_COLOR)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10, side="top")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical")
        columns = ("CopyId", "BookId", "Title", "Publisher", "Status", "Barcode", "Price", "StorageNote", "StatusInt")
        self.tree_copies = ttk.Treeview(
            frame_tree,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set
        )

        # Đặt tiêu đề cột
        self.tree_copies.heading("CopyId", text="Mã Bản sao")
        self.tree_copies.heading("BookId", text="Mã Đầu sách")
        self.tree_copies.heading("Title", text="Tên sách")
        self.tree_copies.heading("Publisher", text="Nhà XB")
        self.tree_copies.heading("Status", text="Trạng thái")
        self.tree_copies.heading("Barcode", text="Mã vạch")
        self.tree_copies.heading("Price", text="Giá tiền")
        self.tree_copies.heading("StorageNote", text="Vị trí/Kệ")

        # Căn chỉnh độ rộng cột
        self.tree_copies.column("CopyId", width=60)
        self.tree_copies.column("BookId", width=60)
        self.tree_copies.column("Title", width=200)
        self.tree_copies.column("Publisher", width=150)
        self.tree_copies.column("Status", width=80)
        self.tree_copies.column("Barcode", width=120)
        self.tree_copies.column("Price", width=80)
        self.tree_copies.column("StorageNote", width=150)
        self.tree_copies.column("Status", width=80, stretch= False)

        scrollbar.config(command=self.tree_copies.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_copies.pack(side="left", fill="both", expand=True)

        self.tree_copies.bind("<<TreeviewSelect>>", self.on_tree_select)

    # ========= CÁC HÀM ĐỂ CHẠY SỰ KIỆN ===========
    def on_tree_select(self, event):
        # Điền dữ liệu vào form khi nhấp vào bảng
        try:
            selected_item = self.tree_copies.selection()[0]
            values = self.tree_copies.item(selected_item, 'values')

            self.clear_form()  # Xóa form cũ

            self.entry_copy_id.config(state="normal")
            self.entry_copy_id.insert(0, values[0])  # CopyId
            self.entry_copy_id.config(state="readonly")

            self.book_id_var.set(str(values[1]))  # BookId (kích hoạt on_book_id_select)

            self.entry_book_title.config(state="normal")
            self.entry_book_title.insert(0, values[2])  # Book Title
            self.entry_book_title.config(state="readonly")

            self.entry_publisher.insert(0, values[3])  # PublisherName

            # values[4] là chữ tiếng Việt  Hiển thị trên bảng
            # values[8] là số (0) -> Dùng để set Combobox

            status_int = str(values[8])
            # Map số sang chuỗi trong Combobox
            status_map = {
                '0': '0 (Có sẵn)',
                '1': '1 (Đang mượn)',
                '2': '2 (Hư hỏng)',
                '-1': '-1 (Đã mất)'
            }
            # Set giá trị cho Combobox dựa trên số lấy được
            if status_int in status_map:
                self.status_var.set(status_map[status_int])


            self.entry_barcode.insert(0, values[5])  # Barcode
            self.entry_price.insert(0, str(values[6]))  # BookMoney
            self.entry_storage_note.insert(0, values[7])  # StorageNote

        except (IndexError, tk.TclError):
            pass  # Bỏ qua nếu click lỗi

    # CÁC HÀM LOAD DỮ LIỆU
    def clear_form(self):
        # Xoá trắng ô nhập liệu
        self.entry_copy_id.config(state="normal")
        self.entry_copy_id.delete(0, tk.END)
        self.entry_copy_id.config(state="readonly")

        if self.book_id_title_map:
            self.book_id_var.set(list(self.book_id_title_map.keys())[0])
        else:
            self.book_id_var.set("")

        self.entry_book_title.config(state="normal")
        self.entry_book_title.delete(0, tk.END)
        self.entry_book_title.config(state="readonly")

        self.entry_publisher.delete(0, tk.END)
        self.status_var.set('0 (Có sẵn)')  # Đặt về mặc định
        self.entry_storage_note.delete(0, tk.END)
        self.entry_barcode.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)

        if self.tree_copies.selection():
            try:
                self.tree_copies.selection_remove(self.tree_copies.selection()[0])
            except IndexError:
                pass
        print("Form đã được làm mới.")

    # Xoá dữ liệu cũ và update cho dữ liệu copy mới
    def load_all_copies(self, book_list=None):
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
        # Lấy BookId VÀ Title từ CSDL.
        #
        book_map = {}
        try:
            book_ids_list = fetch_book_ids()
            #Duyệt các list tuple đó
            for (book_id, title) in book_ids_list: #Gán bookid là key, title là value
                book_map[int(book_id)] = title
            return book_map
        except Exception as e:
            print(f"Lỗi khi lấy Book IDs: {e}")
            return {}

    def update_book_id_options(self):
        #Cập nhật OptionMenu với các BookID
        menu = self.combo_book_id.nametowidget(self.combo_book_id.cget('menu'))
        menu.delete(0, 'end')

        new_values = list(self.book_id_title_map.keys())
        if not new_values:
            menu.add_command(label="Không có BookID", state="disabled")
            self.book_id_var.set("")
            return

        for book_id in new_values:
            menu.add_command(label=book_id, command=lambda value=book_id: self.book_id_var.set(value))

        self.book_id_var.set(new_values[0])

    def on_book_id_select(self, *args):
        # Tự động điền Title khi chọn BookID
        try:
            selected_book_id = int(self.book_id_var.get())
            title = self.book_id_title_map.get(selected_book_id, "Không tìm thấy")

            self.entry_book_title.config(state="normal")
            self.entry_book_title.delete(0, tk.END)
            self.entry_book_title.insert(0, title) #Thêm tiêu đề
            self.entry_book_title.config(state="readonly")
        except ValueError:
            pass  # Bỏ qua nếu ID không hợp lệ

    # Kết hợp 2 hàm để xoá và load lại
    def clear_form_and_reload(self):
        print("Đang làm mới form và dữ liệu...")
        self.clear_form()
        self.load_all_copies()

    # CÁC HÀM CHỨC NĂNG
    # Thêm
    def on_add_book_copy_click(self):
        # Lấy dữ liệu
        book_id = self.book_id_var.get()
        publisher = self.entry_publisher.get()
        status_text = self.status_var.get()
        storage_note = self.entry_storage_note.get()
        barcode = self.entry_barcode.get()
        price = self.entry_price.get()

        # 2. Kiểm tra các ô bắt buộc
        if not book_id or not status_text or not price or not publisher or not barcode:
            messagebox.showerror("Lỗi", "Mã Đầu sách, Nhà XB, Trạng thái, Mã vạch và Giá tiền là bắt buộc!",
                                 parent=self)
            return

        # 3. KIỂM TRA BOOK ID
        try:
            book_id_int = int(book_id)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã Đầu sách không hợp lệ. Vui lòng chọn từ danh sách.", parent=self)
            return

        # 4. KIỂM TRA STATUS
        try:
            status_int = int(status_text.split(" ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Trạng thái không hợp lệ. Vui lòng chọn từ danh sách.", parent=self)
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
            messagebox.showerror("Lỗi", "Giá tiền phải là một số hợp lệ (ví dụ: 30000 hoặc 30.000)", parent=self)
            return

        # Gọi controller (bỏ CopyID)
        success = add_book_copy(book_id_int, publisher, status_int, storage_note, barcode, book_money)
        if success:
            messagebox.showinfo("Thành công", "Đã thêm Bản sao Sách thành công!", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi", "Thêm Bản sao Sách thất bại! (Mã vạch có thể đã tồn tại)", parent=self)

        # Update

    def on_update_book_copy(self):
        # Lấy dữ liệu từ GUI
        copy_id = self.entry_copy_id.get()
        book_id = self.book_id_var.get()
        publisher = self.entry_publisher.get()
        status_text = self.status_var.get()
        storage_note = self.entry_storage_note.get()
        barcode = self.entry_barcode.get()
        book_money_text = self.entry_price.get()

        # --- Kiểm tra dữ liệu ---
        if not copy_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một bản sao từ bảng để cập nhật.", parent=self)
            return

        # 2. Kiểm tra các ô bắt buộc
        if not book_id or not status_text or not book_money_text or not publisher or not barcode:
            messagebox.showerror("Lỗi", "Mã Đầu sách, Nhà XB, Trạng thái, Mã vạch và Giá tiền là bắt buộc!",
                                 parent=self)
            return

        # 3. KIỂM TRA ID
        try:
            book_id_int = int(book_id)
            copy_id_int = int(copy_id)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã Đầu sách / Mã Bản sao không hợp lệ", parent=self)
            return

        # 4. KIỂM TRA STATUS
        try:
            status_int = int(status_text.split(" ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Trạng thái không hợp lệ.", parent=self)
            return

        # 5. KIỂM TRA PRICE
        try:
            # 5a. Xóa dấu phẩy (,)
            price_no_commas = book_money_text.replace(",", "")

            # 5b. Xóa dấu chấm (.)
            price_cleaned = price_no_commas.replace(".", "")

            # 5c. Chuyển đổi chuỗi
            book_money = float(price_cleaned)

        except ValueError:
            messagebox.showerror("Lỗi", "Giá tiền phải là một số", parent=self)
            return
        # --- Kết thúc kiểm tra ---

        # Gọi controller
        success = update_book_copy(copy_id_int, book_id_int, publisher, status_int, storage_note, barcode, book_money)

        if success:
            messagebox.showinfo("Thành công", "Đã cập nhật Bản sao Sách thành công!")
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi", "Cập nhật Bản sao Sách thất bại!")

        # Xoá

    def on_delete_book_copy_click(self):
        copy_id = self.entry_copy_id.get()
        if not copy_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một bản sao sách để xóa!")
            return
        try:
            copy_id_int = int(copy_id)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã Bản sao không hợp lệ!")
            return
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa bản sao sách có Mã: {copy_id_int}?"):
            return

        success = delete_book_copy(copy_id_int)

        if success:
            messagebox.showinfo("Thành công", "Đã xóa Bản sao Sách thành công!")
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi", "Xóa Bản sao Sách thất bại! Sách có thể đang được mượn (trong Phiếu Mượn).",
                                 parent=self)

    def search_copies(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            messagebox.showwarning("Chưa nhập", "Vui lòng nhập Tên sách để tìm.", parent=self)
            return

        # 1. Gọi controller
        results = search_book_copies(keyword)

        if results is None:
            messagebox.showerror("Lỗi CSDL", "Không thể tìm kiếm", parent=self)
        elif not results:
            messagebox.showinfo("Không tìm thấy", f"Không tìm thấy bản sao nào khớp với '{keyword}'.", parent=self)
            # 2. Tải bảng trống
            self.load_all_copies(book_list=[])
        else:
            # 3. Tải kết quả tìm kiếm vào bảng
            self.load_all_copies(book_list=results)