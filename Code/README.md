**SOURCE CODE**
---
HƯỚNG DẪN KẾT NỐI DB CHO WINDOWS
* B1: Mở "SQL Server 2022 Configuration Manager" → Chọn "SQL Server Network Configuration"
* B2: Chọn "Protocols for [INSTANCE]" → "Enable" hai dòng "TCP/IP" và "Named Pipes"
* B3: Click chuột phải chọn "Properties" của "TCP/IP" → Chọn tab "IP Address"
* B4: Tìm tag "IPAll" → Tag "TCP Dynamic Ports" không set giá trị, tag "TCP Port" set giá trị 1433
