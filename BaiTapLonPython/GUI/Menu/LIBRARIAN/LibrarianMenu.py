import os
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from GUI.Font.font import FONT_PIXELS
from tkmacosx import Button as macButton

from GUI.Menu.VIEW.BookMenu import BookManaFrame
from GUI.define import PATH_IMAGE


class LibrarianMenu(tk.Frame):

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
    """
    Frame chứa giao diện Menu của Thủ thư (Librarian).
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)

        self._setup_background()

        self._setup_menu_bar()

        self.content_frame = tk.Frame(self, bg = "white")
        self.content_frame.pack(fill="both", expand=True, padx=50, pady=50)

        self.current_view = None
        self.show_welcome_view()

    def _setup_menu_bar(self):
        """Tạo Menubar BÊN TRONG Frame này."""

        menu_frame = ttk.Frame(self)
        menu_frame.pack(fill="x", side="top", padx=0, pady=0)

        # --- Menu 1: Quản lý Sách/ Đầu sách ---
        book_menubutton = ttk.Menubutton(menu_frame, text=" Book Manager ")
        book_menubutton.pack(side='left', padx=5)

        # Định nghĩa 1 menu cho MenuButton
        book_menu = tk.Menu(book_menubutton, tearoff=0)
        book_menubutton.config(menu=book_menu)

        # cho các label thả xuống vào cái menu đó
        book_menu.add_command(label="Book Title Manager", command=self.show_book_manager_view)
        book_menu.add_command(label="Book Copy Manager")


        # --- Button 2: Quản lý Mượn/Trả ---
        loan_button = macButton(menu_frame, text=" Loan Manager ")
        loan_button.pack(side='left', padx=30)

        #--- Button 3: Quản Lý Độc giả ---
        user_button = macButton(menu_frame, text="Reader Manager", padx=5)
        user_button.pack(side='left', padx=30)

        # --- Button 4: Đăng xuất ---
        logout_button = macButton(menu_frame, text="Log Out", padx=5,command=self.logout)
        logout_button.pack(side='left', padx=30)



    def _clear_content_frame(self):
        """Hàm hỗ trợ: Xóa mọi thứ đang có trong content_frame."""
        if self.current_view:
            self.current_view.destroy()
        self.current_view = None

    # --- CÁC HÀM DEMO ---
    def show_welcome_view(self):
        self._clear_content_frame()
        self.current_view = ttk.Label(
            self.content_frame,
            text="Chào mừng Thủ thư!",
            font=(FONT_PIXELS, 20, "bold")
        )
        self.current_view.pack(pady=50, padx=50)

    def show_book_manager_view(self):
        self._clear_content_frame()
        self.current_view = BookManaFrame(self.content_frame)
        self.current_view.pack(fill="both", expand=True, padx=10, pady=10)




    def logout(self):
        """Gọi hàm show_login_view của MainApplication."""
        self.parent.show_login_view()