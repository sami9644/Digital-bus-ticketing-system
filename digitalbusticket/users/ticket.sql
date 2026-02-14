CREATE DATABASE busdb;

CREATE TABLE buses(
plate_no VARCHAR(200) PRIMARY KEY,
driver_name TEXT,
driver_phone_no TEXT,
driver_photo TEXT
);


CREATE TABLE users (
userid VARCHAR(100) PRIMARY KEY,
fullname TEXT,
phone_no VARCHAR(25) UNIQUE,
phone_verified VARCHAR(50) DEFAULT 'No',
photo TEXT,
birthdate VARCHAR(100),
password_ TEXT
);



CREATE TABLE tickets (
ticketid VARCHAR(100) PRIMARY KEY,
price FLOAT,
bus VARCHAR(200),
address TEXT,
FOREIGN KEY(bus) REFERENCES buses(plate_no)
);


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