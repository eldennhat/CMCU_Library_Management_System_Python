import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

from GUI.Menu.VIEW.BookMenu import BookManaFrame
from GUI.Menu.ADMIN.RegisterView import RegisterView
from GUI.Menu.VIEW.LoanMenu import LoanMenu
from GUI.define import PATH_IMAGE
from tkmacosx import Button as macButton


class AdminMenu(tk.Frame):
    def _setup_background(self):
        # (Lưu ý: Đổi tên file ảnh nếu bạn muốn dùng ảnh khác)
        image_path = os.path.join(PATH_IMAGE, "backgroundLogin.png")

        # (Lưu ý: Đổi kích thước cho khớp với cửa sổ Admin)
        window_width = 800
        window_height = 600

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
        self.content_frame.pack(fill="both",expand=True,  padx=50, pady=50)

        self.current_view = None

        self.show_welcome_view()

    def _setup_menu_bar(self):
        #Tạo 1 frame để chưa các nút menu
        menu_frame = tk.Frame(self)
        menu_frame.pack(fill="x", side='top', padx=0, pady=0)



        #--Button 1: Quản lý độc giả: để hiện ra phần quản lý độc giả
        #Mbutton
        user_button = macButton(menu_frame, text = "Reader Manager", command = self.show_reader_manager, padx= 5)
        user_button.pack(side='left', padx=(5))


        #--Menu 1: Quản lý nhân viên
        #Sẽ tạo ra menubutton khi ấn sẽ hiện ra các chức năng
        staff_menubutton = ttk.Menubutton(menu_frame, text = 'Staff')
        staff_menubutton.pack(side='left', padx=5)

        #Định nghĩa 1 menu cho MenuButton
        staff_menu = tk.Menu(staff_menubutton, tearoff=0)
        staff_menubutton.config(menu=staff_menu)
        #cho các label thả xuống vào cái menu đó
        staff_menu.add_command(label = "Register for staff", command= self.show_create_staff_account_view)
        staff_menu.add_command(label = "Staff Manager")

        #--Menu 2: Quản lý sách (gồm đầu sách và bản sao)
        book_menubutton = ttk.Menubutton(menu_frame, text = "Book Manager ")
        book_menubutton.pack(side='left', padx=5)

        # Định nghĩa 1 menu cho MenuButton
        book_menu = tk.Menu(book_menubutton, tearoff=0)
        book_menubutton.config(menu=book_menu)

        # cho các label thả xuống vào cái menu đó
        book_menu.add_command(label="Book Title Manager", command= self.show_book_manager_view)
        book_menu.add_command(label="Book Copy Manager")

        loan_button = macButton(menu_frame, text="Loan Manager", padx=5, command=self.show_loan_manager_view)
        loan_button.pack(side='left', padx=5)

        #Button hiện 1 frame thống kê:
        statistic_button = macButton(menu_frame, text = "Statistic")
        statistic_button.pack(side='left', padx=5)

        #--Menu 3: Hệ thống
        system_menubutton = ttk.Menubutton(menu_frame, text="System")
        system_menubutton.pack(side="left", padx=(5))

        system_menu = tk.Menu(system_menubutton, tearoff=0)
        system_menubutton.config(menu=system_menu)

        system_menu.add_command(label="Log Out", command=self.logout)

    def _clear_content_frame(self):
        """Hàm hỗ trợ: Xóa mọi thứ đang có trong content_frame."""
        if self.current_view:
            self.current_view.destroy()
        self.current_view = None

    #-----------CÁC HÀM CỦA CÁC MENUBUTTON-----------
    def show_welcome_view(self):
        self._clear_content_frame()
        self.current_view = ttk.Label(
            self.content_frame,
            text = "Chào mừng ADMIN",
            font = ("Press Start 2P", 20, "bold"),
        )
        self.current_view.pack(padx=50, pady=50)

    #CÁC HÀM LIÊN QUAN ĐẾN QUẢN LÝ ĐỘC GIẢ
    def show_reader_manager(self):
        self._clear_content_frame()
        self.current_view = ttk.Label(
            self.content_frame,
            text = "Readers Manager Demo",
            font = ("Press Start 2P", 20, "bold"),
        )
        self.current_view.pack(padx=50, pady=50)


    #CÁC HÀM TRONG QUẢN LÝ NHÂN VIÊN
    def show_create_staff_account_view(self):
        """
        Tải RegisterView (Frame) vào content_frame.
        """
        self._clear_content_frame()

        self.current_view = RegisterView(self.content_frame)

        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    #SỰ KIỆN CHO NÚT BOOK MANAGER
    def show_book_manager_view(self):
        self._clear_content_frame()
        self.current_view = BookManaFrame(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    def show_loan_manager_view(self):
        self._clear_content_frame()
        self.current_view = LoanMenu(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)

    #HÀM ĐỂ DISPLAY STAFF MANAGEMENT
    def show_staff_mana_view(self):
        """
        update StaffMana vao content_frame
        """
        self._clear_content_frame()  #delete frame cũ
        self.current_view = StaffManaFrame(self.content_frame) #create a new frame
        self.current_view.pack(fill = 'both', expand = True, padx = 10, pady = 10)
        
    #HÀM ĐỂ ĐĂNG XUẤT
    def logout(self):
        self.parent.show_login_view()


