import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import pymssql

# --- CÀI ĐẶT CHUNG ---
APP_FONT = ("Press Start 2P", 10, "bold")
APP_FONT_LARGE = ("Press Start 2P", 12, "bold")
BG_COLOR = "#EEEEEE"  # Màu nền cho form
WINDOW_BG = "#54C5E8"  # Màu nền trời xanh

# --- KẾT NỐI DATABASE ---
SQL_SERVER_CONFIG = {
    'server': 'Q407IQ\\SQLEXPRESS',  # Thay đổi nếu cần
    'database': 'LibraryDB',
    # 'username': 'sa',
    # 'password': 'hoang2006@'
}


def get_connection():
    try:
        conn = pymssql.connect(
            server=SQL_SERVER_CONFIG['server'],
            database=SQL_SERVER_CONFIG['database']
        )
        return conn
    except pymssql.Error as e:
        messagebox.showerror("Connection Error", f"Cannot connect to SQL Server:\n{e}")
        return None


# --- CÁC HÀM XỬ LÝ SỰ KIỆN (DATABASE) ---

def fetch_book_ids():
    """Lấy danh sách BookId từ bảng Book để điền vào combobox."""
    try:
        conn = get_connection()
        if not conn: return []

        cursor = conn.cursor()
        cursor.execute("SELECT BookId FROM Book")  # Giả sử bạn có bảng 'Book'
        book_ids = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return book_ids
    except Exception as e:
        print(f"Error when collecting Book IDs: {e}")
        return []


