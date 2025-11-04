if  db_id('LibraryDB') is null
	create database LibraryDB

go
use LibraryDB
go

-- Sách
create table Book
(
	BookId int primary key,
	ISBN varchar(255) not null unique,
	Title nvarchar(255) not null,
	CategoryName nvarchar(255) not null,
	BookAuthor nvarchar(255) not null,
	PublishYear smallint null,
	
	constraint CK_Book_PublishYear check (PublishYear between 868 and year(getdate()))
)


-- Bản sao sách
create table BookCopy
(
	CopyId int primary key,
	BookId int not null,
	Barcode varchar(255) not null unique, -- mã vạch
	StorageNote nvarchar(255) null, -- kệ của sách
	BookMoney decimal(20,0) null, -- tiền sách
	PublisherName nvarchar(255) not null,
	Quantity smallint not null,
	[Status] tinyint not null default 0, -- 0: Available, 1: OnLoan, 2: Lost, 3: Damaged


	-- Số lượng > 0 => Còn sẵn (0: Available) cho phép sửa sang đang mượn (1: OnLoan) 
	-- Số lượng = 0 => Không có sẵn (2: Lost)
	-- Số lượng = -1 => Bị hỏng (3: Damaged)

	constraint CK_Copy_BookMoney check (BookMoney >= 0),
	constraint CK_Copy_Quantity check (Quantity >= -1), 
	constraint CK_Copy_Status_Range check([Status] in (0,1,2,3)),
	constraint CK_Copy_Status_Quantity check (
    ([Status] = 0 and Quantity > 0) or
    ([Status] = 1 and Quantity > 0) or
    ([Status] = 2 and Quantity = 0) or
    ([Status] = 3 and Quantity = -1)
	),
	constraint FK_Copy_Book foreign key(BookId) references Book(BookId) on delete cascade
)


-- Độc giả
create table Reader
(
	ReaderId int primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	[Address] nvarchar(255) not null,
	CreateAt datetime2 not null default sysdatetime(), -- lưu thời điểm bản ghi được tạo
	Fine decimal(20,0) null, -- tiền phạt
	Deposit decimal(20, 0) null -- tiền cọc (tiền cọc > tiền sách + tiền phạt)
)


-- Nhân viên
create table Staff
(
	StaffId int primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	DefaultStart time(0) null,  -- giờ vào ca mặc định (vd 08:00)
    DefaultEnd time(0) null, -- giờ hết ca mặc định (vd 17:00)
)


-- Phiếu mượn
create table Loan
(
	LoanId int primary key,
	ReaderId int not null,
	StaffId int not null,
	LoanDate date not null default cast(getdate() as date),
	DueDate date not null,
	Note nvarchar(255) null,

	constraint FK_Loan_Reader foreign key(ReaderId) references Reader(ReaderId),
	constraint FK_Loan_Staff foreign key(StaffId) references Staff(StaffId),
	constraint CK_Loan_Due check (DueDate >= LoanDate)
)


-- Chi tiết phiếu mượn
create table LoanDetail
(
	LoanDetailId int primary key,
	LoanId int not null,
	CopyId int not null,
	ReturnedDate date null,
	FineAmount decimal(32,2) not null default 0, -- số tiền phạt

	constraint UQ_LoanDetail_Copy unique (CopyId, LoanId),
	constraint FK_LoanDetail_Loan foreign key(LoanId) references Loan(LoanId) on delete cascade,
	constraint FK_LoanDetail_Copy foreign key(CopyId) references BookCopy(CopyId)
)


-- Đặt chỗ
create table Reservation
(
	ReservationId int primary key,
	BookId int not null,
	ReaderId int not null,
	ReservationDate datetime2 not null default sysdatetime(),
	IsFulfilled bit not null default 0,

	constraint FK_Reservation_Book foreign key(BookId) references Book(BookId),
	constraint FK_Reservation_Reader foreign key(ReaderId) references Reader(ReaderId)
)

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

-- Mặc định 2 tài khoản đăng nhập được cấp phát bởi dev
insert into Account (Username, PasswordHash, [Role], StaffId)
values 
	('admin', '123', N'Admin', null), --username: admin, password: admin123
	('librarian1', '123', N'Librarian', null)
