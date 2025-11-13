import tkinter as tk
from tkinter import ttk, messagebox

# Import the font constant - adjust the path based on your project structure
try:
    from GUI.Font.font import FONT_PIXELS
except ImportError:
    # Fallback if import fails
    FONT_PIXELS = "Courier"

# (Bỏ comment các dòng controller này khi bạn đã viết chúng)
# from controller.view_controller.Staff_controller import get_all_staff_details, update_staff, delete_staff

class StaffManaFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pixel_font = (FONT_PIXELS, 10)
        self.pixel_font_bold = (FONT_PIXELS, 11, 'bold')


        # --- Biến lưu trữ (lấy từ 2 bảng Staff và Account) [cite: 489, 493] ---
        self.entry_vars = {
            "staff_id": tk.StringVar(),
            "full_name": tk.StringVar(),
            "birth_date": tk.StringVar(),
            "gender": tk.StringVar(),
            "address": tk.StringVar(),
            "phone": tk.StringVar(),
            "username": tk.StringVar(),
            "position": tk.StringVar(),
        }

        #Tạo giao diện
        self.create_widgets()
        self.load_staff_data() # Tải dữ liệu mẫu

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding = "10")
        main_frame.pack(fill = "both", expand = True)

        #Frame chứa 2 form (Staff và Account)
        form_container = ttk.Frame(main_frame)
        form_container.pack(fill = "x")

        form_container.columnconfigure(0, weight = 2) # Form Staff chiếm 2/3
        form_container.columnconfigure(1, weight = 1) # Form Account chiếm 1/3

        # 1. KHU VỰC THÔNG TIN NHÂN VIÊN (TỪ BẢNG STAFF)
        staff_form = tk.LabelFrame(form_container, text = "Staff Details", font = self.pixel_font)
        staff_form.grid(row = 0, column = 0, sticky = "nsew", padx = (0, 5))

        # Hàng 0: Staff ID (Read only)
        tk.Label(staff_form, text = "Staff ID:", font = self.pixel_font).grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_staff_id = ttk.Entry(staff_form, textvariable = self.entry_vars["staff_id"], font = self.pixel_font, state = "readonly")
        self.entry_staff_id.grid(row = 0, column = 1, sticky = "we", padx = 5, pady = 5)

        # Hàng 1: Full Name
        tk.Label(staff_form, text = "Full Name:", font = self.pixel_font).grid(row = 1, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_full_name = ttk.Entry(staff_form, textvariable = self.entry_vars["full_name"], font = self.pixel_font)
        self.entry_full_name.grid(row = 1, column = 1, sticky = "we", padx = 5, pady = 5)

        # Hàng 2: Birth Date
        tk.Label(staff_form, text = "Birth Date:", font = self.pixel_font).grid(row = 2, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_birth_date = ttk.Entry(staff_form, textvariable = self.entry_vars["birth_date"], font = self.pixel_font)
        self.entry_birth_date.grid(row = 2, column = 1, sticky = "we", padx = 5, pady = 5)

        # Hàng 3: Gender
        tk.Label(staff_form, text = "Gender:", font = self.pixel_font).grid(row = 3, column = 0, sticky = "w", padx = 5, pady = 5)
        self.combo_gender = ttk.Combobox(staff_form, textvariable = self.entry_vars["gender"],
                                         values = ["Male", "Female", "Other"], state = "readonly", font = self.pixel_font)
        self.combo_gender.grid(row = 3, column = 1, sticky = "we", padx = 5, pady = 5)
        # Fixed: Use winfo_toplevel() to get the root window safely
        try:
            self.winfo_toplevel().option_add(f'*TCombobox*Listbox.font', self.pixel_font)
        except:
            pass  # If it fails, just skip the font configuration


        # Hàng 4: Address
        tk.Label(staff_form, text = "Address:", font = self.pixel_font).grid(row = 4, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_address = ttk.Entry(staff_form, textvariable = self.entry_vars["address"], font = self.pixel_font)
        self.entry_address.grid(row = 4, column = 1, sticky = "we", padx = 5, pady = 5)

        # Hàng 5: Phone
        tk.Label(staff_form, text = "Phone:", font = self.pixel_font).grid(row = 5, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_phone = ttk.Entry(staff_form, textvariable = self.entry_vars["phone"], font = self.pixel_font)
        self.entry_phone.grid(row = 5, column = 1, sticky = "we", padx = 5, pady = 5)

        #2. KHU VỰC TÀI KHOẢN (TỪ BẢNG ACCOUNT)
        account_form = tk.LabelFrame(form_container, text = "Account", font = self.pixel_font)
        account_form.grid(row = 0, column = 1, sticky = "nsew", rowspan = 2) # Kéo dài 2 hàng

        # Hàng 0: Username (Readonly)
        tk.Label(account_form, text = "Username:", font = self.pixel_font).grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_username = ttk.Entry(account_form, textvariable = self.entry_vars["username"], font = self.pixel_font, state = "readonly")
        self.entry_username.grid(row = 0, column = 1, sticky = "w", padx = 5, pady = 5)

        # Hàng 1: Position (Vai trò)
        tk.Label(account_form, text = "Position:", font = self.pixel_font).grid(row = 1, column = 0, sticky = "w", padx = 5, pady = 5)
        self.combo_position = ttk.Combobox(account_form, textvariable = self.entry_vars["position"],
                                           values = ["Librarian", "Admin"], state = "readonly", font = self.pixel_font)
        self.combo_position.grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)


        # 3. KHU VỰC CHỨC NĂNG (BUTTONS)
        # (Không có nút "ADD" vì đã có RegisterView)
        button_frame = ttk.Frame(main_frame, padding = "5")
        button_frame.pack(fill = "x", pady = 10)

        tk.Button(button_frame, text = "Update", command = self.update_staff, font = self.pixel_font).pack(side = "left", fill = "x", expand = True, padx = 5)
        tk.Button(button_frame, text = "Remove", command = self.remove_staff, font = self.pixel_font).pack(side = "left", fill = "x", expand = True, padx = 5)
        tk.Button(button_frame, text = "Refresh", command = self.clear_form, font = self.pixel_font).pack(side = "left", fill = "x", expand = True, padx = 5)


        # 4. KHU VỰC HIỂN THỊ (BẢNG DỮ LIỆU)
        display_frame = ttk.Frame(main_frame, padding = (0, 10, 0, 0))
        display_frame.pack(fill = "both", expand = True)

        columns = ("staff_id", "full_name", "position", "phone", "username")

        # 1. Tạo thanh cuộn DỌC (chưa có command)
        scrollbar_y = ttk.Scrollbar(display_frame, orient = "vertical")

        # 2. Tạo thanh cuộn NGANG (chưa có command)
        scrollbar_x = ttk.Scrollbar(display_frame, orient = "horizontal")

        # 3. TẠO BẢNG (self.tree) và gán scrollbar vào nó
        self.tree = ttk.Treeview(display_frame, columns = columns, show = "headings",
                                 yscrollcommand = scrollbar_y.set,
                                 xscrollcommand = scrollbar_x.set)

        # 4. GÁN NGƯỢC LẠI: Gán command (từ self.tree) cho scrollbar
        scrollbar_y.config(command = self.tree.yview)
        scrollbar_x.config(command = self.tree.xview)

        # Đặt tiêu đề
        self.tree.heading("staff_id", text = "Staff ID")
        self.tree.heading("full_name", text = "Full Name")
        self.tree.heading("position", text = "Position")
        self.tree.heading("phone", text = "Phone")
        self.tree.heading("username", text = "Username")

        # Đặt độ rộng
        self.tree.column("staff_id", width = 80, anchor = "center")
        self.tree.column("full_name", width = 250)
        self.tree.column("position", width = 120)
        self.tree.column("phone", width = 150)
        self.tree.column("username", width = 150)

        # Pack
        scrollbar_y.pack(side = "right", fill = "y")
        scrollbar_x.pack(side = "bottom", fill = "x")
        self.tree.pack(side = "left", fill = "both", expand = True)

        # Gán sự kiện
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    #=Các hàm xử lý sự kiện

    def load_staff_data(self):
        """Tải dữ liệu nhân viên (JOIN từ 2 bảng) vào Treeview."""
        # (Code logic gọi controller của bạn ở đây)
        # staff_list = get_all_staff_details()

        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Tải dữ liệu mẫu để test
        sample_staff = [
            # (StaffID, FullName, BirthDate, Gender, Address, Phone, Username, Position)
            ("NV001", "Nguyễn Thanh An", "2006-08-15", "Male", "My Dinh", "0909123456", "admin", "Admin"),
            ("NV002", "Dinh Nguyen Hoang", "2006-07-23", "Male", "Cau Giay", "0987654321", "thuthu01", "Librarian")
        ]

        # Chỉ hiển thị các cột cần thiết trong Treeview
        for staff in sample_staff:
            tree_data = (staff[0], staff[1], staff[7], staff[5], staff[6])
            self.tree.insert("", "end", values = tree_data, iid = staff[0]) # Dùng StaffID làm iid

    def on_item_select(self, event):
        """Sự kiện khi nhấp vào một hàng trong Treeview."""
        selected_item_id = self.tree.focus() # Lấy iid (StaffID)
        if not selected_item_id:
            return

        # (Bạn sẽ cần một hàm controller để lấy chi tiết 1 nhân viên)
        # details = get_staff_by_id(selected_item_id)

        # Giả lập lấy dữ liệu chi tiết dựa trên sample_staff
        details = {}
        if selected_item_id == "NV001":
            details = {"id": "NV001", "name": "Nguyễn Thanh An", "dob": "2006-08-15", "gender": "Male", "addr": "My Dinh", "phone": "0909123456", "user": "admin", "pos": "Admin"}
        elif selected_item_id == "NV002":
            details = {"id": "NV002", "name": "Dinh Nguyen Hoang", "dob": "2006-07-23", "gender": "Male", "addr": "Cau Giay", "phone": "0987654321", "user": "thuthu01", "pos": "Librarian"}
        else:
            return

        # Mở khóa các ô
        self.entry_staff_id.config(state = "normal")
        self.entry_username.config(state = "normal")

        # Điền giá trị vào form
        self.entry_vars["staff_id"].set(details["id"])
        self.entry_vars["full_name"].set(details["name"])
        self.entry_vars["birth_date"].set(details["dob"])
        self.entry_vars["gender"].set(details["gender"])
        self.entry_vars["address"].set(details["addr"])
        self.entry_vars["phone"].set(details["phone"])
        self.entry_vars["username"].set(details["user"])
        self.entry_vars["position"].set(details["pos"])

        # Khóa lại các ô ID và Username
        self.entry_staff_id.config(state = "readonly")
        self.entry_username.config(state = "readonly")

    def clear_form(self):
        """Xóa trắng tất cả các trường trong form và tải lại bảng."""
        self.entry_staff_id.config(state = "normal")
        self.entry_username.config(state = "normal")

        for var in self.entry_vars.values():
            var.set("")

        self.combo_gender.set("") # Xóa combobox
        self.combo_position.set("") # Xóa combobox

        self.tree.selection_remove(self.tree.selection()) # Bỏ chọn trên bảng
        self.load_staff_data() # Tải lại dữ liệu

    def update_staff(self):
        """Xử lý logic cập nhật nhân viên."""
        staff_id = self.entry_vars["staff_id"].get()
        if not staff_id:
            messagebox.showwarning("No Selection", "Please select a staff member from the list.", parent = self)
            return

        # (Code logic cập nhật CSDL của bạn ở đây)
        # (Bạn sẽ cần update 2 bảng: Staff và Account)

        messagebox.showinfo("Success", f"Information for {staff_id} has been updated successfully.", parent = self)
        self.clear_form() # Tải lại bảng

    def remove_staff(self):
        """Xử lý logic xóa nhân viên."""
        staff_id = self.entry_vars["staff_id"].get()
        if not staff_id:
            messagebox.showwarning("No Selection", "Please select a staff member to delete.", parent = self)
            return

        if messagebox.askyesno("Delete Confirmation", f"Are you sure you want to DELETE staff member {staff_id}?\nThis action will also remove the linked account.", parent = self):
            # (Code logic xóa khỏi CSDL của bạn ở đây)
            # (Bạn sẽ cần xóa ở 2 bảng, hoặc dùng 'ON DELETE CASCADE' trong SQL)

            messagebox.showinfo("Success", f"Staff member {staff_id} has been deleted successfully.", parent = self)
            self.clear_form() # Tải lại bảng
