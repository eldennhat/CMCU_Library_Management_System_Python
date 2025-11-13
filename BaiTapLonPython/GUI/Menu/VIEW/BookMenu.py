import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from GUI.Font.font import FONT_PIXELS
from tkmacosx import Button as macButton

from controller.view_controller.Book_controller import get_all_books, add_book, update_book, delete_book, search_book


class BookManaFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pixel_font = (FONT_PIXELS, 10)
        self.pixel_font_bold = (FONT_PIXELS, 11, 'bold')

        # (Các biến vars)
        self.entry_vars = {
            "book_id": tk.StringVar(),
            "isbn": tk.StringVar(),
            'title': tk.StringVar(),
            'category_name': tk.StringVar(),
            'book_author': tk.StringVar(),
            'publish_year': tk.StringVar(),
        }
        self.search_var = tk.StringVar()

        self.create_widgets()
        self.load_sample_data()

    def create_widgets(self):
        main_frame = tk.Frame(self, padx = 10, pady = 10)
        main_frame.pack(fill = 'both', expand = True)

        # 1. Khung tìm kiếm
        search_frame = tk.LabelFrame(main_frame, text = 'Search Book', padx = 10, pady = 10, font = self.pixel_font)
        search_frame.pack(fill = 'x', pady = 5)

        tk.Label(search_frame, text = 'Enter text:', font = self.pixel_font).pack(side = 'left', padx = 5)
        tk.Entry(search_frame, textvariable = self.search_var, width = 40).pack(side = 'left', expand = True)
        tk.Button(search_frame, text = 'Search', command = self.search_book_in_data, font = self.pixel_font).pack(side = 'left', padx = 5)

        # 2. Khu vực nhập liệu (form)
        form_frame = tk.LabelFrame(main_frame, text = 'Book details', padx = 10, pady = 10, font = self.pixel_font)
        form_frame.pack(fill = 'x', pady = 5)

        form_frame.columnconfigure(1, weight = 1)
        form_frame.columnconfigure(3, weight = 1)
        # --------------------------------

        # --- HÀNG 0 ---
        tk.Label(form_frame, text = 'Book ID:', font = self.pixel_font).grid(row = 0, column = 0, sticky = 'w', padx = 5, pady = 5)

        self.entry_book_id = tk.Entry(form_frame, textvariable=self.entry_vars['book_id'], width = 25)
        self.entry_book_id.grid(row = 0, column = 1, sticky = 'we', padx = 5, pady = 5)


        tk.Label(form_frame, text = 'ISBN:', font = self.pixel_font).grid(row = 0, column = 2, sticky = 'w', padx = 5, pady = 5)
        self.entry_isbn = tk.Entry(form_frame, textvariable = self.entry_vars['isbn'], width = 25)
        self.entry_isbn.grid(row = 0, column = 3, sticky = 'we', padx = 5, pady = 5)

        # --- HÀNG 1 ---
        tk.Label(form_frame, text = "Title:", font = self.pixel_font).grid(row = 1, column = 0, sticky = "w", padx = 5, pady = 5)
        self.entry_title = tk.Entry(form_frame, textvariable = self.entry_vars["title"], width = 25)
        self.entry_title.grid(row = 1, column = 1, sticky = 'we', padx = 5, pady = 5)

        tk.Label(form_frame, text = "Author:", font = self.pixel_font).grid(row = 1, column = 2, sticky = "w", padx = 5, pady = 5)
        self.entry_author = tk.Entry(form_frame, textvariable = self.entry_vars["book_author"], width = 25,)
        self.entry_author.grid(row = 1, column = 3, sticky = 'we', padx = 5, pady = 5)

        # --- HÀNG 2 ---
        tk.Label(form_frame, text = "Category:", font = self.pixel_font).grid(row = 2, column = 0, sticky = "w", padx = 5, pady = 5)

        category_list = ["Textbook", "Reference Material", "Novel", "Comic", "Science"]
        self.combo_category = tk.OptionMenu(form_frame, self.entry_vars["category_name"], *category_list)
        self.combo_category.config(font = self.pixel_font, width = 23)  # Giảm width
        self.combo_category.grid(row = 2, column = 1, sticky = "we", padx = 5, pady = 5)  # Dùng sticky='we'

        try:
            self.master.option_add('*TCombobox*Listbox.font', self.pixel_font)
        except tk.TclError:
            pass

        tk.Label(form_frame, text = "Publisher Year:", font = self.pixel_font).grid(row = 2, column = 2, sticky = "w", padx = 5, pady = 5)
        self.entry_year = tk.Entry(form_frame, textvariable = self.entry_vars["publish_year"], width = 25)
        self.entry_year.grid(row = 2, column = 3, sticky = 'we', padx = 5, pady = 5)

        #**************************************************************************************************************
        # === CÁC BUTTON ===

        button_frame = tk.Frame(main_frame, pady = 5)
        button_frame.pack(fill = "x", pady = 10, side = "bottom")

        button_add = macButton(button_frame, text = "ADD", command = self.add_book_to_db, font = self.pixel_font, cursor = "hand2", relief = "raised", bg = "green", fg = "white", activebackground = "green", borderwidth = 4)
        button_add.pack(side = "left",fill = "x",expand = True,padx = 5)

        button_update = macButton(button_frame, text = "UPDATE", command = self.update_book_to_db, font = self.pixel_font,
                                  cursor = "hand2", relief = "raised", bg = "red", fg = "white", activebackground = "red", borderwidth=4)
        button_update.pack(side = "left", fill = "x", expand = True, padx = 5)

        button_remove = macButton(button_frame, text = "REMOVE", command = self.delete_book_from_db, font = self.pixel_font
                                  ,cursor = "hand2", relief = "raised", bg = "#2930d8", fg = "white", activebackground = "#2930d8", borderwidth = 4)
        button_remove.pack(side = "left", fill = "x", expand = True, padx = 5)

        button_load = macButton(button_frame, text = "REFRESH", command = self.clear_form, font = self.pixel_font,
                                cursor = "hand2", relief = "raised", bg = "#203020", fg = "white", activebackground = "#203020", borderwidth = 4)
        button_load.pack(side = "left", fill = "x", expand = True, padx = 5)

        # === 4. KHU VỰC HIỂN THỊ (BẢNG DỮ LIỆU) ===
        display_frame = tk.Frame(main_frame, padx = 10, pady = 10)
        display_frame.pack(fill = "both", expand = True)

        columns = ("book_id", "isbn", "title", "category_name", "book_author", "publish_year")

        scrollbar = ttk.Scrollbar(display_frame, orient = "vertical")

        self.tree = ttk.Treeview(display_frame, columns = columns, show = "headings",
                                 yscrollcommand=scrollbar.set)
        scrollbar.config(command = self.tree.yview)

        # (Tiêu đề và cột)
        self.tree.heading("book_id", text = "Book ID")
        self.tree.heading("isbn", text = "ISBN")
        self.tree.heading("title", text = "Title")
        self.tree.heading("category_name", text = "Category")
        self.tree.heading("book_author", text = "Author")
        self.tree.heading("publish_year", text = "Publish Year")
        self.tree.column("book_id", width = 100, anchor = "center")
        self.tree.column("isbn", width = 150)
        self.tree.column("title", width = 300)
        self.tree.column("category_name", width = 150)
        self.tree.column("book_author", width = 200)
        self.tree.column("publish_year", width = 100, anchor = "center")

        scrollbar.pack(side = "right", fill = "y")
        self.tree.pack(side = "left", fill = "both", expand = True)

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

    # (Tất cả các hàm xử lý sự kiện: load_sample_data,
    #       on_item_select, clear_form, add_book, KA
    #       update_book, delete_book, search_book
    def load_sample_data(self):
        sample_books = [
            ("1", "978-604-77-2007-8", "Lập trình Python", "Giáo trình", "Nguyễn Văn A", "2023"),
            ("2", "978-604-68-1614-2", "Cấu trúc dữ liệu & Giải thuật", "Tài liệu tham khảo", "Trần Thị B", "2022")
        ]
        for book in sample_books:
            self.tree.insert("", "end", values=book)

    def on_item_select(self, event):
        #Lấy thông tin về hàng bạn chọn
        selected_item = self.tree.focus()
        if not selected_item:
            return
        #Lấy toàn bộ dữ liệu vừa chọn đó
        values = self.tree.item(selected_item, "values")

        #Để set các ô theo cái mình vừa chọn
        self.entry_vars["book_id"].set(values[0])
        self.entry_vars["isbn"].set(values[1])
        self.entry_vars["title"].set(values[2])
        self.entry_vars["category_name"].set(values[3])
        self.entry_vars["book_author"].set(values[4])
        self.entry_vars["publish_year"].set(values[5])
        self.entry_book_id.config(state = "readonly") #Không cho sửa
        self.entry_isbn.config(state = "readonly") # không cho sửa

    def clear_form(self):
        # Xoá sạch trong ô nhập liệu
        for var in self.entry_vars.values():
            var.set("")

        # Mở khoá
        self.entry_book_id.config(state = "normal")
        self.entry_isbn.config(state = "normal")

        # Bỏ hàng được chọn nếu chọn
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

        #Làm mới toàn bộ bảng về trạng thái gốc
        self.load_books_to_treeview()

    def load_books_to_treeview(self, book_list=None):
        """
        Xóa Treeview và tải dữ liệu mới vào.
        Nếu booklist được cung cấp từ tìm kiếm, tải list đó.
        Nếu không, gọi CSDL để lấy tất cả.
        """
        #Xoa du lieu cu
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Lay du lieu
        if book_list is None:
            # Neu khong la ham tim kiem, lay tat ca
            book_list = get_all_books()

        # Them du lieu moi vao
        if book_list:
            for book in book_list:
                self.tree.insert("", "end", values = book)


    def add_book_to_db(self):
        # Lay du lieu
        book_id = self.entry_vars["book_id"].get()
        title = self.entry_vars["title"].get()
        isbn = self.entry_vars["isbn"].get()

        # Check
        if not isbn or not book_id or not isbn:
            messagebox.showwarning("Missing Infomation", "Book ID, ISBN và Title is required.")
            return

        #Tao tuple du lieu trung vs csdl
        new_book_data = (
            book_id,
            isbn,
            title,
            self.entry_vars["category_name"].get(),
            self.entry_vars["book_author"].get(),
            self.entry_vars["publish_year"].get()
        )
        #Goi controller để insert vào csdl
        success = add_book(new_book_data)
        if success:
            messagebox.showinfo("Success", f"Add '{title}' successful.")
            self.clear_form()
        else:
            messagebox.showinfo("Failed", f"Add '{title}' failed.")

    def update_book_to_db(self):
        #Kiem tra xem co chon hang nao khong
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Not pick Book", "Please select a book to update.")
            return
        #Lay du lieu tu form
        book_id = self.entry_vars["book_id"].get() #Khoa chinh
        updated_data = (
            self.entry_vars["isbn"].get(),
            self.entry_vars["title"].get(),
            self.entry_vars["category_name"].get(),
            self.entry_vars["book_author"].get(),
            self.entry_vars["publish_year"].get(),
            book_id
        )

        #Goi controller
        success = update_book(updated_data)
        if success:
            messagebox.showinfo("Success", "Update successfully.", parent = self)
            self.clear_form() #Tai lai bang
        else:
            messagebox.showinfo("Failed", "Update failed.",parent = self)


    def delete_book_from_db(self):
        #  Kiểm tra xem có chọn hàng nào không
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Not pick Book", "Please pick a book to delete.", parent = self)
            return

        #  Lấy BookID và Title (để xác nhận)
        book_id = self.entry_vars["book_id"].get()
        title = self.entry_vars["title"].get()

        #  Hỏi xác nhận
        if messagebox.askyesno("Delete", f"Do you want to delelte'{title}' (ID: {book_id})?", parent = self):
            #  Gọi controller
            success = delete_book(book_id)
            if success:
                messagebox.showinfo("Success", "Delete book", parent = self)
                self.clear_form()  # Xóa form ,tải lại bảng
            else:
                messagebox.showerror("Database ERROR", "Can not delete", parent = self)


    def search_book_in_data(self):
        keyword = self.search_var.get()
        if not keyword:
            messagebox.showwarning("Not enter", "Please enter BookTitle or BookAuthor to search.", parent = self)
            return

        #  Gọi controller
        results = search_book(keyword)

        if results is None:
            messagebox.showerror("Database Error", "Can not find", parent = self)
        elif not results:
            messagebox.showinfo("No result", "Can not find a book with keyword", parent = self)
            # Tải lại bảng trống
            self.load_books_to_treeview(book_list = [])
        else:
            #  Tải kết quả tìm kiếm vào bảng
            self.load_books_to_treeview(book_list = results)
