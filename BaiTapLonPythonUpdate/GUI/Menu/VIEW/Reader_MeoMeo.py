import tkinter as tk
from tkinter import ttk, messagebox
from GUI.Font.font import FONT_PIXELS
from controller.view_controller.Reader_controller import get_all_readers, add_reader, update_reader, delete_reader, \
    find_reader
from tkmacosx import  Button as macButton

# --- CÀI ĐẶT CHUNG ---
APP_FONT = ("Arial", 13)
APP_FONT_LARGE = ("Arial", 17, "bold")
BG_COLOR = "#EEEEEE"
WINDOW_BG = "#54C5E8"


# ========= VIẾT  DƯỚI DẠNG CLASS FRAME =========
class ReaderManagementView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.create_widgets()
        self.load_all_readers()

    # ==== CÁC HÀM CHECK CÁC ENTRY =====
    def only_letters(self, entry_widget):
        text = entry_widget.get()
        filtered = ''.join(ch for ch in text if ch.isalpha() or ch.isspace())
        if text != filtered:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filtered)

    def only_numbers(self, entry_widget):
        text = entry_widget.get()
        filtered = ''.join(ch for ch in text if ch.isdigit())
        if text != filtered:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filtered)


    def create_widgets(self):
            # === Frame chính chứa toàn bộ nội dung ===
            main_frame = tk.Frame(self, bg=BG_COLOR, bd=2)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            
            # Pack các nút bấm xuống DƯỚI CÙNG (BOTTOM) trước tiên
            frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
            frame_buttons.pack(fill="x", padx=10, pady=5, side="bottom")

            self.btn_add = macButton(
                frame_buttons, text="THÊM", font=APP_FONT_LARGE,
                bg="#4CAF50", fg="white",
                command=self.on_add_reader_click,
                borderwidth=4, relief="raised", activebackground="#4CAF50",
            )
            self.btn_add.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            self.btn_update = macButton(
                frame_buttons, text="SỬA", font=APP_FONT_LARGE,
                bg="#F44336", fg="white",
                command=self.on_update_reader_click,
                borderwidth=4, relief="raised", activebackground="#F44336",
            )
            self.btn_update.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            self.btn_remove = macButton(
                frame_buttons, text="XOÁ", font=APP_FONT_LARGE,
                bg="#2196F3", fg="white",
                command=self.on_delete_reader_click,
                borderwidth=4, relief="raised", activebackground="#2196F3",
            )
            self.btn_remove.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            self.btn_load = macButton(
                frame_buttons, text="LÀM MỚI", font=APP_FONT_LARGE,
                bg="#FF9800", fg="white",
                command=self.clear_form_and_reload,
                borderwidth=4, relief="raised",activebackground="#FF9800",
            )
            self.btn_load.pack(side="left", padx=10, pady=10, fill="x", expand=True)

            # Pack khung Search lên TRÊN CÙNG (TOP)
            frame_search = tk.LabelFrame(main_frame, text="TÌM THEO TÊN HOẶC SĐT", font=APP_FONT_LARGE)
            frame_search.pack(fill="x", padx=10, pady=10, side="top")

            lbl_search = tk.LabelFrame(frame_search, text="Nhập Tên/SĐT", font=APP_FONT_LARGE)
            lbl_search.pack(side="left", padx=(0, 5))
            self.entry_reader_name_phone_search = tk.Entry(frame_search, width=20)
            self.entry_reader_name_phone_search.pack(side="left", fill="x", expand=True, padx=5)
            self.btn_search = macButton(
                frame_search, text="Tìm kiếm", command=self.on_find_reader_click,
                font=APP_FONT, borderwidth=4, relief="raised", bg = "green", fg="white",
            )
            self.btn_search.pack(side= "left", padx=10)

            # Pack khung Details lên TRÊN (nằm dưới Search)
            frame_details = tk.LabelFrame(main_frame, text="CHI TIẾT ĐỘC GIẢ", font=APP_FONT_LARGE)
            frame_details.pack(fill="x", padx=10, pady=5, side="top")

            # Code grid bên trong frame_details
            frame_details.columnconfigure(1, weight=1)
            frame_details.columnconfigure(3, weight=1)

            #Label id
            lbl_reader_id = tk.Label(frame_details, text="ID:", font=APP_FONT)
            lbl_reader_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.entry_reader_id = tk.Entry(frame_details, state='readonly')
            self.entry_reader_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            #Label Tên
            lbl_full_name = tk.Label(frame_details, text="Tên" ,font=APP_FONT)
            lbl_full_name.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.entry_full_name = tk.Entry(frame_details)
            self.entry_full_name.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            self.entry_full_name.bind("<KeyRelease>", lambda e: self.only_letters(self.entry_full_name))

            #Label SĐT
            lbl_phone = tk.Label(frame_details, text="SĐT", font=APP_FONT)
            lbl_phone.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.entry_phone = tk.Entry(frame_details)
            self.entry_phone.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.entry_phone.bind("<KeyRelease>", lambda e: self.only_numbers(self.entry_phone))

            #Label Address
            lbl_address = tk.Label(frame_details, text="Địa chỉ", font=APP_FONT)
            lbl_address.grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.entry_address = tk.Entry(frame_details)
            self.entry_address.grid(row=1, column=3, padx=5, pady=5, sticky="ew")


            # Pack Bảng vào cuối cùng.
            # Nó sẽ tự động lấp đầy không gian còn lại ở giữa.
            frame_tree = tk.Frame(main_frame)
            frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

            # (Code Treeview bên trong frame_tree giữ nguyên)
            scrollbar = ttk.Scrollbar(frame_tree, orient= "vertical")
            columns = ("ReaderID", "FullName", "Phone", "Address")
            self.tree_readers = ttk.Treeview(
                frame_tree, columns=columns, show="headings",
                yscrollcommand=scrollbar.set
            )
            self.tree_readers.heading("ReaderID", text="ID")
            self.tree_readers.heading("FullName", text="Tên")
            self.tree_readers.heading("Phone", text="SĐT")
            self.tree_readers.heading("Address", text="Địa chỉ")
            self.tree_readers.column("ReaderID", width=100, anchor="center")
            self.tree_readers.column("FullName", width=250)
            self.tree_readers.column("Phone", width=150)
            self.tree_readers.column("Address", width=250)
            scrollbar.config(command=self.tree_readers.yview)
            scrollbar.pack(side="right", fill= "y")
            self.tree_readers.pack(side="left", fill="both", expand=True)
            self.tree_readers.bind("<<TreeviewSelect>>", self.on_tree_select)



    # ========== CÁC HÀM TẠO COMMAND CHO CÁC NÚT BẤM ================
    def set_entry_reader_id_state(self, state):
        self.entry_reader_id.config(state=state)

    def clear_and_set_reader_id(self, reader_id_value):
        self.set_entry_reader_id_state('normal')
        self.entry_reader_id.delete(0, tk.END)
        self.entry_reader_id.insert(0, reader_id_value)
        self.set_entry_reader_id_state('readonly')

    def clear_form(self):
        self.set_entry_reader_id_state('normal')
        self.entry_reader_id.delete(0, tk.END)
        self.set_entry_reader_id_state('readonly')
        self.entry_full_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_reader_name_phone_search.delete(0, tk.END)
        if self.tree_readers.selection():
            try:
                self.tree_readers.selection_remove(self.tree_readers.selection()[0])
            except IndexError:
                pass
        print("Form refreshed. All fields cleared.")

    def on_tree_select(self, event):
        try:
            selected_item = self.tree_readers.selection()[0]
            values = self.tree_readers.item(selected_item, 'values')
            self.clear_form()
            self.clear_and_set_reader_id(values[0])
            self.entry_full_name.insert(0, values[1])
            self.entry_phone.insert(0, values[2] if values[2] else "")
            self.entry_address.insert(0, values[3] if values[3] else "")
        except IndexError:
            pass

    def clear_form_and_reload(self):
        print("Refreshing form and data...")
        self.clear_form()
        self.load_all_readers()

    # Hàm gọi Controller
    def load_all_readers(self, reader_list=None):
        #
        # Xóa Treeview và tải dữ liệu mới vào.
        # Nếu 'reader_list' được cung cấp (từ tìm kiếm), tải list đó.
        # Nếu không, gọi CSDL để lấy tất cả.
        #
        for item in self.tree_readers.get_children():
            self.tree_readers.delete(item)

        if reader_list is None:
            # Nếu không phải tìm kiếm, lấy tất cả
            rows = get_all_readers()
        else:
            # Nếu là tìm kiếm, dùng list đã cho
            rows = reader_list

        if rows:
            for row in rows:
                self.tree_readers.insert("", tk.END, values=row)

    def on_add_reader_click(self):
        full_name = self.entry_full_name.get()
        phone = self.entry_phone.get()
        address = self.entry_address.get()
        if not full_name:
            messagebox.showerror("Lỗi", "Phải có tên", parent=self)
            return
        success = add_reader(full_name, phone, address)
        if success:
            messagebox.showinfo("Thành công", "Thêm Người đọc thành công", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi CSDL", "Không Add được người đọc", parent=self)

    def on_update_reader_click(self):
        reader_id = self.entry_reader_id.get()
        full_name = self.entry_full_name.get()
        phone = self.entry_phone.get()
        address = self.entry_address.get()
        if not reader_id:
            messagebox.showerror("Lỗi", "Chọn ID", parent=self)
            return
        success = update_reader(reader_id, full_name, phone, address)
        if success:
            messagebox.showinfo("Thành Công", "Update thành công", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi CSDL", "Không thể update ", parent=self)

    def on_delete_reader_click(self):
        reader_id = self.entry_reader_id.get()
        if not reader_id:
            messagebox.showerror("Lỗi", "Chọn 1 độc giả để xoá", parent=self)
            return
        if not messagebox.askyesno("", f"Bạn có muốn xoá : {reader_id}?", parent=self):
            return
        success = delete_reader(reader_id)
        if success:
            messagebox.showinfo("Thành Công", "Xoá người đọc", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Database Error", "Không xoá được độc giả, phải xoá độc giả ở Phiếu mượn", parent=self
                                 )

    def on_find_reader_click(self):
        search_term = self.entry_reader_name_phone_search.get().strip()
        if not search_term:
            messagebox.showerror("Error", "Nhập tên hoặc SĐT để tìm", parent=self)
            return

        # 1. Gọi Controller, 'results' SẼ LÀ MỘT LIST
        results = find_reader(search_term)

        # 2. Xử lý kết quả
        if results is None:
            messagebox.showerror("Database Error", "Không thể tìm ", parent=self)
        elif not results:  # (not results) == (results == [])
            messagebox.showinfo("Not found", "Không có độc giả nào trùng", parent=self)
            self.load_all_readers(reader_list=[])  # Tải bảng trống
        else:
            # 3. Tải kết quả tìm kiếm vào bảng
            self.load_all_readers(reader_list = results)


