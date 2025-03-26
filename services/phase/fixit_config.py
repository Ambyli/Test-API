from .config import Config
from .sql_config import SQLConfig


# fixit config
class FixitConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Fixit Functions
        # input: FixitID
        # output: [[CaseID, CaseNumber]]
        self.get_case_by_FixitID = "SELECT (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, a.CaseID, b.LocationID FROM {database}.dbo.Fixits as a left join {database}.dbo.Cases as b on a.CaseID = b.CaseID WHERE a.FixitID = ?"
        # input: FixitID
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixit_by_IDs = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.FixitID in (SELECT value FROM STRING_SPLIT(?, ',')) ORDER BY Created DESC"
        # input: FixitID
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixit_by_ID = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM SFTW.dbo.Locations WHERE ID = a.ErrorZone) as Zone, (SELECT Weight FROM SFTW.dbo.Locations WHERE ID = a.ErrorZone) as FixitWeight, (SELECT Location FROM SFTW.dbo.Locations as LocationsTable LEFT JOIN SFTW.dbo.Cases as casesTable ON casesTable.LocationID = LocationsTable.ID WHERE casesTable.CaseID = a.CaseID) as CaseLocation, (SELECT Weight FROM SFTW.dbo.Locations as LocationsTable LEFT JOIN SFTW.dbo.Cases as casesTable ON casesTable.LocationID = LocationsTable.ID WHERE casesTable.CaseID = a.CaseID) as CaseWeight, b.EmployeeID as CreatedBy, c.EmployeeID as CheckoutBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM SFTW.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM SFTW.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM SFTW.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM SFTW.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.FixitID =  ? ORDER BY Created DESC"
        # input: ""
        # output: [[Created, CaseNumber, ShipDate, CustomerID, Error, Zone, FixitWeight, CaseLocation, CaseWeight, Name, Notes, FixitID]]
        self.get_fixits_active = """
            SELECT 
            a.Created, 
            (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, 
            (SELECT TOP 1 ShipDate FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as ShipDate, 
            (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, 
            (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, 
            (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, 
            (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, 
            (SELECT Weight FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as FixitWeight, 
            (
                SELECT 
                TOP 1
                Location 
                FROM 
                {database}.dbo.Locations as LocationsTable 
                LEFT JOIN 
                {database}.dbo.CasePairings as casesTable 
                ON 
                casesTable.LocationID = LocationsTable.ID 
                WHERE 
                casesTable.CaseID = a.CaseID
            ) as CaseLocation, 
            (
                SELECT 
                TOP 1
                Weight 
                FROM 
                {database}.dbo.Locations as LocationsTable 
                LEFT JOIN 
                {database}.dbo.CasePairings as casesTable 
                ON 
                casesTable.LocationID = LocationsTable.ID 
                WHERE 
                casesTable.CaseID = a.CaseID
            ) as CaseWeight, 
            b.EmployeeID as CreatedBy, 
            (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, 
            (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, 
            a.Notes, 
            a.FixitID, 
            a.Checkout, 
            (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, 
            a.Status, 
            a.LocationID 
            FROM 
            {database}.dbo.Fixits as a 
            OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b 
            OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c 
            WHERE 
            (SELECT TOP 1 Status FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) = 'In Production' 
            and 
            a.Checkout IS NULL 
            and 
            a.Status = 2 
            ORDER BY Created DESC
        """
        # input: Date1, Date2
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixits_by_Dates = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and DATEDIFF(day, ?, a.Created) >= 0 and DATEDIFF(day, ?, a.Created) <= 0 and not CHARINDEX(Notes, 'test') > 0 ORDER BY CaseNumber DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # input: CaseID
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixits_by_Case = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b  outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) = ? ORDER BY Created DESC"
        # input: ErrorReason
        # output: [[FCreated, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixits_by_Reason = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName,(SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.ErrorReason = ? and DATEDIFF(day, ?, a.Created) >= 0 and DATEDIFF(day, ?, a.Created) <= 0 ORDER BY Created DESC"
        # input: ErrorZone
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixits_by_Location = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.ErrorZone = ? and DATEDIFF(day, ?, a.Created) >= 0 and DATEDIFF(day, ?, a.Created) <= 0 ORDER BY Created DESC"
        # input: Who
        # output: [[Created, CaseNumber, CustomerID, Error, Name, Notes, FixitID]]
        self.get_fixits_by_Who = "SELECT a.Created, (SELECT TOP 1 CaseNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CaseNumber, (SELECT TOP 1 RXNumber FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerPID, (SELECT TOP 1 CustomerID FROM {database}.dbo.Cases WHERE CaseID = a.CaseID) as CustomerID, (SELECT ReasonType FROM {database}.dbo.FixitReasons WHERE ID = a.ErrorReason) as Error, (SELECT Location FROM {database}.dbo.Locations WHERE ID = a.ErrorZone) as Zone, b.EmployeeID as CreatedBy, (SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), b.EmployeeID) or EmployeeID = CONVERT(varchar(25), b.EmployeeID)) as CreatedName,(SELECT TOP 1 CONCAT(FirstName, ' ', LastName) FROM {database}.dbo.Employees WHERE CONCAT(FirstName, ' ', LastName) = CONVERT(varchar(25), c.EmployeeID) or EmployeeID = CONVERT(varchar(25), c.EmployeeID)) as CheckoutName, a.Notes, a.FixitID, a.Checkout, (SELECT COUNT(AlignerID) FROM {database}.dbo.Aligners WHERE FixitCID = a.FixitID) as Units, a.Status, a.LocationID FROM {database}.dbo.Fixits as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as b outer apply (SELECT TOP 1 EmployeeID FROM SFTW.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckoutVerificationID) as c WHERE a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and a.VerificationID = ? and DATEDIFF(day, ?, a.Created) >= 0 and DATEDIFF(day, ?, a.Created) <= 0 ORDER BY Created DESC"
        # input: Status, StatusID, FixitID
        # output: [[]]
        self.update_fixit_status = "UPDATE {database}.dbo.Fixits SET Status = ? OUTPUT Inserted.FixitID WHERE FixitID = ?"
        # input: CaseID, ErrorZone, ErrorReason, Notes, Created, VerificationID
        # output: [[FixitID]]
        self.insert_fixit = "INSERT INTO {database}.dbo.Fixits (CaseID, ErrorZone, ErrorReason, ErrorVerificationID, Notes, Created, VerificationID, Status, LocationID) OUTPUT Inserted.FixitID, inserted.CaseID, inserted.ErrorZone, inserted.ErrorReason, inserted.ErrorVerificationID, inserted.Notes, inserted.Created, inserted.VerificationID, inserted.Status, inserted.LocationID VALUES (?, ?, ?, ?, ?, GETDATE(), ?, 2, ?)"
        # input: Checkout, CheckoutVerificationID
        # output: [[FixitID]]
        self.remove_fixit = "UPDATE {database}.dbo.Fixits SET Checkout = GETDATE(), CheckoutVerificationID = ?, Status = 4 OUTPUT Inserted.FixitID WHERE FixitID = ?"
        # input: Checkout, CheckoutVerificationID
        # output: [[FixitID]]
        self.deactivate_fixit = "UPDATE {database}.dbo.Fixits SET Checkout = GETDATE(), CheckoutVerificationID = ?, Status = 5 OUTPUT Inserted.FixitID WHERE FixitID = ?"
        # input: FixitID
        # output: [[Checkout]]
        self.check_fixit = (
            "SELECT Checkout FROM {database}.dbo.Fixits WHERE FixitID = ?"
        )
        # input: AlignerID
        # output: [[FixitCID]]
        self.check_aligner = (
            "SELECT FixitCID FROM {database}.dbo.Aligners WHERE AlignerID = ?"
        )
        # input: FixitID, Change, VerificationID, Location
        # output: [[LogID]]
        self.insert_fixit_log = "INSERT INTO {database}.dbo.FixitLog (FixitID, LogTypeID, CaseID, Change, LogNote, Logged, LoggedVerificationID, ErrorZone, ErrorReason, ErrorVerificationID, Notes, Created, VerificationID, Checkout, CheckoutVerificationID, Status, LocationID) OUTPUT Inserted.ID VALUES (?, ?, (SELECT TOP 1 CaseID FROM {database}.dbo.Fixits WHERE FixitID = ?), ?, ?, GETDATE(), ?, (SELECT TOP 1 ErrorZone FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 ErrorReason FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 ErrorVerificationID FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 Notes FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 Checkout FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 CheckoutVerificationID FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Fixits WHERE FixitID = ?), (SELECT TOP 1 LocationID FROM {database}.dbo.Fixits WHERE FixitID = ?))"
        # input: Statuses
        # output: [case_employee_links]
        self.get_fixit_employee_links_by_status = "SELECT ID as FixitEmployeeLinkID, FixitID,  Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CheckedInBy, Status FROM {database}.dbo.FixitEmployeeLinks as a WHERE Status in (SELECT value FROM STRING_SPLIT(?, ','))"
        # input: Statuses, caseNumber
        # output: [case_employee_links]
        self.get_fixit_employee_links_by_fixit_and_status = "SELECT TOP (1) ID as FixitEmployeeLinkID, FixitID,  Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CheckedInBy, Status FROM {database}.dbo.FixitEmployeeLinks as a WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and FixitID = ? order by Created asc"
        # input: Statuses, caseIDs
        # output: [case_employee_links]
        self.get_fixit_employee_links_by_fixits_and_status = "SELECT ID as FixitEmployeeLinkID, FixitID,  Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CheckedInBy, Status FROM {database}.dbo.FixitEmployeeLinks as a WHERE Status in (SELECT value FROM STRING_SPLIT(?, ',')) and FixitID in (SELECT value FROM STRING_SPLIT(?,',')) order by Created asc"
        # Input: EmployeeID, CaseID
        # Output: case_employee_link_ID
        self.insert_fixit_employee_link = "INSERT INTO {database}.[dbo].[FixitEmployeeLinks] ([FixitID], [VerificationID], [Created], [Status]) OUTPUT inserted.ID VALUES (?, ?, GETDATE(), 11)"
        # Input: LogTypeID, LinkID, CaseID, DateIn, CheckIn, DateOut, CheckOut, Status, Change, Description
        # Output: [case_employee_link_log]
        self.insert_fixit_employee_link_log = "INSERT INTO {database}.dbo.FixitEmployeeLinkLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, FixitID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT FixitID FROM {database}.dbo.FixitEmployeeLinks WHERE ID = ?), (SELECT Created FROM {database}.dbo.FixitEmployeeLinks WHERE ID = ?), (SELECT VerificationID FROM {database}.dbo.FixitEmployeeLinks WHERE ID = ?), (SELECT Status FROM {database}.dbo.FixitEmployeeLinks WHERE ID = ?))"
        # Input: LogTypeID, LinkID, CaseID, DateIn, CheckIn, DateOut, CheckOut, Status, Change, Description
        # Output: [case_employee_link_log]
        self.get_fixit_employee_link_logs_by_fixit = "SELECT ID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, FixitID, Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy, Status FROM {database}.dbo.FixitEmployeeLinkLogs as a WHERE Status = 11 and FixitID = ? order by Created asc"
        # Input: EmployeeID
        # Output: [fixit_employee_link_log]
        self.get_fixit_employee_link_logs_by_employeeID = "SELECT ID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, FixitID, Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy, Status FROM {database}.dbo.FixitEmployeeLinkLogs as a WHERE Status = 11 and (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) = ? and Created >= DATEADD(HOUR, -48, GETDATE()) order by Created asc"
        # Input: FixitID
        # Output: [case_employee_links]
        self.remove_employees_FROM_fixit = "UPDATE {database}.dbo.FixitEmployeeLinks SET Status = 12 OUTPUT Inserted.LinkID WHERE FixitID = ?"
        # Input: employeeID, case_employee_link_ID
        # Output: FixitEmployeeLinkID
        self.change_fixit_employee_link = "UPDATE {database}.dbo.FixitEmployeeLinks SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        # input: Location, CaseID
        # output: CaseID
        self.update_fixit_location = "UPDATE {database}.dbo.Fixits SET LocationID = ? OUTPUT Inserted.FixitID WHERE FixitID = ?"
