import tkinter as tk
from tkinter import ttk, messagebox
import pymssql
from pathlib import Path
import pyodbc

# --- CÀI ĐẶT CHUNG ---
APP_FONT = ("Press Start 2P", 10, "bold")
APP_FONT_LARGE = ("Press Start 2P", 12, "bold")
BG_COLOR = "#EEEEEE"  # Màu nền cho form
WINDOW_BG = "#54C5E8"  # Màu nền trời xanh

# --- KẾT NỐI DATABASE  --- thay đổi nếu cần
SQL_SERVER_CONFIG = {
    'server': 'Q407IQ\\SQLEXPRESS',
    'database': 'LibraryDB',
    # 'username': 'sa', # Đã bị xóa
    # 'password': 'hoang2006@' # Đã bị xóa
}


def get_connection():
    try:

        conn = pymssql.connect(
            server=SQL_SERVER_CONFIG['server'],
            database=SQL_SERVER_CONFIG['database']
        )
        return conn
    except pymssql.Error as e:
        messagebox.showerror("Conection error", f"Cannot connect to SQL server:\n{e}")
        return None


# --- HÀM HỖ TRỢ XỬ LÝ ENTRY ID ---

def set_entry_reader_id_state(state):
    """Đặt trạng thái của entry_reader_id (normal, readonly, disabled)"""
    entry_reader_id.config(state=state)


def clear_and_set_reader_id(reader_id_value):
    """Xóa, chèn giá trị ID và khóa lại entry_reader_id"""
    set_entry_reader_id_state('normal')
    entry_reader_id.delete(0, tk.END)
    entry_reader_id.insert(0, reader_id_value)
    set_entry_reader_id_state('readonly')


# --- CÁC HÀM XỬ LÝ SỰ KIỆN (DATABASE) ---

