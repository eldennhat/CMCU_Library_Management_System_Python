import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk
from tkmacosx import Button as macButton
from GUI.define import PATH_IMAGE
from controller.login_controller.auth_controller import check_login
class LoginView(tk.Frame):

    #Frame chứa giao diện Đăng nhập với các tùy chỉnh về style.

    def _setup_background(self):
        image_path = os.path.join(PATH_IMAGE, "backgroundLogin.png")
        img = Image.open(image_path)
        img = img.resize((1000,800), Image.Resampling.LANCZOS)
        #Image.Resampling.LANCZOS:Giúp thay đổi kích thước ảnh mà vẫn giữu được đỗ sắc nét

        #lưu tham chiếu
        self.bg_img = ImageTk.PhotoImage(img)

        #Tạo label chứa ảnh
        bg_label = tk.Label(self, image=self.bg_img)
        bg_label.place(x = 0, y = 0,relwidth=1, relheight=1)

    def __init__(self, parent, on_login_callback):
        #
        super().__init__(parent)
        #lệnh này gọi đến tk.Frame(Cha) viêc của lớp cha này là tạo ra 1 frame trống và gắn nó vào parent(Mảnh đất để xây frame)
        self.pack(fill="both", expand=True)

        #Lưu lại hàm
        self.on_login_callback = on_login_callback

        #Tạo nền bằng hàm:
        self._setup_background()

        # Tạo "Box" và căn giữa
        # dùng LabelFrame để lấy cái viền
        login_frame = ttk.LabelFrame(
            self,
            text=""  # Bỏ title ở đây
        )
        login_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 4. Sắp xếp các widget bên trong "Box" (dùng grid)

        # --- HÀNG 0: TITLE (DÙNG tk.Label) ---
        #
        title_label = tk.Label(
            login_frame,
            text="ĐĂNG NHẬP",
            font=("Arial", 18, "bold"),
            foreground="black"
        )
        # Đặt title này ở hàng đầu tiên, căn giữa (columnspan=2)
        title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 20))

        # --- HÀNG 1: Tên đăng nhập ---
        #tk.Label
        user_label = tk.Label(
            login_frame,
            text="Tên tài khoản: ",
            font=("Arial", 13, "bold")  # Đặt font trực tiếp
        )
        user_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.user_entry = ttk.Entry(login_frame, width=20)
        self.user_entry.grid(row=1, column=1, padx=10, pady=5)

        # --- HÀNG 2: Mật khẩu (DÙNG tk.Label) ---
        # tk.Label
        pass_label = tk.Label(
            login_frame,
            text="Mật khẩu:",
            font=("Arial", 13, "bold")  # Đặt font trực tiếp
        )
        pass_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.pass_entry = ttk.Entry(login_frame, show="*", width=20)
        self.pass_entry.grid(row=2, column=1, padx=10, pady=5)


        # --- HÀNG 3: Các nút bấm ---
        #1 frame chưa các nút bấm
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # 5. 2 nút bấmButton
        self.login_button = macButton(
            button_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#25A18E",
            fg="white",
            width=85,
            borderwidth=4,
            cursor="hand2",
            relief='raised',
            bordercolor="black",
            activebackground="green",
            command=self._on_login_click, #nút bấm sẽ chạy hàm _on_login
        )
        self.login_button.pack(anchor= "center", padx=10)


    def _on_login_click(self):
        username = self.user_entry.get() #lấy dữ liệu từ các ô nhập vào
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showwarning(message="Thiếu thông tin , Vui lòng nhập đủ thông tin") #Báo lỗi bằg 1 tin nhắn
            return

        role = check_login(username, password)
        #Gọi hàm check: Hàm nhận 2 tham số để check trong csdl
        #Hàm check_login ở controller sẽ check xem có chuẩn thông tin không

        if role: #nếu chả về chuẩn check login sẽ true, và trả về role cho Main
            self.on_login_callback(role)
        else:
            messagebox.showwarning(message="Đăng nhập thất bại! sai tên sai mk")



