import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

from GUI.Menu.ADMIN.StaffMenu import StaffManagementView
from GUI.Menu.VIEW.BookCopyMenu import BookCopyMenuView
from GUI.Menu.VIEW.BookMenu import BookManaFrame
from GUI.Menu.ADMIN.RegisterView import RegisterView
from GUI.Menu.VIEW.LoanMenu import LoanMenu
from GUI.Menu.VIEW.Reader_MeoMeo import ReaderManagementView
from GUI.define import PATH_IMAGE
from tkmacosx import Button as macButton


class AdminMenu(tk.Frame):
    def _setup_background(self):
        # (Lưu ý: Đổi tên file ảnh nếu bạn muốn dùng ảnh khác)
        image_path = os.path.join(PATH_IMAGE, "backgroundLogin.png")

        window_width = 1000
        window_height = 800

        try:
            img = Image.open(image_path)

            # Resize ảnh
            try:
                img = img.resize((window_width, window_height), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((window_width, window_height), Image.LANCZOS)

            # Phải lưu tham chiếu
            self.bg_img = ImageTk.PhotoImage(img)

            # Tạo Label chứa ảnh
            bg_label = tk.Label(self, image=self.bg_img)

            # Đặt label này LÊN TRƯỚC (để nó nằm sau cùng)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        except Exception as e:
            print(f"Lỗi khi tải background AdminMenu: {e}")


    def __init__(self, parent):
        super().__init__(parent) #parent là mainApplication
        self.pack(fill="both", expand=True)  # Lấp đầy cửa sổ
        self.parent = parent

        #Tạo background
        self._setup_background()
        #--1. Tạo Menu Bar
        self._setup_menu_bar()

        #--2. Tạo 1 frame nội dung
        self.content_frame = tk.Frame(self, bg = "white")
        self.content_frame.pack(fill="both",expand=True,  padx=10, pady=10)

        self.current_view = None

        self.show_welcome_view()

    def _setup_menu_bar(self):
        #Tạo 1 frame để chưa các nút menu
        menu_frame = tk.Frame(self)
        menu_frame.pack(fill="x", side='top', padx=0, pady=0)



        #--Button 1: Quản lý độc giả: để hiện ra phần quản lý độc giả
        #Mbutton
        user_button = macButton(menu_frame, text = "Quản lý độc giả", command = self.show_reader_manager, padx= 5)
        user_button.pack(side='left', padx=(5))


        #--Button 2: Quản lý nhân viên
        staff_button = macButton(menu_frame, text= "Quản lý nhân viên", command = self.show_staff_menu_view, padx= 5)
        staff_button.pack(side='left', padx=(5))


        #--Menu 2: Quản lý sách (gồm đầu sách và bản sao)
        book_menubutton = ttk.Menubutton(menu_frame, text = "Quản lý sách")
        book_menubutton.pack(side='left', padx=5)

        # Định nghĩa 1 menu cho MenuButton
        book_menu = tk.Menu(book_menubutton, tearoff=0)
        book_menubutton.config(menu=book_menu)

        # cho các label thả xuống vào cái menu đó
        book_menu.add_command(label="Quản lý đầu sách", command= self.show_book_manager_view)
        book_menu.add_command(label="Quản lý bản sao sách", command= self.show_copy_manager_view)

        #Button mượn trả
        loan_button = macButton(menu_frame, text="Quản lý mượn trả", padx=5, command=self.show_loan_manager_view)
        loan_button.pack(side='left', padx=5)


        # --- Button 4: Đăng xuất ---
        logout_button = macButton(menu_frame, text="Log Out", padx=5, command=self.logout)
        logout_button.pack(side='left', padx=30)



    def _clear_content_frame(self):
        #Hàm hỗ trợ: Xóa mọi thứ đang có trong content_frame.
        if self.current_view:
            self.current_view.destroy()
        self.current_view = None

    #-----------CÁC HÀM CỦA CÁC MENUBUTTON-----------
    def show_welcome_view(self):
        self._clear_content_frame()
        self.current_view = ttk.Label(
            self.content_frame,
            text = " Welcome\n  Admin",
            font = ("Press Start 2P", 60, "bold"),
        )
        self.current_view.pack(padx=100, pady=300)

    #CÁC HÀM LIÊN QUAN ĐẾN QUẢN LÝ ĐỘC GIẢ
    def show_reader_manager(self):
        self._clear_content_frame()
        self.current_view = ReaderManagementView(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)


    #CÁC VIEW TRONG QUẢN LÝ NHÂN VIÊN
    def show_create_staff_account_view(self):
        #Tải RegisterView (Frame) vào content_frame.
        self._clear_content_frame()
        self.current_view = RegisterView(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    def show_staff_menu_view(self):
        self._clear_content_frame()
        self.current_view = StaffManagementView(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    #SỰ KIỆN CHO NÚT BOOK MANAGER
    def show_book_manager_view(self):
        self._clear_content_frame()
        self.current_view = BookManaFrame(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    def show_copy_manager_view(self):
        self._clear_content_frame()
        self.current_view = BookCopyMenuView(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)


    #SỰ KIỆN CHO LOAN MANAGER
    def show_loan_manager_view(self):
        self._clear_content_frame()
        self.current_view = LoanMenu(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)


    #HÀM ĐỂ ĐĂNG XUẤT
    def logout(self):
        self.parent.show_login_view()


