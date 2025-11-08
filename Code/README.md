**SOURCE CODE**
---
HƯỚNG DẪN KẾT NỐI DB CHO WINDOWS
* B1: Mở "SQL Server 2022 Configuration Manager" → Chọn "SQL Server Network Configuration"
* B2: Chọn "Protocols for [INSTANCE]" → "Enable" hai dòng "TCP/IP" và "Named Pipes"
* B3: Click chuột phải chọn "Properties" của "TCP/IP" → Chọn tab "IP Address"
* B4: Tìm tag "IPAll" → Tag "TCP Dynamic Ports" không set giá trị, tag "TCP Port" set giá trị 1433
* B5: Mở project → Mở "database\\db_connector.py"
* B6: Tại biến `SQL_SERVER_CONFIG` đang mặc định sử dụng "SQL Authen" thay đổi các đối số tương ứng với máy
* B7 (Nếu muốn đổi sang "Windows Authen"): Tại biến `SQL_SERVER_CONFIG` comment các đối số, chỉ để lại `'server'` và `'database'` → thay đổi các giá trị tương ứng
* B8 (Nếu muốn đổi sang "Windows Authen"): Tại phương thức `get_db_connection()` comment các hàm trả về database kết nối, chỉ để lại `server=SQL_SERVER_CONFIG['server'],` và `database=SQL_SERVER_CONFIG['database']`
