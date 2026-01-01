CREATE DATABASE busdb;

CREATE TABLE buses(
plate_no VARCHAR(200) PRIMARY KEY,
driver_name TEXT,
driver_phone_no TEXT,
driver_photo TEXT
);
INSERT INTO buses VALUES('11234','Abebe zenebe','0911234567','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpakLfEWE9itUoSbf20LvtoJmOaA224PPYyw&s');

CREATE TABLE users (
userid VARCHAR(100) PRIMARY KEY,
fullname TEXT,
phone_no VARCHAR(25) UNIQUE,
phone_verified VARCHAR(50) DEFAULT 'No',
photo TEXT,
birthdate VARCHAR(100)
);
ALTER TABLE users ADD COLUMN password_ TEXT;


CREATE TABLE tickets (
ticketid VARCHAR(100) PRIMARY KEY,
price FLOAT,
bus VARCHAR(200),
address TEXT,
FOREIGN KEY(bus) REFERENCES buses(plate_no)
);
INSERT INTO tickets VALUES('ticket001',20,'11234','megenagna-yeka abado');

CREATE TABLE payment(
transactionid VARCHAR(200) PRIMARY KEY,
totalprice FLOAT,
totalpersons INT,
paidby VARCHAR(100),
ticket VARCHAR(100),
FOREIGN KEY(paidby) REFERENCES users(userid),
FOREIGN KEY(ticket) REFERENCES tickets(ticketid)
);





CREATE TABLE admins(
username VARCHAR(100) PRIMARY KEY,
password_ TEXT
);


INSERT INTO admins VALUES('admin','admin');