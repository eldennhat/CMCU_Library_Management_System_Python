if  db_id('LibraryDB') is null
	create database LibraryDB

go
use LibraryDB
go

-- Sách
create table Book
(
	BookId int identity(1,1) primary key,
	ISBN varchar(255) not null unique,
	Title nvarchar(255) not null,
	CategoryName nvarchar(255) not null,
	BookAuthor nvarchar(255) not null,
	PublishYear smallint null,
	
	constraint CK_Book_PublishYear check (PublishYear between 868 and year(getdate()))
)
go

-- Bản sao sách
create table BookCopy
(
	CopyId int identity(1,1) primary key,
	BookId int not null,
	Barcode varchar(255) not null unique, -- mã vạch
	StorageNote nvarchar(255) null, -- kệ của sách
	BookMoney decimal(20,0) null, -- tiền sách
	PublisherName nvarchar(255) not null,
	[Status] smallint NOT NULL default 0, -- -1: Lost, 0: Available, 1: OnLoan, 2: Damaged
    CONSTRAINT CK_Copy_Status check ([Status] IN (-1,0,1,2)),
	constraint FK_Copy_Book foreign key(BookId) references Book(BookId) on delete cascade
)
go

-- Độc giả
create table Reader
(
	ReaderId int identity(1,1) primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	[Address] nvarchar(255) not null,
	CreateAt datetime2 not null default sysdatetime() -- lưu thời điểm bản ghi được tạo
)
go

-- Nhân viên
create table Staff
(
	StaffId int identity(1,1) primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	DefaultStart time(0) null,  -- giờ vào ca mặc định (vd 08:00)
    DefaultEnd time(0) null, -- giờ hết ca mặc định (vd 17:00)
)
go

-- Phiếu mượn
create table Loan
(
	LoanId int identity(1,1) primary key,
	ReaderId int not null,
	StaffId int not null,
	LoanDate datetime2 not null default sysdatetime(),
	DueDate datetime2 not null,
	Note nvarchar(255) null,

	constraint FK_Loan_Reader foreign key(ReaderId) references Reader(ReaderId),
	constraint FK_Loan_Staff foreign key(StaffId) references Staff(StaffId),
	constraint CK_Loan_Due check (DueDate >= LoanDate)
)
go
go

-- Chi tiết phiếu mượn
create table LoanDetail
(
	LoanDetailId int identity(1,1) primary key,
	LoanId int not null,
	CopyId int not null,
	ReturnedDate datetime2 null,
	Fine decimal(20,0) null, -- tiền phạt (nếu ReturnDate sau DueDate thì Fine tự động + 20000/1 ngày trả muộn, nếu sau 10 ngày ReturnedDate vẫn chưa trả thì Fine gấp đôi tiền sách. Bắt đầu tính từ LoanDate)
	Deposit decimal(20, 0) null, -- tiền cọc (gấp đôi tiền sách) 

	constraint UQ_LoanDetail_Copy unique (CopyId, LoanId),
	constraint FK_LoanDetail_Loan foreign key(LoanId) references Loan(LoanId) on delete cascade,
	constraint FK_LoanDetail_Copy foreign key(CopyId) references BookCopy(CopyId)
)
go

-- Tài khoản đăng nhập
create table Account
(
	AccountId int primary key identity(1,1),
	Username varchar(50) not null unique,
	PasswordHash varchar(255) not null,
	[Role] nvarchar(50) not null, -- 'Admin' hoặc 'Librarian'
	StaffId int null, -- liên kết với nhân viên (có thể null cho admin hệ thống)

	constraint CK_Account_Role check (Role in (N'Admin', N'Librarian')),
	constraint FK_Account_Staff foreign key(StaffId) references Staff(StaffId)
)
go

insert into Staff (FullName, Phone, DefaultStart, DefaultEnd)
values 
	(N'Nguyễn Thành An', N'0123456789', '07:00', '10:00'),
	(N'Nguyễn Nhật Minh Quang', N'0123456789', '11:00', '14:00'),
	(N'Đinh Nguyên Hoàng', N'9876543210', '08:00', '16:00'),
	(N'Phạm Tuấn Hưng', N'9876543210', '16:00', '19:00')
go

-- Mặc định 2 tài khoản đăng nhập được cấp phát bởi dev
insert into Account (Username, PasswordHash, [Role], StaffId)
values 
	('admin', '123', N'Admin', null), --username: admin, password: admin123
	('librarian1', '123', N'Librarian', 1),
	('librarian2', '123', N'Librarian', 2),
	('librarian3', '123', N'Librarian', 3),
	('librarian4', '123', N'Librarian', 4)
go

insert into Book (ISBN, Title, CategoryName, BookAuthor, PublishYear)
values 
	('978-604-2-13519-1', N'Dế mèn phiêu lưu kí', N'Truyện dài', N'Tô Hoài', '2023'),
	('978140882594', N'Happy Potter', N'Truyện dài', N'J.K Rowling', '1997'),
	('30184934', N'Chưa có tên', N'Truyện ngắn', N'Chưa có tác giả', '2000')
go

insert into BookCopy (BookId, Barcode, StorageNote, BookMoney, PublisherName, [Status])
values 
	('1', N'12345', N'Kệ truyện dài', '50000', 'NXB1', 0),
	('2', N'67890', N'Kệ truyện dài', '55000', 'NXB2', 0),
	('3', N'24680', N'Kệ truyện ngắn', '60000', 'NXB3', 0)
go

insert into Reader(FullName, Phone, [Address])
values
	(N'Khuất Thuỳ Linh', '0987653213', N'Khu 3 Hoàng Cương'),
	(N'Nguyễn Duy Anh', '0987641345', N'Thanh Ba'),
	(N'Hà Văn Võ Quyền', '0987343526', N'Phú Thọ')
go


-- Trigger tự động tính Fine khi cập nhật ReturnedDate
if object_id('TRG_CalculateFine', 'TR') is not null
    drop trigger TRG_CalculateFine
go

create trigger TRG_CalculateFine
on LoanDetail
after insert, update
as
begin
    -- Chỉ chạy khi ReturnedDate được cập nhật
    if update(ReturnedDate)
    begin
        update ld
        set Fine = 
            case
                -- Chưa trả sách
                when i.ReturnedDate IS NULL then NULL
                
                -- Trả đúng hạn hoặc sớm
                when i.ReturnedDate <= l.DueDate then 0
                
                -- Trả trễ nhưng <= 10 ngày kể từ LoanDate
                when i.ReturnedDate > l.DueDate 
                     and datediff(day, l.LoanDate, i.ReturnedDate) <= 10
                then datediff(day, l.DueDate, i.ReturnedDate) * 20000
                
                -- Quá 10 ngày kể từ LoanDate -> phạt gấp đôi tiền sách
                else bc.BookMoney * 2
            end
        from LoanDetail ld
        inner join inserted i on ld.LoanDetailId = i.LoanDetailId
        inner join Loan l on ld.LoanId = l.LoanId
        inner join BookCopy bc on ld.CopyId = bc.CopyId;
    end
end
go

select *
from dbo.Book
