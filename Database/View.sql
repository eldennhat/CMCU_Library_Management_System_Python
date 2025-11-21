--View

-- VIEW HỖ TRỢ CHO APP PYTHON --
-- View gộp 3 (Loan, Staff, Reader ) 
-- để tìm kiếm thông tin của những đối tượng liên quan Loan ID cụ thể
IF OBJECT_ID('v_LoanInfo', 'V') IS NOT NULL
DROP VIEW v_LoanInfo
GO

CREATE VIEW v_LoanInfo
AS
SELECT 
    l.LoanId, 
    l.LoanDate, 
    l.DueDate, 
    r.FullName AS ReaderName, 
    r.Phone    AS ReaderPhone, 
    s.FullName AS StaffName
FROM Loan AS l
JOIN Reader AS r ON l.ReaderId = r.ReaderId
JOIN Staff AS s ON l.StaffId = s.StaffId
GO

SELECT * FROM v_LoanInfo
WHERE LoanId = 4003
GO

-- View các thông tin sách mượn cho 1 LoanID cụ thể
IF OBJECT_ID('v_LoanBookDetails', 'V') IS NOT NULL
DROP VIEW v_LoanBookDetails
GO

CREATE VIEW v_LoanBookDetails
AS
SELECT 
    d.LoanId,
    d.CopyId, 
    b.Title AS BookTitle,
    d.ReturnedDate, 
    d.Deposit,
    d.Fine
FROM LoanDetail AS d
    JOIN BookCopy AS c ON d.CopyId = c.CopyId
    JOIN Book AS b ON c.BookId = b.BookId
GO

SELECT * FROM v_LoanBookDetails
WHERE LoanId = 4053
GO



--VIEW cho chi tiết tất cả thông tin phiếu mượn
IF OBJECT_ID('v_LoanDetails', 'V') IS NOT NULL
DROP VIEW v_LoanDetails
GO

CREATE VIEW v_LoanDetails
AS
SELECT 
    l.LoanId,
    d.CopyId,
    b.Title    AS BookTitle,
    d.ReturnedDate,
    s.FullName AS StaffName,
    r.FullName AS ReaderName,
    r.ReaderId,
    d.Fine,
    d.Deposit
FROM LoanDetail AS d
    JOIN Loan AS l ON d.LoanId = l.LoanId
    JOIN BookCopy AS c ON d.CopyId = c.CopyId
    JOIN Book AS b ON c.BookId = b.BookId
    JOIN Staff AS s ON l.StaffId = s.StaffId
    JOIN Reader AS r ON l.ReaderId = r.ReaderId
GO

SELECT * FROM v_LoanDetails
ORDER BY LoanId DESC
GO

-- View cho chi tiết 1 bản sao sách 
IF OBJECT_ID('v_Copies', 'V') IS NOT NULL
    DROP VIEW v_Copies
GO

CREATE VIEW v_Copies
AS
SELECT 
    bc.CopyId, 
    bc.BookId, 
    b.Title, 
    bc.PublisherName, 
    -- Xử lý hiển thị trạng thái sang tiếng Việt cho dễ đọc
    CASE 
        WHEN bc.Status = -1 THEN N'Đã mất'
        WHEN bc.Status = 0 THEN N'Có sẵn'
        WHEN bc.Status = 1 THEN N'Đang mượn'
        WHEN bc.Status = 2 THEN N'Hư hỏng'
        ELSE N'Không xác định'
    END AS StatusText,
    bc.Barcode, 
    bc.BookMoney, 
    bc.StorageNote,
    bc.Status-- Vẫn giữ cột số để code xử lý nếu cần
FROM BookCopy as bc
    JOIN Book as b ON bc.BookId = b.BookId
GO

SELECT * FROM v_Copies
WHERE Title LIKE N'%Lập%'

-- VIEW thông tin chi tiết của nhân viên (Bao gồm cả Account)
IF OBJECT_ID('v_Staff', 'V') IS NOT NULL
    DROP VIEW v_Staff
GO

CREATE VIEW v_Staff
AS
SELECT 
    s.StaffId, 
    s.FullName, 
    s.Phone, 
    s.DefaultStart, 
    s.DefaultEnd, 
    a.Username, 
    a.[Role],
    a.PasswordHash
FROM Staff AS s
    JOIN Account AS a ON s.StaffId = a.StaffId

GO
SELECT * FROM v_Staff
WHERE StaffId = 4




                    