def search_or_load_all_copies():
    """Tải tất cả bản sao sách lên Treeview."""
    # Xóa dữ liệu cũ
    for item in tree_copies.get_children():
        tree_copies.delete(item)

    try:
        conn = get_connection()
        if not conn: return

        cursor = conn.cursor()
        sql = "SELECT CopyId, BookId, PublisherName, Status, Barcode, BookMoney, StorageNote FROM BookCopy"
        cursor.execute(sql)

        rows = cursor.fetchall()
        for row in rows:
            tree_copies.insert("", tk.END, values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load Book Copy data:\n{e}")


def add_book_copy():
    # Lấy dữ liệu từ GUI
    book_id = combo_book_id.get()
    publisher = entry_publisher.get()
    status = combo_status.get()
    storage_note = entry_storage_note.get()
    barcode = entry_barcode.get()
    book_money_text = entry_price.get()

    # --- Kiểm tra dữ liệu (từ code gốc) ---
    if not book_id or not status:
        messagebox.showerror("Error", "Book ID and Status are required.")
        return
    if not book_money_text:
        messagebox.showerror("Error", "Price is required!")
        return
    try:
        book_money = float(book_money_text)
    except ValueError:
        messagebox.showerror("Error", "Price must be numbers!")
        return
    status_int = int(status)
    # --- Kết thúc kiểm tra ---

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()

        sql = """
              INSERT INTO BookCopy (BookId, PublisherName, [Status], StorageNote, Barcode, BookMoney)
              VALUES (%s, %s, %s, %s, %s, %s) \
              """
        cursor.execute(sql, (book_id, publisher, status_int, storage_note, barcode, book_money))
        conn.commit()

        messagebox.showinfo("Success", "Book copy added successfully!")
        cursor.close()
        conn.close()

        load_form()  # Xóa form
        search_or_load_all_copies()  # Tải lại bảng

    except Exception as e:
        messagebox.showerror("Error", f"Error when adding book:\n{e}")


def update_book_copy():
    # Lấy dữ liệu từ GUI
    copy_id = entry_copy_id.get()
    book_id = combo_book_id.get()
    publisher = entry_publisher.get()
    status = combo_status.get()
    storage_note = entry_storage_note.get()
    barcode = entry_barcode.get()
    book_money_text = entry_price.get()

    # --- Kiểm tra dữ liệu ---
    if not copy_id:
        messagebox.showerror("Error", "Need to chose one copy ID to update..")
        return
    if not book_id or not status or not book_money_text:
        messagebox.showerror("Error", "Book ID, Status, and Price are required!")
        return
    try:
        book_money = float(book_money_text)
        copy_id_int = int(copy_id)
        status_int = int(status)
    except ValueError:
        messagebox.showerror("Error", "Copy ID and Price must be numbers!")
        return
    # --- Kết thúc kiểm tra ---

    try:
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()

        sql = """
              UPDATE BookCopy
              SET BookId=%s, \
                  PublisherName=%s, [Status]=%s, StorageNote=%s, Barcode=%s, BookMoney=%s
              WHERE CopyId=%s \
              """
        cursor.execute(sql, (book_id, publisher, status_int, storage_note, barcode, book_money, copy_id_int))
        conn.commit()

        messagebox.showinfo("Success", "Book copy updated successfully!")
        cursor.close()
        conn.close()

        load_form()  # Xóa form
        search_or_load_all_copies()  # Tải lại bảng

    except Exception as e:
        messagebox.showerror("Error", f"Error when updating:\n{e}")


def delete_book_copy():
    copy_id_text = entry_copy_id.get()
    if not copy_id_text:
        messagebox.showerror("Error", "Chose a book copy to delete!")
        return
    try:
        copy_id = int(copy_id_text)
    except ValueError:
        messagebox.showerror("Error", "CopyId is invalid!")
        return

    if not messagebox.askyesno("Confirm", f"Do you want to delete book copy with Copy Id: {copy_id}?"):
        return

    try:
        conn = get_connection()
        if not conn: return

        cursor = conn.cursor()
        sql = "DELETE FROM BookCopy WHERE CopyId=%s"
        cursor.execute(sql, (copy_id,))
        conn.commit()

        messagebox.showinfo("Success", "Book copy deleted successfully!")
        cursor.close()
        conn.close()

        load_form()  # Xóa form
        search_or_load_all_copies()  # Tải lại bảng
    except Exception as e:
        messagebox.showerror("Error", str(e))


def load_form():
    """Xóa trắng các ô nhập liệu."""
    entry_copy_id.delete(0, tk.END)
    combo_book_id.set("")
    entry_publisher.delete(0, tk.END)
    combo_status.set("")
    entry_storage_note.delete(0, tk.END)
    entry_barcode.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_search.delete(0, tk.END)

    if tree_copies.selection():
        tree_copies.selection_remove(tree_copies.selection()[0])
    print("Form refreshed.")


def on_tree_select(event):
    """Điền dữ liệu vào form khi nhấp vào bảng."""
    try:
        selected_item = tree_copies.selection()[0]
        values = tree_copies.item(selected_item, 'values')

        load_form()  # Xóa form cũ

        # Điền dữ liệu mới
        entry_copy_id.insert(0, values[0])  # CopyId
        combo_book_id.set(str(values[1]))  # BookId
        entry_publisher.insert(0, values[2])  # PublisherName
        combo_status.set(str(values[3]))  # Status
        entry_barcode.insert(0, values[4])  # Barcode
        entry_price.insert(0, str(values[5]))  # BookMoney
        entry_storage_note.insert(0, values[6])  # StorageNote

    except IndexError:
        pass


# --- TẠO GIAO DIỆN ---

window = tk.Tk()
window.title("Book Copy Management Menu")
window.geometry("800x650")
window.configure(bg=WINDOW_BG)
window.resizable(False, False)

# --- Style cho widget ---
style = ttk.Style()
style.configure("TLabel", font=APP_FONT, background=BG_COLOR)
style.configure("TButton", font=APP_FONT)
style.configure("TEntry", font=APP_FONT)
style.configure("TCombobox", font=APP_FONT)
style.configure("TTreeview.Heading", font=APP_FONT_LARGE)
style.configure("TTreeview", font=APP_FONT, rowheight=25)
style.configure("TLabelFrame", font=APP_FONT_LARGE, background=BG_COLOR)
style.configure("TLabelFrame.Label", font=APP_FONT_LARGE, background=BG_COLOR)

# --- Tabs (Giống trong ảnh) ---
tab_control = ttk.Notebook(window)
# Bạn có thể tạo các tab khác ở đây
tab_book_copy = ttk.Frame(tab_control, padding=10)  # Tab chính
tab_control.add(tab_book_copy, text='Book Copy Manager')
tab_control.pack(expand=1, fill="both")

# === Frame chính chứa toàn bộ nội dung ===
main_frame = tk.Frame(tab_book_copy, bg=BG_COLOR, bd=2, relief=tk.RIDGE)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# --- 1. Khung Search ---
frame_search = ttk.LabelFrame(main_frame, text="Search Book Copy", padding=(10, 5))
frame_search.pack(fill="x", padx=10, pady=10)

lbl_search = ttk.Label(frame_search, text="Enter text:")
lbl_search.pack(side=tk.LEFT, padx=(0, 5))

entry_search = ttk.Entry(frame_search, font=APP_FONT, width=40)
entry_search.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

btn_search = ttk.Button(frame_search, text="Search", command=search_or_load_all_copies)
btn_search.pack(side=tk.LEFT, padx=(5, 0))

# --- 2. Khung Book Copy Details ---
frame_details = ttk.LabelFrame(main_frame, text="Book Copy Details", padding=10)
frame_details.pack(fill="x", padx=10, pady=5)

frame_details.columnconfigure(1, weight=1)
frame_details.columnconfigure(3, weight=1)

# Hàng 1: Copy ID & Book ID
lbl_copy_id = ttk.Label(frame_details, text="Copy ID:")
lbl_copy_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_copy_id = ttk.Entry(frame_details, font=APP_FONT)
entry_copy_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

lbl_book_id = ttk.Label(frame_details, text="Book ID:")
lbl_book_id.grid(row=0, column=2, padx=5, pady=5, sticky="w")
combo_book_id = ttk.Combobox(frame_details, font=APP_FONT, state="readonly")
combo_book_id.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Hàng 2: Publisher & Barcode
lbl_publisher = ttk.Label(frame_details, text="Publisher:")
lbl_publisher.grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_publisher = ttk.Entry(frame_details, font=APP_FONT)
entry_publisher.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

lbl_barcode = ttk.Label(frame_details, text="Barcode:")
lbl_barcode.grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_barcode = ttk.Entry(frame_details, font=APP_FONT)
entry_barcode.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

# Hàng 3: Price & Status
lbl_price = ttk.Label(frame_details, text="Price:")
lbl_price.grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_price = ttk.Entry(frame_details, font=APP_FONT)
entry_price.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

lbl_status = ttk.Label(frame_details, text="Status:")
lbl_status.grid(row=2, column=2, padx=5, pady=5, sticky="w")
status_values = ['-1', '0', '1', '2']
combo_status = ttk.Combobox(frame_details, values=status_values, font=APP_FONT, state="readonly")
combo_status.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

# Hàng 4: Storage Note
lbl_storage_note = ttk.Label(frame_details, text="Storage Note:")
lbl_storage_note.grid(row=3, column=0, padx=5, pady=5, sticky="w")
entry_storage_note = ttk.Entry(frame_details, font=APP_FONT)
entry_storage_note.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

# --- 3. Bảng danh sách (Treeview) ---
frame_tree = tk.Frame(main_frame)
frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL)
columns = ("CopyId", "BookId", "Publisher", "Status", "Barcode", "Price", "StorageNote")
tree_copies = ttk.Treeview(
    frame_tree,
    columns=columns,
    show="headings",
    yscrollcommand=scrollbar.set
)

