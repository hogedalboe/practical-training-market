-- Database: practicaltrainingmarket

--DROP DATABASE practicaltrainingmarket;

--CREATE DATABASE practicaltrainingmarket
--    WITH 
--    OWNER = postgres
--    ENCODING = 'UTF8'
--    LC_COLLATE = 'English_United States.1252'
--    LC_CTYPE = 'English_United States.1252'
--    TABLESPACE = pg_default
--    CONNECTION LIMIT = -1;

-- Drop tables
DROP TABLE IF EXISTS School CASCADE;
DROP TABLE IF EXISTS Education CASCADE;
DROP TABLE IF EXISTS Facility CASCADE;
DROP TABLE IF EXISTS Committee CASCADE;
DROP TABLE IF EXISTS Organization CASCADE;
DROP TABLE IF EXISTS Seating CASCADE;
DROP TABLE IF EXISTS Specialization CASCADE;
DROP TABLE IF EXISTS ProductionUnit CASCADE;
DROP TABLE IF EXISTS Approval CASCADE;
DROP TABLE IF EXISTS Distance CASCADE;
DROP TABLE IF EXISTS Company CASCADE;
DROP TABLE IF EXISTS Financial CASCADE;
DROP TABLE IF EXISTS PostalArea CASCADE;
DROP TABLE IF EXISTS Sector CASCADE;
DROP TABLE IF EXISTS Business CASCADE;
DROP TABLE IF EXISTS Region CASCADE;
DROP TABLE IF EXISTS Municipality CASCADE;
DROP TABLE IF EXISTS Limitation CASCADE;
DROP TABLE IF EXISTS Limits CASCADE;

-- Tables
CREATE TABLE School (
	SchoolNum INT,
	Name VARCHAR(100) NOT NULL,
	PRIMARY KEY (SchoolNum)
);

CREATE TABLE Committee (
	CommitteeCode INT,
	Name VARCHAR(100),
	PRIMARY KEY (CommitteeCode)
);

CREATE TABLE Education (
	EduNum INT,
	Name VARCHAR(100) NOT NULL,
	CommitteeCode INT,
	PRIMARY KEY (EduNum),
	FOREIGN KEY (CommitteeCode) REFERENCES Committee (CommitteeCode)
);

CREATE TABLE Region (
	RegionCode INT,
	Name VARCHAR(100) NOT NULL,
	PRIMARY KEY (RegionCode)
);

CREATE TABLE Municipality (
	MunicipalityCode INT,
	Name VARCHAR(100) NOT NULL,
	RegionCode INT,
	PRIMARY KEY (MunicipalityCode),
	FOREIGN KEY (RegionCode) REFERENCES Region (RegionCode)
);

CREATE TABLE PostalArea (
	PostalCode INT,
	MunicipalityCode INT,
	City VARCHAR(100),
	PRIMARY KEY (PostalCode),
	FOREIGN KEY (MunicipalityCode) REFERENCES Municipality (MunicipalityCode)
);

CREATE TABLE Facility (
	ID SERIAL,
	SchoolNum INT,
	EduNum INT,
	Street VARCHAR(100),
	StreetNumber VARCHAR(100),
	City VARCHAR(100),
	PostalCode INT,
	PRIMARY KEY (ID),
	FOREIGN KEY (PostalCode) REFERENCES PostalArea (PostalCode),
	FOREIGN KEY (SchoolNum) REFERENCES School (SchoolNum),
	FOREIGN KEY (EduNum) REFERENCES Education (EduNum)
);

/*
CREATE TABLE Organization (
	OrgNum INT,
	Name VARCHAR(100),
	OrgType VARCHAR(100),
	PRIMARY KEY (OrgNum)
);

CREATE TABLE Seating (
	OrgNum INT,
	CommitteeCode INT,
	Seats INT,
	PRIMARY KEY (OrgNum, CommitteeCode),
	FOREIGN KEY (OrgNum) REFERENCES Organization (OrgNum),
	FOREIGN KEY (CommitteeCode) REFERENCES Committee (CommitteeCode)
);
*/

CREATE TABLE Specialization (
	SpecNum INT,
	EduNum INT,
	Name VARCHAR(100),
	PRIMARY KEY (SpecNum, EduNum),
	FOREIGN KEY (EduNum) REFERENCES Education (EduNum)
);

CREATE TABLE Sector (
	SectorCode INT,
	SectorName VARCHAR(100),
	PRIMARY KEY (SectorCode)
);

CREATE TABLE Business (
	BusinessCode INT,
	Name VARCHAR(100),
	PRIMARY KEY (BusinessCode)
);

CREATE TABLE Company (
	CVRNum INT,
	Name VARCHAR(100),
	SectorCode INT,
	BusinessCode INT,
	Employees INT,
	Established DATE,
	Website VARCHAR(100),
	PRIMARY KEY (CVRNum),
	FOREIGN KEY (SectorCode) REFERENCES Sector (SectorCode),
	FOREIGN KEY (BusinessCode) REFERENCES Business (BusinessCode)
);

CREATE TABLE ProductionUnit (
	PNum INT,
	CVRNum INT,
	Street VARCHAR(100),
	StreetNumber VARCHAR(100),
	City VARCHAR(100),
	PostalCode INT,
	PRIMARY KEY (PNum),
	FOREIGN KEY (PostalCode) REFERENCES PostalArea (PostalCode),
	FOREIGN KEY (CVRNum) REFERENCES Company (CVRNum)
);

CREATE TABLE Limitation (
	LimitationCode INT,
	Name VARCHAR(100),
	PRIMARY KEY (LimitationCode)
);

CREATE TABLE Approval (
	SpecNum INT,
	EduNum INT,
	PNum INT,
	SubmissionDate DATE,
	ApprovalDate DATE,
	ApprovalAmount INT,
	CurrentAmount INT,
	OtherActive INT,
	PRIMARY KEY (SpecNum, EduNum, PNum),
	FOREIGN KEY (SpecNum, EduNum) REFERENCES Specialization (SpecNum, EduNum),
	FOREIGN KEY (PNum) REFERENCES ProductionUnit (PNum)
);

CREATE TABLE Limits (
	LimitationCode INT,
	SpecNum INT,
	EduNum INT,
	PNum INT,
	PRIMARY KEY (LimitationCode, SpecNum, EduNum, PNum),
	FOREIGN KEY (LimitationCode) REFERENCES Limitation (LimitationCode),
	FOREIGN KEY (SpecNum, EduNum, PNum) REFERENCES Approval (SpecNum, EduNum, PNum)
);

CREATE TABLE Distance (
	PNum INT,
	FacilityID INT,
	Km FLOAT,
	Hours INT,
	Minutes INT,
	PRIMARY KEY (PNum, FacilityID),
	FOREIGN KEY (PNum) REFERENCES ProductionUnit (PNum),
	FOREIGN KEY (FacilityID) REFERENCES Facility (ID)
);

CREATE TABLE Financial (
	PubYear INT,
	CVRNum INT,
	LiquidityRatio FLOAT,
	ROI FLOAT,
	SolvencyRatio FLOAT,
	NetTurnover FLOAT,
	GrossProfit FLOAT,
	Equity FLOAT,
	NetResult FLOAT,
	Balance FLOAT,
	Currency VARCHAR(3),
	PRIMARY KEY (PubYear, CVRNum),
	FOREIGN KEY (CVRNum) REFERENCES Company (CVRNum)
);