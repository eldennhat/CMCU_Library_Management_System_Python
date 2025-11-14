import tkinter as tk
from tkinter import ttk, messagebox
from GUI.Font.font import FONT_PIXELS
from controller.admin_controller.staff_controller import get_all_staff_details, get_staff_details_by_id, \
    update_staff_details, delete_staff_and_account, create_staff_and_account

from tkmacosx import Button as macButton
APP_FONT = (FONT_PIXELS, 10)
APP_FONT_LARGE = (FONT_PIXELS, 11, 'bold')
BG_COLOR = "#EEEEEE"


class StaffManagementView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)


        self.pixel_font = APP_FONT
        self.pixel_font_bold = APP_FONT_LARGE

        # --- Biến lưu trữ -
        self.entry_vars = {
            "staff_id": tk.StringVar(),
            "full_name": tk.StringVar(),
            "phone": tk.StringVar(),
            "default_start": tk.StringVar(),  # Sửa lại
            "default_end": tk.StringVar(),  # Sửa lại
            "username": tk.StringVar(),
            "password": tk.StringVar(),
            "re_password": tk.StringVar(),
            "position": tk.StringVar(),
        }

        self.create_widgets()
        self.load_staff_data()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Nút bấm (DƯỚI CÙNG) ---
        frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
        frame_buttons.pack(fill="x", pady=10, side="bottom")

        self.btn_add = macButton(
            frame_buttons, text="ADD", font=self.pixel_font_bold,
            bg="#4CAF50", fg="white",
            command=self.on_add_staff_and_account_click,
            borderwidth=4, relief="raised"
        )
        self.btn_add.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_update = macButton(
            frame_buttons, text="UPDATE", font=self.pixel_font_bold,
            bg="#FF9800", fg="white",
            command=self.on_update_staff_click,
            borderwidth=4, relief="raised"
        )
        self.btn_update.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_remove = macButton(
            frame_buttons, text="REMOVE", font=self.pixel_font_bold,
            bg="#F44336", fg="white",
            command=self.on_remove_staff_click,
            borderwidth=4, relief="raised"
        )
        self.btn_remove.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.btn_load = macButton(
            frame_buttons, text="REFRESH", font=self.pixel_font_bold,
            bg="#2196F3", fg="white",
            command=self.clear_form_and_reload,
            borderwidth=4, relief="raised"
        )
        self.btn_load.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # ---  2 KHUNG CẠNH NHAU ---
        form_container = tk.Frame(main_frame, bg=BG_COLOR)
        form_container.pack(fill="x", side="top", padx=10, pady=5)  # Pack lên trên

        form_container.columnconfigure(0, weight=2)  # Form Staff chiếm 2/3
        form_container.columnconfigure(1, weight=1)  # Form Account chiếm 1/3

        # 1. KHU VỰC THÔNG TIN NHÂN VIÊN (Bảng Staff)
        staff_form = tk.LabelFrame(form_container, text="Staff Details", font=self.pixel_font_bold, bg=BG_COLOR)
        staff_form.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        staff_form.columnconfigure(1, weight=1)  # Cho Entry co giãn

        # Hàng 0: Staff ID
        tk.Label(staff_form, text="Staff ID:", font=self.pixel_font, bg=BG_COLOR).grid(row=0, column=0, sticky="w",
                                                                                       padx=5, pady=2)
        self.entry_staff_id = tk.Entry(staff_form, textvariable=self.entry_vars["staff_id"],
                                       state="readonly")
        self.entry_staff_id.grid(row=0, column=1, sticky="we", padx=5, pady=2)

        # Hàng 1: Full Name
        tk.Label(staff_form, text="Full Name:", font=self.pixel_font, bg=BG_COLOR).grid(row=1, column=0, sticky="w",
                                                                                        padx=5, pady=2)
        self.entry_full_name = tk.Entry(staff_form, textvariable=self.entry_vars["full_name"])
        self.entry_full_name.grid(row=1, column=1, sticky="we", padx=5, pady=2)

        # Hàng 2: Phone
        tk.Label(staff_form, text="Phone:", font=self.pixel_font, bg=BG_COLOR).grid(row=2, column=0, sticky="w", padx=5,
                                                                                    pady=2)
        self.entry_phone = tk.Entry(staff_form, textvariable=self.entry_vars["phone"])
        self.entry_phone.grid(row=2, column=1, sticky="we", padx=5, pady=2)

        # Hàng 3: Default Start
        tk.Label(staff_form, text="Default Start:", font=self.pixel_font, bg=BG_COLOR).grid(row=3, column=0, sticky="w",
                                                                                            padx=5, pady=2)
        self.entry_default_start = tk.Entry(staff_form, textvariable=self.entry_vars["default_start"],
                                           )
        self.entry_default_start.grid(row=3, column=1, sticky="we", padx=5, pady=2)

        # Hàng 4: Default End
        tk.Label(staff_form, text="Default End:", font=self.pixel_font, bg=BG_COLOR).grid(row=4, column=0, sticky="w",
                                                                                          padx=5, pady=2)
        self.entry_default_end = tk.Entry(staff_form, textvariable=self.entry_vars["default_end"])
        self.entry_default_end.grid(row=4, column=1, sticky="we", padx=5, pady=2)

        # 2. KHU VỰC TÀI KHOẢN (Bảng Account)
        account_form = tk.LabelFrame(form_container, text="Account", font=self.pixel_font_bold, bg=BG_COLOR)
        # GHI CHÚ: 'rowspan=2' để nó cao bằng 'staff_form'
        account_form.grid(row=0, column=1, sticky="nsew", rowspan=5)
        account_form.columnconfigure(1, weight=1)

        # Hàng 0: Username
        tk.Label(account_form, text="Username:", font=self.pixel_font, bg=BG_COLOR).grid(row=0, column=0, sticky="w",
                                                                                         padx=5, pady=2)
        self.entry_username = tk.Entry(account_form, textvariable=self.entry_vars["username"])
        self.entry_username.grid(row=0, column=1, sticky="we", padx=5, pady=2)

        # Hàng 1: Position (Role)
        tk.Label(account_form, text="Position:", font=self.pixel_font, bg=BG_COLOR).grid(row=1, column=0, sticky="w",
                                                                                         padx=5, pady=2)
        self.combo_position = ttk.Combobox(account_form, textvariable=self.entry_vars["position"],
                                           values=["Librarian", "Admin"], state="readonly")
        self.combo_position.grid(row=1, column=1, sticky="we", padx=5, pady=2)
        self.combo_position.set("Librarian")  # Mặc định

        # Hàng 2: Password
        tk.Label(account_form, text="Password:", font=self.pixel_font, bg=BG_COLOR).grid(row=2, column=0, sticky="w",
                                                                                         padx=5, pady=2)
        self.entry_password = tk.Entry(account_form, textvariable=self.entry_vars["password"],
                                       )
        self.entry_password.grid(row=2, column=1, sticky="we", padx=5, pady=2)

        # Hàng 3: Re-Password (
        tk.Label(account_form, text="Re-Password:", font=self.pixel_font, bg=BG_COLOR).grid(row=3, column=0, sticky="w",
                                                                                            padx=5, pady=2)
        self.entry_re_password = tk.Entry(account_form, textvariable=self.entry_vars["re_password"],
                                         show="*")
        self.entry_re_password.grid(row=3, column=1, sticky="we", padx=5, pady=2)

        # 4. KHU VỰC HIỂN THỊ (BẢNG DỮ LIỆU)
        display_frame = tk.Frame(main_frame)
        display_frame.pack(fill="both", expand=True, padx=10, pady=10, side="top")

        #
        columns = ("staff_id", "full_name", "position", "phone", "username", "password")
        scrollbar_y = ttk.Scrollbar(display_frame, orient="vertical")
        scrollbar_x = ttk.Scrollbar(display_frame, orient="horizontal")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        self.tree.heading("staff_id", text="Staff ID")
        self.tree.heading("full_name", text="Full Name")
        self.tree.heading("position", text="Position")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("username", text="Username")
        self.tree.heading("password", text="Password")
        self.tree.column("staff_id", width=80, anchor="center")
        self.tree.column("full_name", width=250)
        self.tree.column("position", width=120)
        self.tree.column("phone", width=150)
        self.tree.column("username", width=150)
        self.tree.column("password", width=150)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)


    # =Các hàm xử lý sự kiện (ĐÃ KẾT NỐI CONTROLLER) =

    def load_staff_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        staff_list = get_all_staff_details()  # Gọi Controller
        if staff_list:
            for staff_row in staff_list:
                self.tree.insert("", "end", values=staff_row, iid=staff_row[0])

    def on_item_select(self, event):
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            return

        details = get_staff_details_by_id(selected_item_id)  # Gọi Controller
        if not details:
            messagebox.showerror("Lỗi", "Không thể lấy chi tiết nhân viên.", parent=self)
            return

        # Mở khóa các ô
        self.entry_staff_id.config(state="normal")
        self.entry_username.config(state="normal")
        self.entry_password.config(state="normal")

        self.clear_form(reload_data=False)

        # Điền giá trị vào form
        self.entry_vars["staff_id"].set(details.get("StaffId", ""))
        self.entry_vars["full_name"].set(details.get("FullName", ""))
        self.entry_vars["phone"].set(details.get("Phone", ""))
        start_time = details.get("DefaultStart", "")
        end_time = details.get("DefaultEnd", "")
        self.entry_vars["default_start"].set(str(start_time) if start_time else "")
        self.entry_vars["default_end"].set(str(end_time) if end_time else "")
        self.entry_vars["username"].set(details.get("Username", ""))
        self.entry_vars["position"].set(details.get("Role", ""))
        self.entry_vars["password"].set(details.get("PasswordHash", ""))

        #  Khóa các ô không được sửa khi UPDATE
        self.entry_staff_id.config(state="readonly")
        self.entry_username.config(state="readonly")
        # Khóa luôn 2 ô password (chỉ dùng khi ADD)
        self.entry_password.config(state="readonly")
        self.entry_re_password.config(state="disabled")

    def clear_form(self, reload_data=True):
        #Xóa trắng tất cả các trường trong form.
        self.entry_staff_id.config(state="normal")
        self.entry_username.config(state="normal")
        self.entry_password.config(state="normal")
        self.entry_re_password.config(state="normal")

        for var_name, var in self.entry_vars.items():
            var.set("")

        self.combo_position.set("Librarian")  # Đặt về mặc định

        self.entry_staff_id.config(state="readonly")  # Khóa lại

        self.tree.selection_remove(self.tree.selection())

        if reload_data:
            self.load_staff_data()

    def clear_form_and_reload(self):
        self.clear_form(reload_data=True)

    #  ADD
    def on_add_staff_and_account_click(self):
        #Gộp 2 việc: Thêm Staff và Thêm Account
        # 1. Lấy dữ liệu
        full_name = self.entry_vars["full_name"].get()
        phone = self.entry_vars["phone"].get()
        start_time = self.entry_vars["default_start"].get() or None
        end_time = self.entry_vars["default_end"].get() or None

        username = self.entry_vars["username"].get()
        password = self.entry_vars["password"].get()
        re_password = self.entry_vars["re_password"].get()
        role = self.entry_vars["position"].get()

        # 2. Kiểm tra
        if not full_name or not phone or not username or not password or not role:
            messagebox.showwarning("Thiếu thông tin", "Phải nhập: Full Name, Phone, Username, Password, và Position.",
                                   parent=self)
            return

        if password != re_password:
            messagebox.showerror("Lỗi Mật khẩu", "Mật khẩu nhập lại không khớp!", parent=self)
            return

        # 3. Kiểm tra xem có đang chọn hàng nào không (phải ở chế độ ADD)
        if self.entry_vars["staff_id"].get():
            messagebox.showwarning("Lỗi", "Đang chọn nhân viên. Vui lòng nhấn 'REFRESH' để thêm mới.", parent=self)
            return

        # 4. Gói dữ liệu và Gọi Controller
        staff_data = (full_name, phone, start_time, end_time)
        account_data = (username, password, role)  # (Gửi pass thuần)

        success, message = create_staff_and_account(staff_data, account_data)

        if success:
            messagebox.showinfo("Thành công", message, parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi CSDL", message, parent=self)  # Hiển thị lỗi

    #UPDATE
    def on_update_staff_click(self):
        staff_id = self.entry_vars["staff_id"].get()
        if not staff_id:
            messagebox.showwarning("No Selection", "Please select a staff member from the list.", parent=self)
            return

        full_name = self.entry_vars["full_name"].get()
        phone = self.entry_vars["phone"].get()
        start_time = self.entry_vars["default_start"].get() or None
        end_time = self.entry_vars["default_end"].get() or None
        role = self.entry_vars["position"].get()

        if not full_name or not role:
            messagebox.showwarning("Thiếu thông tin", "Full Name và Position là bắt buộc.", parent=self)
            return

        success = update_staff_details(staff_id, full_name, phone, start_time, end_time, role)

        if success:
            messagebox.showinfo("Success", f"Information for {staff_id} has been updated.", parent=self)
            self.clear_form_and_reload()
        else:
            messagebox.showerror("Lỗi CSDL", "Không thể cập nhật thông tin.", parent=self)

    #REMOVE
    def on_remove_staff_click(self):
        staff_id = self.entry_vars["staff_id"].get()
        if not staff_id:
            messagebox.showwarning("No Selection", "Please select a staff member to delete.", parent=self)
            return

        if messagebox.askyesno("Delete Confirmation",
                               f"Are you sure you want to DELETE staff member {staff_id}?\nThis action will also remove the linked account.",
                               parent=self):

            success = delete_staff_and_account(staff_id)

            if success:
                messagebox.showinfo("Success", f"Staff member {staff_id} has been deleted.", parent=self)
                self.clear_form_and_reload()
            else:
                messagebox.showerror("Lỗi CSDL",
                                     "Không thể xóa nhân viên.\n(Lưu ý: Không thể xóa nhân viên đang liên kết với Phiếu Mượn).",
                                     parent=self)