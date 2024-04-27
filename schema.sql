CREATE TABLE IF NOT EXISTS Landlord (
    Lid INT AUTO_INCREMENT PRIMARY KEY,
    LFname VARCHAR(20),
    LLname VARCHAR(20),
    LEmail VARCHAR(40),
    LPhone VARCHAR(15),
    LAddress VARCHAR(50),
    LPassword VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS  Property(
	Pid INT AUTO_INCREMENT PRIMARY KEY,
    PCategory varchar(20),
    PLocation varchar(20),
    PCity varchar(20),
    PState varchar(20),
    PPin varchar(20),
    Lid INT,
   FOREIGN KEY (Lid) REFERENCES Landlord(Lid) on delete cascade
);

ALTER TABLE  Property AUTO_INCREMENT = 101;

CREATE TABLE IF NOT EXISTS  Tenant(
	Tid INT AUTO_INCREMENT PRIMARY KEY,
    TFname VARCHAR(20),
    TLname VARCHAR(20),
    TEmail VARCHAR(40),
    TPhone VARCHAR(15),
    DOC date,
    Pid INT,
	FOREIGN KEY (Pid) REFERENCES Property(Pid) on delete cascade
);

ALTER TABLE  Tenant AUTO_INCREMENT = 201;

CREATE TABLE IF NOT EXISTS  Rent (
    Lid INT,
    Tid INT,
    Deposit INT,
    Rent INT,
    PaymentStatus ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid', 
    PayDate DATE,
    PRIMARY KEY (Lid, Tid),
    FOREIGN KEY (Lid) REFERENCES Landlord(Lid) ON DELETE CASCADE,
    FOREIGN KEY (Tid) REFERENCES Tenant(Tid) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS  TenantPhone (
    Tid INT,
    PhoneNumber VARCHAR(20),
    FOREIGN KEY (Tid) REFERENCES Tenant(Tid) on delete cascade
);