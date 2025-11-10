import tkinter as tk
from tkinter import ttk

from tkmacosx import Button as macButton
from GUI.Font.font import FONT_PIXELS

from controller.admin_controller.staff_controller import register_new_user


class RegisterView(tk.Frame):

    """
    Đây là 1 frame (Trang ở trong AdminMenu nếu bạn nhấn chọn thêm khoản ở admin menu)
    """
    def __init__(self, parent):
        super().__init__(parent) #để khởi tạo cửa sổ TopLevel


        #----Giao diện đăng ký

        main_frame = tk.Frame(self, width=300, height=300)
        main_frame.place(relx = 0.5, rely = 0.5, anchor = "center")

        #--Hàng 0:
        title_label = tk.Label(
            main_frame,
            text = "Create Account",
            font = (FONT_PIXELS, 15, "bold"),
            fg = "#FFFFA9",
            bg =  "#FF9240",
            padx = 20,
            pady = 10

        )
        title_label.grid(row =0 , column = 0, columnspan = 2, pady=(0,20))

        #--Hàng 1: Tên đăng nhập
        user_label = tk.Label(main_frame, text = "Username: ", font = (FONT_PIXELS, 12))
        user_label.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = 'w')
        self.user_entry = ttk.Entry(main_frame, width = 30)
        self.user_entry.grid(row = 1, column = 1, padx = 5, pady = 5)

        #--Hàng 2: Mật khẩu
        pass_label = tk.Label(main_frame, text="Password: ", font=(FONT_PIXELS, 12))
        pass_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.pass_entry = ttk.Entry(main_frame, width=30, show="*")
        self.pass_entry.grid(row=2, column=1, padx=0, pady=5)

        #--Hàng 3: Nhập lại mật khẩu:
        repass_label = tk.Label(main_frame, text="Re-Password: ", font=(FONT_PIXELS, 9))
        repass_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.repass_entry = ttk.Entry(main_frame, width=30, show="*")
        self.repass_entry.grid(row=3, column=1, padx=10, pady=5)

        #--Hàng 4: Vai trò
        role_label = tk.Label(main_frame, text="Role: ", font=(FONT_PIXELS, 9))
        role_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(  #1 box có lựa chọn
            main_frame,
            textvariable = self.role_var,
            values = ["Admin", "Librarian"],
            state = "readonly",
            width = 25
        )
        self.role_combobox.grid(row=4, column=1, padx=15, pady=5, sticky='w')
        self.role_combobox.current(1)

        #--Hàng 5: Nút bấm
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row = 5, column = 0, columnspan = 2, pady = 20)

        self.submit_button = macButton(
            button_frame,
            text = "Register",
            font = (FONT_PIXELS, 10, "bold"),
            bg = "#C20000",
            fg = "white",
            width = 120,
            cursor = "hand2", relief = "raised",
            bordercolor="black",
            activebackground="#E55B40",
            borderwidth=4,
            command = self._on_submit

        )
        self.submit_button.pack(padx=10)


    #______Hàm để xử lý sự kiện đăng ký
    def _on_submit(self):
        """
        Được gọi khi nhấn nút 'Đăng Ký'.
        Lấy dữ liệu, kiểm tra, và gọi controller.
        """

        #1. Lấy dự liệu từ các ô nhập
        username = self.user_entry.get()
        password = self.pass_entry.get()
        re_password = self.repass_entry.get()
        role = self.role_var.get()

        #2. Kiểm tra phía giao diện
        #Kiểm tra xem có bỏ ô trống không
        if not username or not password or not re_password or not role:
            print("Thiếu thông tin, vui lòng nhập đủ ")
            return
        #Kiểm tra xêm mật khẩu nhập lại có khớp không
        if password != re_password:
            print("Mật khẩu nhập lại không khớp")
            return

        #3. Gọi controller để xử lý sự kiện
        status = register_new_user(username, password, role)

        #4. Xử lý kết quả từ controller
        if status == "SUCCESS":
            print("Đã tạo thành công")
        elif status == "USERNAME_EXISTS":
            print("Lỗi trùng lặp tên đăng nhập, vui lòng nhập lại")
        elif status == "DB_ERROR":
            print("Lỗi CSDL!!")



