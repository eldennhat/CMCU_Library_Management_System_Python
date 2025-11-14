import tkinter as tk

from tkinter import messagebox

from GUI.Menu.LOGIN.MenuLogin import LoginView
from GUI.Menu.ADMIN.AdminMenu import AdminMenu
from GUI.Menu.LIBRARIAN.LibrarianMenu import LibrarianMenu

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__() #là mảnh đất chính để xây dựng ra các frame login, admin...
        self.title("Hệ thống quản lý thư viện")
        self.geometry("800x500")
        self.resizable(width=False, height=False)

        self.current_frame = None #Frame đang được hiển thị

        self.show_login_view()

    def show_login_view(self):
        #Huỷ frame cũ nếu có
        if self.current_frame:
            self.current_frame.destroy()


        #Giải thích: hàm on_login_succes sẽ được gọi cho hàm callback, và sẽ trả về role ở login
        self.current_frame = LoginView(self, on_login_callback= self.on_login_success)

        #Cập nhật lại cửa sổ
        self.title("Ứng dụng Quản lý thư viện ")
        self.geometry("600x400")
        self.resizable(False, False)

    def on_login_success(self, role):
        if role == "Admin":
            self.show_admin_menu() #Hàm hiển thị admin ở dưới
        elif role == "Librarian":
            self.show_librarian_view() #Hàm hiển thị Thủ thư
        else:
            messagebox.showwarning("Lỗi vai trò không xác định")

    def show_admin_menu(self): #Hiển thị frame Admin
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = AdminMenu(self)

        self.geometry("1000x800")
        self.title("Admin")
        self.resizable(False, False)

    def show_librarian_view(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LibrarianMenu(self)

        self.geometry("1000x800")
        self.title("Librarian")
        self.resizable(False, False)


if __name__ == "__main__": #Điểm khởi chạy
    app = MainApplication()
    app.mainloop()

