-- Table schema examples for SQL Server database

-- Example 1: T_CINS_dwell table (contains dwell time data)
CREATE TABLE dbo.T_CINS_dwell (
    ID INT PRIMARY KEY IDENTITY(1,1),
    ContainerNumber NVARCHAR(20) NOT NULL,
    Terminal NVARCHAR(50) NOT NULL,
    VesselName NVARCHAR(100) NOT NULL,
    ArrivalDate DATETIME NOT NULL,
    DepartureDate DATETIME NULL,
    DwellTimeHours AS DATEDIFF(HOUR, ArrivalDate, COALESCE(DepartureDate, GETDATE())),
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
    LastUpdate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT UQ_ContainerNumber UNIQUE (ContainerNumber)
);

-- Example 2: Ref_MonthIndex table (contains month index reference data)
CREATE TABLE dbo.Ref_MonthIndex (
    YearMonth INT PRIMARY KEY,
    Year INT NOT NULL,
    Month INT NOT NULL,
    MonthName NVARCHAR(50) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Quarter INT NOT NULL,
    IsCurrent BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE()
);

-- Example 3: T_Scorecard_Dwelltime table (contains scorecard metrics)
CREATE TABLE dbo.T_Scorecard_Dwelltime (
    ID INT PRIMARY KEY IDENTITY(1,1),
    YearMonth INT NOT NULL,
    Terminal NVARCHAR(50) NOT NULL,
    AverageDwellTime DECIMAL(5, 2) NOT NULL,
    TargetDwellTime DECIMAL(5, 2) NOT NULL,
    Variance DECIMAL(5, 2) NOT NULL,
    Volume INT NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    LastUpdate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Scorecard_Month FOREIGN KEY (YearMonth) REFERENCES dbo.Ref_MonthIndex(YearMonth)
);