# Đặt tiêu đề cột
tree_copies.heading("CopyId", text="Copy ID")
tree_copies.heading("BookId", text="Book ID")
tree_copies.heading("Publisher", text="Publisher")
tree_copies.heading("Status", text="Status")
tree_copies.heading("Barcode", text="Barcode")
tree_copies.heading("Price", text="Price")
tree_copies.heading("StorageNote", text="Storage Note")

# Căn chỉnh độ rộng cột
tree_copies.column("CopyId", width=60, anchor="center")
tree_copies.column("BookId", width=60, anchor="center")
tree_copies.column("Publisher", width=150)
tree_copies.column("Status", width=50, anchor="center")
tree_copies.column("Barcode", width=120)
tree_copies.column("Price", width=80, anchor="e")
tree_copies.column("StorageNote", width=150)

scrollbar.config(command=tree_copies.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree_copies.pack(side=tk.LEFT, fill="both", expand=True)

tree_copies.bind("<<TreeviewSelect>>", on_tree_select)

# --- 4. Khung nút bấm (Giống hệt ảnh) ---
frame_buttons = tk.Frame(main_frame, bg=BG_COLOR)
frame_buttons.pack(fill="x", padx=10, pady=5)

btn_add = tk.Button(
    frame_buttons, text="ADD", font=APP_FONT_LARGE,
    bg="#4CAF50", fg="white", width=6, command=add_book_copy
)
btn_add.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_update = tk.Button(
    frame_buttons, text="UPDATE", font=APP_FONT_LARGE,
    bg="#F44336", fg="white", width=6, command=update_book_copy
)
btn_update.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_remove = tk.Button(
    frame_buttons, text="REMOVE", font=APP_FONT_LARGE,
    bg="#2196F3", fg="white", width=6, command=delete_book_copy
)
btn_remove.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

btn_load = tk.Button(
    frame_buttons, text="LOAD FORM", font=APP_FONT_LARGE,
    bg="#FF9800", fg="white", width=6, command=load_form
)
btn_load.pack(side=tk.LEFT, padx=10, pady=10, fill="x", expand=True)

# --- Tải dữ liệu ban đầu ---
combo_book_id['values'] = fetch_book_ids()
search_or_load_all_copies()

# --- Chạy cửa sổ ---
window.mainloop()