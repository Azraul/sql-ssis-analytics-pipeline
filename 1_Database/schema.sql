-- =================================================================
-- # SQL SSIS Analytics Project - Database Schema
-- This script creates the database designed to hold the
-- 'all_admissions_clean.csv' file.
-- =================================================================

-- Database name with SQLCMD
:setvar DatabaseName "SqlSsisAnalyticsDB"

-- Make sure we are in the correct Database
USE [$(DatabaseName)];
GO

-- Drop tables in reverse order (handles dependencies)
IF OBJECT_ID('FactAdmissions', 'U') IS NOT NULL DROP TABLE FactAdmissions;
IF OBJECT_ID('DimProgram', 'U') IS NOT NULL DROP TABLE DimProgram;
IF OBJECT_ID('DimUniversity', 'U') IS NOT NULL DROP TABLE DimUniversity;
IF OBJECT_ID('DimApplicantGender', 'U') IS NOT NULL DROP TABLE DimApplicantGender;
IF OBJECT_ID('DimApplicantAgeGroup', 'U') IS NOT NULL DROP TABLE DimApplicantAgeGroup;
GO

-- =============================================
-- DIMENSION TABLES
-- =============================================

-- Stores a unique list of all universities
CREATE TABLE DimUniversity (
    UniversityID INT PRIMARY KEY IDENTITY(1,1),
    UniversityName NVARCHAR(255) NOT NULL UNIQUE
);
GO

-- Stores unique Gender values ('Men', 'Women')
CREATE TABLE DimApplicantGender (
    GenderID INT PRIMARY KEY IDENTITY(1,1),
    Gender NVARCHAR(50) NOT NULL UNIQUE
);
GO

-- Stores unique Age Group values ('18 and under', '19', '20', etc., see vipunen.fi)
CREATE TABLE DimApplicantAgeGroup (
    AgeGroupID INT PRIMARY KEY IDENTITY(1,1),
    AgeGroup NVARCHAR(50) NOT NULL UNIQUE
);
GO

-- Stores the detailed Program and Faculty information, linked to a University
CREATE TABLE DimProgram (
    ProgramID INT PRIMARY KEY IDENTITY(1,1),
    ProgramName NVARCHAR(500) NOT NULL,
    FacultyName NVARCHAR(255) NULL, -- Allow Null due to NDU
    UniversityID INT NOT NULL,
    CONSTRAINT FK_DimProgram_DimUniversity FOREIGN KEY (UniversityID) REFERENCES DimUniversity(UniversityID)
);
GO

-- =============================================
-- FACT TABLE
-- =============================================

-- The central table stores the numeric metrics and links to all dimensions.
CREATE TABLE FactAdmissions (
    AdmissionID INT PRIMARY KEY IDENTITY(1,1),
    [Year] INT NOT NULL,
    FirstTimeApplicants INT NULL,
    TotalApplicants INT NULL,
    Admitted INT NULL,
    
    -- Foreign keys that link to the dimension tables
    ProgramID INT NOT NULL,
    GenderID INT NOT NULL,
    AgeGroupID INT NOT NULL,

    -- Define the relationships for data integrity
    CONSTRAINT FK_FactAdmissions_DimProgram FOREIGN KEY (ProgramID) REFERENCES DimProgram(ProgramID),
    CONSTRAINT FK_FactAdmissions_DimApplicantGender FOREIGN KEY (GenderID) REFERENCES DimApplicantGender(GenderID),
    CONSTRAINT FK_FactAdmissions_DimApplicantAgeGroup FOREIGN KEY (AgeGroupID) REFERENCES DimApplicantAgeGroup(AgeGroupID)
);
GO

PRINT 'Database schema created successfully!';