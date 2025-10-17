/*THIS SCRIPT DOESNOT CRATE A DATABASE*/

-- Tạo bảng Tilte (Đầu sách)
CREATE TABLE Tilte (
    Tilte_id CHAR(5) PRIMARY KEY,
    Tilte_name VARCHAR(255),
    author VARCHAR(255)
);

-- Tạo bảng Readers (Độc giả)
CREATE TABLE Readers (
    reader_id SMALLINT PRIMARY KEY,
    reader_name VARCHAR(255),
    contact_number BIGINT
);

-- Tạo bảng Book_copy (Bản sao sách)
CREATE TABLE Book_copy (
    copy_id CHAR(5) PRIMARY KEY,
    Tilte_id CHAR(5),
    [Status] CHAR(50),
    Publisher VARCHAR(50),
    Year_publish SMALLINT,
    Remaining_quantity BIGINT,
    FOREIGN KEY (Tilte_id) REFERENCES Tilte(Tilte_id)
);

-- Tạo bảng Borrow_Ticket (Phiếu mượn)
CREATE TABLE Borrow_Ticket (
    ticket_id INT PRIMARY KEY,
    reader_id SMALLINT,
    borrow_date DATETIME,
    return_date DATETIME,
    FOREIGN KEY (reader_id) REFERENCES Readers(reader_id)
);

-- Tạo bảng Borrow_details (Chi tiết mượn)
CREATE TABLE Borrow_details (
    ticket_id INT,
    copy_id CHAR(5),
    Quantity INT,
    PRIMARY KEY (ticket_id, copy_id), -- Khóa chính ghép
    FOREIGN KEY (ticket_id) REFERENCES Borrow_Ticket(ticket_id),
    FOREIGN KEY (copy_id) REFERENCES Book_copy(copy_id)
);