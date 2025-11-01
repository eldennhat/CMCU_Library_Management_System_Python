if  db_id('LibraryDB') is null
	create database LibraryDB

go
use LibraryDB
go

-- Danh mục cơ bản
create table Category -- thể loại
(
	CategoryId varchar(255) primary key,
	CategoryName nvarchar(255) not null unique,
	[Description] nvarchar(max) null
)

create table Publisher -- nhà xuất bản
(
	PublisherId varchar(255) primary key,
	PublichserName nvarchar(255) not null unique
)

create table Author -- tác giả
(
	AuthorId varchar(255) primary key,
	AuthorName nvarchar(255) not null unique,
	PenName nvarchar(255) null unique
)


-- Sách
create table Book
(
	BookId varchar(255) primary key,
	ISBN varchar(255) not null unique,
	Title nvarchar(255) not null,
	CategoryId varchar(255) not null,
	PublisherId varchar(255) not null,
	PublishYear smallint null,
	
	constraint CK_Book_PublishYear check (PublishYear between 868 and year(getdate())), -- Năm xuất bản nằm giữa 868 và hiện tại
	constraint FK_Book_Category foreign key(CategoryId) references Category(CategoryId), -- CategoryId trong Book phải tồn tại bên Category
	constraint FK_Book_Publisher foreign key(PublisherId) references Publisher(PublisherId) -- PublisherId trong Book phải tồn tại bên Publisher (có thể NULL)
)


create table BookAuthor
(
	BookId varchar(255) not null,
	AuthorId varchar(255) not null
	primary key (BookId, AuthorId)

	constraint FK_BA_Book foreign key(BookId) references Book(BookId) on delete cascade,
	constraint FK_BA_Author foreign key(AuthorId) references Author(AuthorId) on delete cascade
)


-- Bản sao sách
create table BookCopy
(
	CopyId varchar(255) primary key,
	BookId varchar(255) not null,
	Barcode varchar(255) not null unique, -- mã vạch
	StorageNote nvarchar(255) null, -- kệ của sách
	[Status] tinyint not null default 0 -- 0: Available, 1: OnLoan, 2: Lost, 3: Damaged

	constraint CK_Copy_Status check([Status] in (0,1,2,3)),
	constraint FK_Copy_Book foreign key(BookId) references Book(BookId) on delete cascade,
)


-- Độc giả
create table Reader
(
	ReaderId varchar(255) primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	[Address] nvarchar(255) not null,
	CreateAt datetime2 not null default sysdatetime(), -- lưu thời điểm bản ghi được tạo
	IsActive bit not null default 1 -- mặc định đang hoạt động
)


-- Nhân viên
create table Staff
(
	StaffId varchar(255) primary key,
	FullName nvarchar(255) not null,
	Phone nvarchar(255) not null,
	Role nvarchar(255) not null,
	IsActive bit not null default 1
)


-- Phiếu mượn
create table Loan
(
	LoanId varchar(255) primary key,
	ReaderId varchar(255) not null,
	StaffId varchar(255) not null,
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
	LoanDetailId varchar(255) primary key,
	LoanId varchar(255) not null,
	CopyId varchar(255) not null,
	ReturnedDate date null,
	FineAmount decimal(32,2) not null default 0, -- số tiền phạt

	constraint UQ_LoanDetail_Copy unique (CopyId, LoanId),
	constraint FK_LoanDetail_Loan foreign key(LoanId) references Loan(LoanId) on delete cascade,
	constraint FK_LoanDetail_Copy foreign key(CopyId) references BookCopy(CopyId)
)


-- Đặt chỗ
create table Reservation
(
	ReservationId varchar(255) primary key,
	BookId varchar(255) not null,
	ReaderId varchar(255) not null,
	ReservationDate datetime2 not null default sysdatetime(),
	IsFulfilled bit not null default 0,

	constraint FK_Reservation_Book foreign key(BookId) references Book(BookId),
	constraint FK_Reservation_Reader foreign key(ReaderId) references Reader(ReaderId)
)

