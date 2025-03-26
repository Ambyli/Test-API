from .config import Config
from .sql_config import SQLConfig


# stock config
class StockConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Stock functions
        self.get_stocks = "SELECT ID, Name, CustomerID, Description, Created, VerificationID, Organizer, Status, Priority, Barcode, DailyUse, LeadTime, ReorderPoint FROM {database}.dbo.StockTypes WHERE Status in (11) ORDER BY Name ASC"
        self.get_stocks_details = """
            SELECT st.ID ,st.Name, st.CustomerID, st.Description, st.Created, ISNULL(COUNT(s.StockID), 0) AS StockTotal,  st.Organizer, st.Status as StockStatus, st.LeadTime, st.ReorderPoint, sts.StatusType, st.Priority, st.Barcode, st.DailyUse, l.ID as LocationID, l.Location as LocationName, stsl.StatusType as LocationStatus
            FROM {database}.dbo.StockTypes st
            LEFT JOIN {database}.dbo.StockStorage s ON st.ID = s.StockID AND s.Status = 11
            LEFT JOIN {database}.dbo.Locations l ON s.Location = l.ID
            LEFT JOIN {database}.dbo.Status sts on sts.ID = st.Status
            LEFT JOIN {database}.dbo.Status stsl on stsl.ID = l.Status
            WHERE s.Status = 11
                    AND st.Status = 11
            GROUP BY st.Name, st.CustomerID, st.Description, st.Created, st.Organizer, st.Status, st.LeadTime, st.ReorderPoint, sts.StatusType, st.Priority, st.Barcode, st.DailyUse, l.ID, l.Location, stsl.StatusType, st.ID
            ORDER BY st.ID
        """
        self.get_active_stocks = "SELECT ID, Name, CustomerID, Description, Created, VerificationID, Organizer, Status, Priority, Barcode FROM {database}.dbo.StockTypes WHERE Status = ? ORDER BY Name ASC"
        self.get_stocks_by_ID = """
            SELECT stockTypeTable.*, EmployeeTable.FirstName as ResponsibleByFirstName, EmployeeTable.LastName as ResponsibleByLastName, VendorTable.Vendor FROM {database}.dbo.StockTypes stockTypeTable 
            LEFT JOIN {database}.dbo.Employees EmployeeTable ON EmployeeTable.EmployeeID = (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = stockTypeTable.ResponsibleVerificationID ORDER BY ID DESC)
            LEFT JOIN {database}.dbo.Vendors VendorTable ON VendorTable.ID = stockTypeTable.VendorID 
            WHERE stockTypeTable.ID = ?
        """
        self.get_stocks_by_locations_and_status = """
            DECLARE @locations varchar(max) = ?
            DECLARE @status int = ?

            SELECT stockTypesTable.*, vendorTable.Vendor as VendorName, stockStorageTable.Location, locationTable.Location as LocationName, statusTable.StatusType, COUNT(stockStorageTable.StockID) as Quantity, stockStorageTable.Removed, stockStorageTable.RemovedVerificationID  FROM {database}.dbo.StockTypes stockTypesTable
            LEFT JOIN {database}.dbo.StockStorage stockStorageTable ON stockStorageTable.StockID = stockTypesTable.ID
            LEFT JOIN {database}.dbo.Locations locationTable ON locationTable.ID = stockStorageTable.Location
            LEFT JOIN {database}.dbo.Status statusTable ON statusTable.ID = locationTable.Status
            LEFT JOIN {database}.dbo.Vendors vendorTable ON vendorTable.ID = stockTypesTable.VendorID
            WHERE (@locations IS NULL OR stockStorageTable.Location IN (SELECT VALUE FROM STRING_SPLIT(@locations, ','))) 
                    AND (@status IS NULL OR stockTypesTable.Status = @status) 
                    AND stockTypesTable.Status = 11
					AND stockStorageTable.Status = 11
					AND stockStorageTable.RemovedVerificationID is NULL
            GROUP BY stockTypesTable.ID, stockTypesTable.Name, stockTypesTable.CustomerID, statusTable.StatusType, stockTypesTable.Description, stockTypesTable.Created, stockTypesTable.VerificationID, stockTypesTable.Organizer, stockTypesTable.Status, stockTypesTable.Priority, stockTypesTable.Barcode, stockTypesTable.DailyUse, stockTypesTable.LeadTime, stockTypesTable.ReorderPoint, stockTypesTable.ResponsibleVerificationID, stockTypesTable.VendorID, vendorTable.Vendor, stockStorageTable.Location, locationTable.Location, stockStorageTable.Removed, stockStorageTable.RemovedVerificationID
            ORDER BY ID
        """
        self.insert_stock = "INSERT INTO {database}.dbo.StockTypes (Name, CustomerID, Description, Created, VerificationID, Status, Priority, Barcode, LeadTime, ReorderPoint, DailyUse, VendorID, ResponsibleVerificationID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, 11, ?, ?, ?, ?, ?, ?, ?)"
        self.update_stock_status = "UPDATE {database}.dbo.StockTypes SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_stock_type = """
            DECLARE @name varchar(50) = ?
            DECLARE @description varchar(200) = ?
            DECLARE @customerID varchar(50) = ?
            DECLARE @priority int = ?
            DECLARE @barcode varchar(36) = ?
            DECLARE @leadTime int = ?
            DECLARE @reorderPoint int = ?
            DECLARE @vendorID int = ?
            DECLARE @responsible int = ?
            DECLARE @dailyUse int = ?
            DECLARE @stockID int = ?
            DECLARE @employeeID int = ?

            UPDATE {database}.dbo.StockTypes SET Name = CONVERT(varchar(50), @name), Description = CONVERT(varchar(200), @description), Priority = @priority, Barcode = CONVERT(varchar(50), @barcode), LeadTime = @leadTime, ReorderPoint = @reorderPoint, DailyUse = @dailyUse, VendorID = @vendorID, ResponsibleVerificationID = @responsible, CustomerID = @customerID
            OUTPUT 43, 'Status: ACTIVE', 'Stock Updated', GETDATE(), CONVERT(varchar(50), @employeeID), @stockID, CONVERT(varchar(50), @name), CONVERT(varchar(50), @customerID), CONVERT(varchar(200), @description), INSERTED.Created, INSERTED.VerificationID, INSERTED.Organizer, INSERTED.Status, @priority
            INTO {database}.dbo.StockTypeLog
            (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, StockID, Name, CustomerID, Description, Created, VerificationID, Organizer, Status, Priority) OUTPUT INSERTED.ID
            WHERE ID = @stockID
        """
        self.update_stock_type_priority = ""
        self.update_stock_type_customer = ""
        self.get_stock_logs_by_stock = """
            WITH stockTypeLog as (
                SELECT stockTypeLogTable.*, logTypeTable.LogType
                FROM {database}.dbo.StockTypeLog stockTypeLogTable 
                LEFT JOIN {database}.dbo.LogTypes logTypeTable ON logTypeTable.ID = stockTypeLogTable.LogTypeID
                WHERE stockTypeLogTable.StockID = ?
            ),
            loggedVerificationID as (
                SELECT LoggedVerificationID FROM stockTypeLog
            ),
            loggedEmployees as (
                SELECT empTable.FirstName, empTable.LastName, linkTable.VerificationID FROM {database}.dbo.VerificationEmployeeLinks linkTable
                LEFT JOIN {database}.dbo.Employees empTable ON linkTable.EmployeeID = empTable.EmployeeID 
                WHERE linkTable.VerificationID in (SELECT LoggedVerificationID FROM loggedVerificationID)
            ),
            stockTypeLogs as (
                SELECT logTable.*, logEmpTable.FirstName, logEmpTable.LastName FROM stockTypeLog logTable
                LEFT JOIN loggedEmployees logEmpTable ON logEmpTable.VerificationID = logTable.LoggedVerificationID
            )
            select * from stockTypeLogs
        """
        self.get_stock_logs = """
            Declare @LogTypeIDs NVARCHAR(MAX) = ?
            Declare @StockIDs NVARCHAR(MAX) = ?
            Declare @CustomerIDs NVARCHAR(MAX) = ?
            Declare @LoggedFrom DATETIME = ?
            Declare @LoggedTo DATETIME = ?;
            WITH stockTypeLog as (
                SELECT stockTypeLogTable.*, logTypeTable.LogType
                FROM {database}.dbo.StockTypeLog stockTypeLogTable 
                LEFT JOIN {database}.dbo.LogTypes logTypeTable ON logTypeTable.ID = stockTypeLogTable.LogTypeID
                WHERE stockTypeLogTable.LogTypeID = 45
            ),
            loggedVerificationID as (
                SELECT LoggedVerificationID FROM stockTypeLog
            ),
            loggedEmployees as (
                SELECT empTable.FirstName, empTable.LastName, linkTable.VerificationID FROM {database}.dbo.VerificationEmployeeLinks linkTable
                LEFT JOIN {database}.dbo.Employees empTable ON linkTable.EmployeeID = empTable.EmployeeID 
                WHERE linkTable.VerificationID in (SELECT LoggedVerificationID FROM loggedVerificationID)
            ),
            stockTypeLogs as (
                SELECT logTable.*, logEmpTable.FirstName, logEmpTable.LastName FROM stockTypeLog logTable
                LEFT JOIN loggedEmployees logEmpTable ON logEmpTable.VerificationID = logTable.LoggedVerificationID
            )
            select * from stockTypeLogs
			WHERE (@LogTypeIDs IS NULL or LogTypeID in (SELECT VALUE FROM STRING_SPLIT(@LogTypeIDs, ',')))
			AND (@StockIDs IS NULL or StockID in (SELECT VALUE FROM STRING_SPLIT(@StockIDs, ',')))
			AND (@CustomerIDs IS NULL or CustomerID in (SELECT VALUE FROM STRING_SPLIT(@CustomerIDs, ',')))
			AND Logged BETWEEN @LoggedFrom AND DATEADD(day, 1, @LoggedTo)
			ORDER BY Logged DESC
        """
        self.insert_stock_log = "INSERT INTO {database}.dbo.StockTypeLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, StockID, Name, CustomerID, Description, Created, VerificationID, Organizer, Status, Priority) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT Name FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT CustomerID FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT Description FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT Created FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT VerificationID FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT Organizer FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT Status FROM {database}.dbo.StockTypes WHERE ID = ?), (SELECT Priority FROM {database}.dbo.StockTypes WHERE ID = ?))"

        # # Storage functions
        self.insert_stock_into_storage = "INSERT INTO {database}.dbo.StockStorage (Created, CreatedVerificationID, Status, StockID, Location) OUTPUT Inserted.ID VALUES (GETDATE(), ?, 11, ?, ?)"
        self.remove_stock_from_storage = "UPDATE {database}.dbo.StockStorage SET Removed = GETDATE(), RemovedVerificationID = ?, Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        self.update_stock_storage_location = "UPDATE {database}.dbo.StockStorage SET Location = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_stock_storage_status = "UPDATE {database}.dbo.StockStorage Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.bulk_update_status_stocks = """
            DECLARE @loc INT = ?
            DECLARE @fromStatus INT = ?
            DECLARE @toStatus INT = ?
            DECLARE @moveQuantity INT = ?
            DECLARE @moveStockID INT = ?;

            WITH stockStorageAvailable AS (
                select top (@moveQuantity) * from {database}.[dbo].[StockStorage] 
                WHERE StockID = @moveStockID AND Location = @loc AND Status = @fromStatus
            )
            UPDATE {database}.[dbo].[StockStorage]
            SET Status = @toStatus
            OUTPUT INSERTED.ID
            FROM {database}.[dbo].[StockStorage] ss
            INNER JOIN stockStorageAvailable ssa ON ssa.ID = ss.ID
            WHERE ssa.ID = ss.ID;
        """
        self.update_stock_storage_stock_type = ""
        self.get_stock_storage_by_location = "SELECT StockStorage.ID, StockStorage.Created, StockStorage.VerificationID, StockStorage.Removed, StockStorage.RemovedBy, StockStorage.Status, StockStorage.StockID, StockStorage.[Location] FROM {database}.dbo.StockStorage LEFT JOIN {database}.dbo.StockTypes ON StockStorage.StockID = StockTypes.ID WHERE StockStorage.[Location] = ? and StockStorage.Removed IS NULL ORDER BY StockTypes.[Name] ASC, StockStorage.ID ASC"

        self.get_stock_storage_by_id_location = "SELECT ID, Created, VerificationID, Removed, RemovedBy, Status, StockID, Location FROM {database}.dbo.StockStorage WHERE StockID = ? and Location = ? ORDER BY Removed DESC, Location DESC, ID DESC"
        self.get_active_stock_storages_by_id_location = """
            SELECT a.ID, a.Created, vrlc.EmployeeID as CreatedBy, a.Removed, vrlr.EmployeeID as RemovedBy, a.Status, a.Location, a.StockID 
            FROM {database}.dbo.StockStorage as a 
            LEFT JOIN {database}.dbo.Locations as b ON a.Location = b.ID 
            LEFT JOIN {database}.dbo.VerificationEmployeeLinks as vrlc ON vrlc.VerificationID = a.CreatedVerificationID
            LEFT JOIN {database}.dbo.VerificationEmployeeLinks as vrlr ON vrlr.VerificationID = a.RemovedVerificationID
            WHERE a.StockID = ? and a.Location = ? and a.Removed IS NULL ORDER BY Created DESC OFFSET(0) ROWS FETCH NEXT ? ROWS ONLY
        """
        self.get_stock_storage = "SELECT ID, Created, VerificationID, Removed, RemovedBy, Status, StockID, Location FROM {database}.dbo.StockStorage"
        self.get_stock_storage_by_each_id = "SELECT Stocks.ID, Stocks.Name, Stocks.CustomerID, Stocks.Barcode, (ISNULL(InStock.Units, 0) + ISNULL(OverStock.Units, 0)) as TotalLeft, ISNULL(InStock.Units, 0) as InStock, ISNULL(OverStock.Units, 0) as OverStock, ISNULL(Removed.Units, 0) as Used FROM {database}.dbo.StockTypes as Stocks OUTER APPLY ( SELECT SUM(Units) as Units FROM ( SELECT a.StockID, COUNT(a.ID) as Units, a.Location as LocationID, b.Location, c.Location as Parent, a.Status FROM {database}.dbo.StockStorage as a LEFT JOIN {database}.dbo.Locations as b ON a.Location = b.ID OUTER APPLY (SELECT Location FROM {database}.dbo.Locations WHERE ID = b.Parent) as c WHERE a.StockID = Stocks.ID and b.Status = 18 and a.Removed IS NULL GROUP BY a.StockID, a.Location, b.Location, c.Location, a.Status ) as inner_query GROUP BY Parent ) as InStock OUTER APPLY ( SELECT SUM(Units) as Units FROM ( SELECT a.StockID, COUNT(a.ID) as Units, a.Location as LocationID, b.Location, c.Location as Parent, a.Status FROM {database}.dbo.StockStorage as a LEFT JOIN {database}.dbo.Locations as b ON a.Location = b.ID OUTER APPLY (SELECT Location FROM {database}.dbo.Locations WHERE ID = b.Parent) as c WHERE a.StockID = Stocks.ID and b.Status = 19 and a.Removed IS NULL GROUP BY a.StockID, a.Location, b.Location, c.Location, a.Status ) as inner_query GROUP BY Parent ) as OverStock OUTER APPLY ( SELECT SUM(Units) as Units FROM ( SELECT a.StockID, COUNT(a.ID) as Units, a.Location as LocationID, b.Location, c.Location as Parent, a.Status FROM {database}.dbo.StockStorage as a LEFT JOIN {database}.dbo.Locations as b ON a.Location = b.ID OUTER APPLY (SELECT Location FROM {database}.dbo.Locations WHERE ID = b.Parent) as c WHERE a.StockID = Stocks.ID and a.Removed IS NOT NULL GROUP BY a.StockID, a.Location, b.Location, c.Location, a.Status ) as inner_query ) as Removed"
        self.insert_stock_storage_log = "INSERT INTO {database}.dbo.StockStorageLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, StorageID, Created, VerificationID, Removed, RemovedBy, Status, StockID, Location) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT Created FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT VerificationID FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT Removed FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT RemovedBy FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT Status FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT StockID FROM {database}.dbo.StockStorage WHERE ID = ?), (SELECT Location FROM {database}.dbo.StockStorage WHERE ID = ?))"
        self.get_stock_storage_log_by_location = "SELECT ID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, StorageID, Created, VerificationID, Removed, RemovedBy, Status, StockID, Location FROM {database}.dbo.StockStorageLog WHERE Location = ? and (LogTypeID = 1 or LogTypeID = 2) ORDER BY Logged DESC"
        # fmt: off
        self.bulk_insert_stocks = '''
            DECLARE @batchID INT = ?
            DECLARE @quantity INT = ?
            DECLARE @stockID INT = ?
            DECLARE @location INT = ?
            DECLARE @employeeID varchar(50) = ?;

            WITH nums AS (
                SELECT TOP (@quantity) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS num
                FROM sys.all_columns a CROSS JOIN sys.all_columns b
            )
            INSERT INTO {database}.[dbo].[StockStorage]
            ([Created], [CreatedVerificationID], [Removed], [RemovedVerificationID], [Status], [StockID], [Location])
            OUTPUT inserted.ID
            SELECT GETDATE(), CONVERT(varchar(50), @employeeID), NULL, NULL, 11, @stockID, @location
            FROM nums;

            WITH nums AS (
                SELECT TOP (@quantity) ID, Created FROM {database}.[dbo].[StockStorage] ORDER BY Created DESC
            )
            INSERT INTO {database}.[dbo].[StockStorageBatchLinks]
            (StockStorageID, BatchID, Created, VerificationID, Status)
            SELECT s.ID, @batchID, GETDATE(), @employeeID, 11
            FROM {database}.[dbo].[StockStorage] s
            INNER JOIN nums ON s.ID = nums.ID;
        '''
        self.bulk_moving_stocks = '''
            DECLARE @fromLoc INT = ?
            DECLARE @toLoc INT = ?
            DECLARE @moveQuantity INT = ?
            DECLARE @moveStockID INT = ?;

            WITH stockStorageAvailable AS (
                SELECT TOP (@moveQuantity) ss.*, (SELECT Location FROM {database}.[dbo].Locations WHERE ID = @toLoc) as LocationTo, l.Location as LocationFrom FROM {database}.[dbo].[StockStorage] ss
                LEFT JOIN {database}.[dbo].Locations l ON ss.Location = l.ID 
                WHERE StockID = @moveStockID AND ss.Location = @fromLoc
            )

            UPDATE {database}.[dbo].[StockStorage]
            SET Location = @toLoc
            OUTPUT INSERTED.ID
            FROM {database}.[dbo].[StockStorage] ss
            INNER JOIN stockStorageAvailable ssa ON ssa.ID = ss.ID
            WHERE ssa.ID = ss.ID;
        '''
        self.get_stock_storage_logs_by_stockID = '''
            SELECT ssl.StockID as ID, ssl.Logged, ssl.LoggedVerificationID, eb.FirstName, eb.LastName, COUNT(ssl.LogNote) as Quantity,MAX(ssl.LogNote) as LogNote, ssl.LogTypeID, lt.LogType
            FROM {database}.[dbo].[StockStorageLog] ssl
            LEFT JOIN {database}.[dbo].LogTypes lt ON lt.ID = ssl.LogTypeID
            LEFT JOIN {database}.[dbo].EmployeeIDs eb ON eb.VerificationID = ssl.LoggedVerificationID
            WHERE StockID = ?
            GROUP BY ssl.StockID,ssl.Logged, ssl.Location, ssl.LogTypeID, lt.LogType, ssl.LoggedVerificationID, eb.FirstName, eb.LastName
            ORDER BY Logged DESC
        '''

        # fmt: on
        # # Action functions
        self.get_stock_actions = "SELECT stockActionsTable.*, ( SELECT COUNT(*) FROM {database}.dbo.StockTypeActionsLinks WHERE ActionID = stockActionsTable.ID) as ItemQuantity FROM {database}.dbo.StockActions stockActionsTable ORDER BY NAME ASC"
        self.get_stock_action_by_Location = "SELECT stockActionsTable.*, ( SELECT COUNT(*) FROM {database}.dbo.StockTypeActionsLinks WHERE ActionID = stockActionsTable.ID) as ItemQuantity FROM {database}.dbo.StockActions stockActionsTable WHERE LocationID is not Null AND (? IS NULL OR LocationID IN (SELECT VALUE FROM STRING_SPLIT(?,','))) ORDER BY LocationID ASC, NAME ASC"
        self.get_stock_action_by_ID = (
            "SELECT * FROM {database}.dbo.StockActions WHERE ID = ? ORDER BY Name ASC"
        )
        self.get_stock_action_by_Barcode = "SELECT * FROM {database}.dbo.StockActions WHERE Barcode = ? ORDER BY Name ASC"
        self.get_active_stock_actions = "SELECT stockActionsTable.*, ( SELECT COUNT(*) FROM {database}.dbo.StockTypeActionsLinks WHERE ActionID = stockActionsTable.ID AND Status = 11) as ItemQuantity FROM {database}.dbo.StockActions stockActionsTable ORDER BY NAME ASC"
        self.insert_stock_action = "INSERT INTO {database}.dbo.StockActions (Name, Description, Priority, CustomerID, Created, VerificationID, Status, Barcode, LocationID) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, 11, ?, ?)"
        self.insert_stock_action_auto_barcode = """
            DECLARE @name VARCHAR(20) = ?
            DECLARE @description VARCHAR(100) = ?
            DECLARE @priority INT = ?
            DECLARE @customerID VARCHAR(50) = ?
            DECLARE @verificationID INT = ?
            DECLARE @locationID INT = ?

            IF EXISTS (SELECT 1 FROM {database}.dbo.CustomerAccounts WHERE CustomerID = @customerID AND AccountID is not Null)
            BEGIN 
                INSERT INTO {database}.dbo.StockActions (Name, Description, Priority, CustomerID, Created, VerificationID, Status, Barcode, LocationID)
                OUTPUT Inserted.ID
                SELECT @name, @description, @priority, @customerID, GETDATE(), @verificationID, 11, CA.AccountID + '-' + CONVERT(varchar(max), IDENT_CURRENT('{database}.dbo.StockActions')+1), @locationID
                FROM {database}.dbo.CustomerAccounts CA
                WHERE CA.CustomerID = @customerID
                ORDER BY CA.DateIn DESC
                OFFSET 0 ROWS
                FETCH NEXT 1 ROWS ONLY;
            END
        """
        self.update_stock_action = "UPDATE {database}.dbo.StockActions SET Name = ?, Description = ?, Priority = ?, LocationID = ? OUTPUT INSERTED.ID WHERE ID = ?"
        self.remove_stock_action = "UPDATE {database}.dbo.StockActions SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"

        # # Action Link functions
        self.get_links_by_action = "SELECT ID, ActionID, StockID, Count, Created, VerificationID, Status, Initial, Destination FROM {database}.dbo.StockTypeActionsLinks WHERE ActionID = ? ORDER BY ID DESC"
        self.get_stock_action_links_by_barcode = """
            SELECT StockTypeTable.Name as StockName, StockTypeActionLinksTable.*, LocationFromTable.Location as InitialName, LocationToTable.Location as DestinationName  FROM {database}.dbo.StockTypeActionsLinks StockTypeActionLinksTable
            LEFT JOIN {database}.dbo.StockActions SA ON SA.ID = StockTypeActionLinksTable.ActionID
            LEFT JOIN {database}.dbo.StockTypes StockTypeTable ON StockTypeTable.ID = StockTypeActionLinksTable.StockID
            LEFT JOIN {database}.dbo.Locations LocationFromTable ON LocationFromTable.ID = StockTypeActionLinksTable.Initial
            LEFT JOIN {database}.dbo.Locations LocationToTable ON LocationToTable.ID = StockTypeActionLinksTable.Destination
            WHERE SA.Barcode = ? AND StockTypeActionLinksTable.Status = 11 ORDER BY StockName ASC, InitialName ASC, DestinationName ASC
        """
        self.link_stock_with_action = "INSERT INTO {database}.dbo.StockTypeActionsLinks (ActionID, StockID, Count, Created, VerificationID, Status, Initial, Destination) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, 11, ?, ?)"
        self.remove_stock_action_link = "UPDATE {database}.dbo.StockTypeActionsLinks SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        self.update_stock_action_link = "UPDATE {database}.dbo.StockTypeActionsLinks SET Count = ?, Initial = ?, Destination = ? OUTPUT Inserted.ID WHERE ID = ?"
        # # Stock Type Action Links
        self.get_stock_type_action_links_by_action = "SELECT StockTypeActionLinksTable.*, (SELECT COUNT(*) FROM {database}.dbo.StockStorage WHERE StockID = StockTypeActionLinksTable.StockID AND Location = StockTypeActionLinksTable.Initial AND Status = 11) AS TotalLeft, (SELECT Location FROM {database}.dbo.Locations WHERE ID = StockTypeActionLinksTable.Initial) as InitialLocation,  (SELECT Location FROM {database}.dbo.Locations WHERE ID = StockTypeActionLinksTable.Destination) as DestinationLocation, StockTypesTable.Name as StockName, StockTypesTable.CustomerID FROM {database}.dbo.StockTypeActionsLinks StockTypeActionLinksTable LEFT JOIN {database}.dbo.StockTypes StockTypesTable ON StockTypesTable.ID = StockTypeActionLinksTable.StockID  WHERE (? IS NULL OR ActionID = ?) AND StockTypeActionLinksTable.Status = 11 ORDER BY StockID ASC"
        # # Create Stock Type Action Links
        self.bulk_insert_stock_type_action_links = """
            DECLARE @actionID INT = ?
            DECLARE @empID varchar(36) = ?
            DECLARE @status INT = ?
            DECLARE @initials varchar(max) = ?
            DECLARE @destinations varchar(max) = ?
            DECLARE @stockIDs varchar(max) = ?
            DECLARE @counts varchar(max) = ?;

            WITH stock AS (  SELECT value as StockID, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS row_num  FROM STRING_SPLIT(@stockIDs, ',')),
            count AS (  SELECT value as Count, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS row_num  FROM STRING_SPLIT(@counts, ',')),
            initial AS (  SELECT value as Initial, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS row_num  FROM STRING_SPLIT(@initials, ',')),
            dest AS (  SELECT value as Destination, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS row_num  FROM STRING_SPLIT(@destinations, ','))

            INSERT INTO {database}.dbo.StockTypeActionsLinks (ActionID,StockID,Count,Created,VerificationID,Status,Initial,Destination) OUTPUT INSERTED.ID
            SELECT @actionID, s.StockID, CONVERT(int, c.Count), GETDATE(), @empID, @status, CONVERT(INT, i.Initial), CONVERT(INT, d.Destination)
            FROM stock as s
            INNER JOIN count c ON s.row_num = c.row_num
            INNER JOIN initial i ON s.row_num = i.row_num
            INNER JOIN dest d ON s.row_num = d.row_num
        """

        # # Stock Storage File Link functions
        self.get_stock_storage_files_by_ID = "SELECT a.ID, a.StockStorageID, b.FileTypeID, a.Path, a.Created, a.VerificationID, a.Status FROM {database}.dbo.StockStorageFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.StockStorageID = ? ORDER BY a.ID ASC"
        self.get_active_stock_storage_files_by_ID = "SELECT a.ID, a.StockStorageID, b.FileTypeID, a.Path, a.Created, a.VerificationID, a.Status FROM {database}.dbo.StockStorageFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.StockStorageID = ? and a.Status = 11 ORDER BY a.ID ASC"
        self.insert_stock_storage_file = "INSERT INTO {database}.dbo.StockStorageFileLinks (StockStorageID, FileID, Path, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?)"
        self.update_status_of_stock_storage_file = "UPDATE {database}.dbo.StockStorageFileLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.remove_stock_storage_file = "UPDATE {database}.dbo.StockStorageFileLinks SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"

        # # Stock Storage Batch
        self.insert_stock_storage_batch_link = "INSERT INTO {database}.dbo.StockStorageBatchLinks (StockStorageID, BatchID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        self.get_stock_storage_by_batch = "SELECT storage.ID, storage.Created, storage.VerificationID, storage.Removed, storage.RemovedBy, storage.Status, storage.StockID, storage.Location FROM {database}.dbo.StockStorage as storage LEFT JOIN {database}.dbo.StockStorageBatchLinks as links ON storage.ID = links.StockStorageID WHERE links.BatchID = ? ORDER BY storage.ID DESC"

        self.insert_stock_storage_batch = "INSERT INTO {database}.dbo.StockStorageBatch ([Order], Created, VerificationID, Description, Location) OUTPUT Inserted.ID VALUES (?, GETDATE(), ?, ?, ?)"
        self.get_stock_storage_batch_by_ID = "SELECT ID, [Order], Created, VerificationID, Description, Location FROM {database}.dbo.StockStorageBatch WHERE ID = ?"
        self.get_stock_storage_batch_by_location = "SELECT ID, [Order], Created, VerificationID, Description, Location FROM {database}.dbo.StockStorageBatch WHERE Location = ? ORDER BY Created DESC"

        self.insert_stock_storage_batch_file = "INSERT INTO {database}.dbo.StockStorageBatchFileLinks (StockStorageBatchID, FileID, Path, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, 11)"
        self.get_stock_storage_batch_file_by_batch = "SELECT ID, StockStorageBatchID, FileID, Path, Created, VerificationID, Status FROM {database}.dbo.StockStorageBatchFileLinks WHERE StockStorageBatchID = ? ORDER BY Created DESC"

        self.insert_stock_storage_batch_file_links = "INSERT INTO {database}.dbo.StockStorageBatchFileLinks (StockStorageBatchID ,FileID, Created, VerificationID,Status) OUTPUT INSERTED.ID SELECT ?, value, GETDATE(), ?, ? FROM STRING_SPLIT(?, ',')"
        # # Stock Storage Batch File Links
        self.get_stock_storage_batch_history_by_location = "SELECT a.ID as BatchID, a.[Order], a.[Description], a.[Order], b.ID as LinkID, b.[Path], a.[Location], a.[Created], a.[VerificationID] FROM {database}.dbo.StockStorageBatch as a OUTER APPLY (SELECT * FROM {database}.dbo.StockStorageBatchFileLinks WHERE StockStorageBatchID = a.ID) as b WHERE DATEDIFF(day, ?, a.Created) >= 0 and DATEDIFF(day, ?, a.Created) <= 0 and a.[Location] = ? ORDER BY a.Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