def load_all_readers():
    """Tải tất cả độc giả lên Treeview."""
    # Xóa dữ liệu cũ
    for item in tree_readers.get_children():
        tree_readers.delete(item)

    try:
        conn = get_connection()
        if not conn: return

        cursor = conn.cursor()
        sql = "SELECT ReaderId, FullName, Phone, Address FROM Reader"
        cursor.execute(sql)

        rows = cursor.fetchall()
        for row in rows:
            tree_readers.insert("", tk.END, values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load Readers list:\n{e}")


def add_reader():
    # Lấy dữ liệu từ các ô entry trong form "Details"
    full_name = entry_full_name.get()
    phone = entry_phone.get()
    address = entry_address.get()

    if not full_name:
        messagebox.showerror("Error", "Full Name is required!")
        return

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()

        sql = """INSERT INTO Reader (FullName, Phone, Address)
                 VALUES (%s, %s, %s)"""

        cursor.execute(sql, (full_name, phone, address))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Succes", "Reader added successfully!")

        clear_form_and_reload()  # Gọi hàm mới để xóa form và tải lại bảng

    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_reader():
    # Lấy dữ liệu từ các ô entry trong form "Details"
    reader_id = entry_reader_id.get()
    full_name = entry_full_name.get()
    phone = entry_phone.get()
    address = entry_address.get()

    if not reader_id:
        messagebox.showerror("Error", "To update, choose a Reader ID!")
        return

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        sql = """UPDATE Reader
                 SET FullName=%s,
                     Phone=%s,
                     Address=%s
                 WHERE ReaderID = %s"""
        # Sử dụng các widget mới
        cursor.execute(sql, (full_name, phone, address, reader_id))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Reader updated successfully!")

        clear_form_and_reload()  # Gọi hàm mới để xóa form và tải lại bảng

    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_reader():
    # Lấy ID từ ô "Reader ID" trong form "Details"
    reader_id = entry_reader_id.get()

    if not reader_id:
        messagebox.showerror("Error", "To delete, choose a Reader ID!")
        return

    if not messagebox.askyesno("Confirmation", f"Do you want to delete Reader ID: {reader_id}?"):
        return

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        sql = "DELETE FROM Reader WHERE ReaderID=%s"
        # Sử dụng widget mới
        cursor.execute(sql, (reader_id,))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Reader deleted successfully!")

        clear_form_and_reload()  # Gọi hàm mới để xóa form và tải lại bảng

    except Exception as e:
        messagebox.showerror("Error", str(e))


def find_reader():
    """Tìm độc giả bằng FullName/Phone từ ô TÌM KIẾM và điền vào form."""
    # Lấy dữ liệu từ ô TÌM KIẾM (Search)
    search_term = entry_reader_name_phone_search.get().strip()

    if not search_term:
        messagebox.showerror("Error", "Insert FullName or Phone to begin searching.")
        return

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()

        # Cải tiến SQL để tìm kiếm theo cả FullName hoặc Phone
        sql = """
              SELECT TOP 1 ReaderID, FullName, Phone, Address
              FROM Reader
              WHERE FullName LIKE %s
                 OR Phone LIKE %s
              """
        # Thêm '%' để tìm kiếm tương đối
        search_pattern = f'%{search_term}%'
        cursor.execute(sql, (search_pattern, search_pattern))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            # Xóa form cũ và điền thông tin vào entry_reader_id
            clear_form()
            clear_and_set_reader_id(row[0])

            # Điền thông tin vào các Entry khác
            entry_full_name.insert(0, row[1])
            entry_phone.insert(0, row[2] if row[2] else "")
            entry_address.insert(0, row[3] if row[3] else "")

            messagebox.showinfo("Success", f"Reader ID: {row[0]} found")
        else:
            messagebox.showinfo("Not found", "FullName or Phone not found.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def clear_form():
    """Xóa trắng các ô nhập liệu trong form "Details"."""
    set_entry_reader_id_state('normal')  # Phải mở khóa mới xóa được
    entry_reader_id.delete(0, tk.END)
    set_entry_reader_id_state('readonly')  # Khóa lại

    entry_full_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_address.delete(0, tk.END)
    entry_reader_name_phone_search.delete(0, tk.END)  # Xóa ô tìm kiếm

    # Bỏ chọn trong treeview
    if tree_readers.selection():
        tree_readers.selection_remove(tree_readers.selection()[0])
    print("Form refreshed. All fields cleared.")


def on_tree_select(event):
    """Điền dữ liệu vào form "Details" khi nhấp vào bảng."""
    try:
        selected_item = tree_readers.selection()[0]
        values = tree_readers.item(selected_item, 'values')

        # Xóa form cũ và điền ID vào entry_reader_id (chỉ có thể làm khi mở khóa)
        clear_form()
        clear_and_set_reader_id(values[0])

        # Điền dữ liệu mới vào các Entry khác
        entry_full_name.insert(0, values[1])
        entry_phone.insert(0, values[2] if values[2] else "")
        entry_address.insert(0, values[3] if values[3] else "")

    except IndexError:
        pass


# 🆕 HÀM MỚI KẾT HỢP CẢ CLEAR VÀ RELOAD
def clear_form_and_reload():
    """Xóa form và tải lại dữ liệu từ database."""
    print("Refreshing form and data...")
    clear_form()  # Xóa các ô nhập liệu
    load_all_readers()  # Tải lại bảng


# --- TẠO GIAO DIỆN ---

window = tk.Tk()
window.title("Reader Management Menu")
window.geometry("800x650")
window.configure(bg=WINDOW_BG)
window.resizable(False, False)

# --- Style cho widget ---
style = ttk.Style()
style.configure("TLabel", font=APP_FONT, background=BG_COLOR)
style.configure("TButton", font=APP_FONT)
style.configure("TEntry")
style.configure("TCombobox", font=APP_FONT)
style.configure("TTreeview.Heading", font=APP_FONT_LARGE)
style.configure("TTreeview", font=APP_FONT, rowheight=25)
style.configure("TLabelFrame", font=APP_FONT_LARGE, background=BG_COLOR)
style.configure("TLabelFrame.Label",
                font=APP_FONT_LARGE,
                background=BG_COLOR,
                foreground="#000000") # Thêm foreground để đảm bảo màu chữ tiêu đề

style.configure("TLabelFrame", background=BG_COLOR)
# --- Tabs  ---
tab_control = ttk.Notebook(window)
tab_reader = ttk.Frame(tab_control, padding=10)  # Tab chính
tab_control.add(tab_reader, text='Reader Manager')
tab_control.pack(expand=1, fill="both")

# === Frame chính chứa toàn bộ nội dung ===
main_frame = tk.Frame(tab_reader, bg=BG_COLOR, bd=2, relief=tk.RIDGE)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# --- 1. Khung Search Reader ---
frame_search = ttk.LabelFrame(main_frame, text="Search Reader", padding=(10, 5))
frame_search.pack(fill="x", padx=10, pady=10)

lbl_search = ttk.Label(frame_search, text="Enter FullName/Phone:")
lbl_search.pack(side=tk.LEFT, padx=(0, 5))

entry_reader_name_phone_search = ttk.Entry(frame_search, width=20)
entry_reader_name_phone_search.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

btn_search = ttk.Button(frame_search, text="Find", command=find_reader)
btn_search.pack(side=tk.LEFT, padx=(10, 0))
# --- 2. Khung Reader Details ---
frame_details = ttk.LabelFrame(main_frame, text="Reader Details", padding=10)
frame_details.pack(fill="x", padx=10, pady=5)

frame_details.columnconfigure(1, weight=1)
frame_details.columnconfigure(3, weight=1)

# Hàng 1: Reader ID & Full Name
lbl_reader_id = ttk.Label(frame_details, text="Reader ID:")
lbl_reader_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_reader_id = ttk.Entry(frame_details, state='readonly')  # Đặt state='readonly'
entry_reader_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

lbl_full_name = ttk.Label(frame_details, text="Full Name:")
lbl_full_name.grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_full_name = ttk.Entry(frame_details)
entry_full_name.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Hàng 2: Phone & Address
lbl_phone = ttk.Label(frame_details, text="Phone:")
lbl_phone.grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_phone = ttk.Entry(frame_details)
entry_phone.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

lbl_address = ttk.Label(frame_details, text="Address:")
lbl_address.grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_address = ttk.Entry(frame_details)
entry_address.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

# --- 3. Bảng danh sách (Treeview) ---
frame_tree = tk.Frame(main_frame)
frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL)
columns = ("ReaderID", "FullName", "Phone", "Address")
tree_readers = ttk.Treeview(
    frame_tree,
    columns=columns,
    show="headings",
    yscrollcommand=scrollbar.set
)

# Đặt tiêu đề cột
tree_readers.heading("ReaderID", text="Reader ID")
tree_readers.heading("FullName", text="Full Name")
tree_readers.heading("Phone", text="Phone")
tree_readers.heading("Address", text="Address")

# Căn chỉnh độ rộng cột
tree_readers.column("ReaderID", width=100, anchor="center")
tree_readers.column("FullName", width=250)
tree_readers.column("Phone", width=150)
tree_readers.column("Address", width=250)

scrollbar.config(command=tree_readers.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree_readers.pack(side=tk.LEFT, fill="both", expand=True)

# Gán sự kiện khi nhấp vào bảng
tree_readers.bind("<<TreeviewSelect>>", on_tree_select)

# --- 4. Khung nút bấm  ---
frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
frame_buttons.pack(fill="x", padx=10, pady=5)

# Gắn các hàm CẬP NHẬT vào các nút
btn_add = tk.Button(
    frame_buttons, text="ADD", font=APP_FONT_LARGE,
    bg="#4CAF50", fg="white", width=6, command=add_reader
)
btn_add.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_update = tk.Button(
    frame_buttons, text="UPDATE", font=APP_FONT_LARGE,
    bg="#F44336", fg="white", width=6, command=update_reader
)
btn_update.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_remove = tk.Button(
    frame_buttons, text="REMOVE", font=APP_FONT_LARGE,
    bg="#2196F3", fg="white", width=6, command=delete_reader
)
btn_remove.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_load = tk.Button(
    frame_buttons, text="REFRESH", font=APP_FONT_LARGE,
    bg="#FF9800", fg="white", width=6, command=clear_form_and_reload
)
btn_load.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

# --- Tải dữ liệu ban đầu ---
load_all_readers()

# --- Chạy cửa sổ ---
window.mainloop()