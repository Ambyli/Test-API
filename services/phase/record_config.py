from .config import Config
from .sql_config import SQLConfig


# record config
class RecordConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)
        # fmt: off

        ## Laser

        # # get laser record Logs by case
        self.get_laser_record_logs_by_case = "SELECT lrl.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.LaserRecordLogs as lrl OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = lrl.VerificationID ORDER BY ID DESC) as vel WHERE CaseNumber = ?"

        # # get all laser records 
        self.get_all_laser_records = "SELECT lr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.LaserRecords as lr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = lr.VerificationID ORDER BY ID DESC) as vel"
        
        # # get records by case 
        self.get_laser_records_by_case = "SELECT lr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.LaserRecords as lr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = lr.VerificationID ORDER BY ID DESC) as vel WHERE CaseNumber = ?"
        
        # # get records by id 
        self.get_laser_records_by_laser = "SELECT lr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.LaserRecords as lr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = lr.VerificationID ORDER BY ID DESC) as vel WHERE ID = ?"

        # # create new laser record
        # # input: LaserMark, Aligner, CaseNumber, Correct, VerificationID
        self.create_laser_record = """
            DECLARE  @TempLaserRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, LaserRecordID INT, LaserMark VARCHAR(255), Aligner VARCHAR(255), CaseNumber INT, Correct BIT, VerificationID INT,  Created DATETIME, Status INT, BagUDID INT);
            INSERT INTO {database}.dbo.LaserRecords (LaserMark, Aligner, CaseNumber, Correct, VerificationID, Created, Status, BagUDID)
            OUTPUT 55, 'LASER RECORD CREATED', 'New', GETDATE(), inserted.VerificationID, inserted.ID, inserted.LaserMark, inserted.Aligner, inserted.CaseNumber, inserted.Correct,inserted.VerificationID, inserted.Created,  inserted.Status, inserted.BagUDID
            INTO @TempLaserRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LaserRecordID, LaserMark, Aligner, CaseNumber, Correct, VerificationID, Created,  Status, BagUDID)
            OUTPUT inserted.ID
            VALUES (?, ?, ?, ?, ?, GETDATE(), 11, ?)
            INSERT INTO {database}.dbo.LaserRecordLogs OUTPUT inserted.ID SELECT * FROM @TempLaserRecordLogs;
        """

        # # update laser record
        # # input: LaserMark, Aligner, Change, updateBy, ID
        self.update_laser_record = """
            DECLARE @TempLaserRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, LaserRecordID INT, LaserMark VARCHAR(255), Aligner VARCHAR(255), CaseNumber INT, Correct BIT, VerificationID INT, Created DATETIME, Status INT, BagUDID INT);
            UPDATE {database}.dbo.LaserRecords SET LaserMark = ?, Aligner = ?, BagUDID = ?, Correct = ?
            OUTPUT 56, 'LASER RECORD UPDATED', ?, GETDATE(), ?, inserted.ID, inserted.LaserMark, inserted.Aligner, inserted.CaseNumber, inserted.Correct, inserted.VerificationID, inserted.Created, inserted.Status, inserted.BagUDID
            INTO @TempLaserRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LaserRecordID, LaserMark, Aligner, CaseNumber, Correct, VerificationID, Created, Status, BagUDID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.LaserRecordLogs OUTPUT inserted.ID SELECT * FROM @TempLaserRecordLogs;
        """

        # # set status of all records for the given case to 12 
        self.delete_laser_record_by_laser_case = """
            DECLARE @TempLaserRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, LaserRecordID INT, LaserMark VARCHAR(255), Aligner INT, CaseNumber INT, Correct BIT, VerificationID VARCHAR(255), Created DATETIME, Status INT, BagUDID INT);
            UPDATE {database}.dbo.LaserRecords SET Status = 12
            OUTPUT 56, 'LASER RECORD REMOVED', 'Set laser record inactive', GETDATE(), ?,  inserted.ID,inserted.LaserMark, inserted.Aligner, inserted.CaseNumber, inserted.Correct, inserted.VerificationID, inserted.Created, inserted.Status, inserted.BagUDID
            INTO @TempLaserRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LaserRecordID,  LaserMark, Aligner,CaseNumber, Correct, VerificationID, Created, Status, BagUDID)
            OUTPUT inserted.ID
            WHERE CaseNumber = ?;
            INSERT INTO {database}.dbo.LaserRecordLogs OUTPUT inserted.ID SELECT * FROM @TempLaserRecordLogs;
        """

        # # set status of the given record id to 12 
        self.delete_laser_record_by_laser_record = """
            DECLARE @TempLaserRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, LaserRecordID INT, LaserMark VARCHAR(255), Aligner INT, CaseNumber INT, Correct BIT, VerificationID VARCHAR(255), Created DATETIME, Status INT, BagUDID INT);
            UPDATE {database}.dbo.LaserRecords SET Status = 12
            OUTPUT 56, 'LASER RECORD REMOVED', 'Set laser record inactive', GETDATE(), ?,  inserted.ID,inserted.LaserMark, inserted.Aligner, inserted.CaseNumber, inserted.Correct, inserted.VerificationID, inserted.Created, inserted.Status, inserted.BagUDID
            INTO @TempLaserRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LaserRecordID,  LaserMark, Aligner,CaseNumber, Correct, VerificationID, Created, Status, BagUDID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.LaserRecordLogs OUTPUT inserted.ID SELECT * FROM @TempLaserRecordLogs;
        """
 
        ## Shipping

        # # get shipping record Logs by case
        self.get_shipping_record_logs_by_case = "SELECT srl.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.ShippingRecordLogs as srl OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = srl.VerificationID ORDER BY ID DESC) as vel WHERE CaseNumber = ?"

        # # get all shipping records 
        self.get_all_shipping_records = "SELECT sr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.ShippingRecords as sr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = sr.VerificationID ORDER BY ID DESC) as vel"
        
        # # get records by case 
        self.get_shipping_records_by_case = "SELECT sr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.ShippingRecords as sr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = sr.VerificationID ORDER BY ID DESC) as vel WHERE CaseNumber = ?"
        
        # # get records by shipping 
        self.get_shipping_records_by_shipping = "SELECT sr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.ShippingRecords as sr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = sr.VerificationID ORDER BY ID DESC) as vel WHERE ID = ?"

         # # get records by tracking # 
        self.get_shipping_records_by_tracking_number = "SELECT sr.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.ShippingRecords as sr OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = sr.VerificationID ORDER BY ID DESC) as vel WHERE Tracking = ?"

        # # create new shipping record
        # # input: Country, Tracking, CaseNumber, VerificationID
        self.create_shipping_record = """
            DECLARE @TempShippingRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, ShippingRecordID INT, Country VARCHAR(255), Tracking VARCHAR(255), CaseNumber INT, VerificationID VARCHAR(255), Created DATETIME, Status INT);
            INSERT INTO {database}.dbo.ShippingRecords (Country, Tracking, CaseNumber, VerificationID, Created, Status) 
            OUTPUT 53, 'SHIPPING RECORD CREATED', 'New', GETDATE(), inserted.VerificationID, inserted.ID, inserted.Country, inserted.Tracking, inserted.CaseNumber, inserted.VerificationID, inserted.Created, inserted.Status
            INTO @TempShippingRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ShippingRecordID, Country, Tracking, CaseNumber, VerificationID, Created, Status)
            OUTPUT inserted.ID
            VALUES (?, ?, ?, ?, GETDATE(), 11)
            INSERT INTO {database}.dbo.ShippingRecordLogs OUTPUT inserted.ID SELECT * FROM @TempShippingRecordLogs;
        """

        # # update shipping record
        # # input: Country, Tracking, Change, loggedBy, ID
        self.update_shipping_record = """
            DECLARE @TempShippingRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, ShippingRecordID INT, Country VARCHAR(255),Tracking VARCHAR(255), CaseNumber INT, VerificationID VARCHAR(255), Created DATETIME, Status INT);
            UPDATE {database}.dbo.ShippingRecords SET Country = ?, Tracking = ?
            OUTPUT 54, 'SHIPPING RECORD UPDATED', ?, GETDATE(), ?, inserted.ID, inserted.Country, inserted.Tracking, inserted.CaseNumber, inserted.VerificationID, inserted.Created, inserted.Status
            INTO @TempShippingRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ShippingRecordID, Country, Tracking, CaseNumber, VerificationID, Created, Status)
            OUTPUT inserted.ID WHERE ID = ?
            INSERT INTO {database}.dbo.ShippingRecordLogs OUTPUT inserted.ID SELECT * FROM @TempShippingRecordLogs;
        """
        # # set status of record to 12 by shipping ID 
        self.delete_shipping_record_by_shipping = """
            DECLARE @TempShippingRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, ShippingRecordID INT, Country VARCHAR(255),Tracking VARCHAR(255), CaseNumber INT, VerificationID VARCHAR(255), Created DATETIME, Status INT);
            UPDATE {database}.dbo.ShippingRecords SET Status = 12
            OUTPUT 54, 'SHIPPING RECORD REMOVED', 'Set shipping record inactive', GETDATE(), ?, inserted.ID, inserted.Country, inserted.Tracking, inserted.CaseNumber, inserted.VerificationID, inserted.Created, inserted.Status
            INTO @TempShippingRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ShippingRecordID, Country, Tracking, CaseNumber, VerificationID, Created, Status)
            OUTPUT inserted.ID WHERE ID = ?
            INSERT INTO {database}.dbo.ShippingRecordLogs OUTPUT inserted.ID SELECT * FROM @TempShippingRecordLogs;
        """
        # # set status of record to 12 by caseNumber
        self.delete_shipping_record_by_case = """
            DECLARE @TempShippingRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, ShippingRecordID INT, Country VARCHAR(255),Tracking VARCHAR(255), CaseNumber INT, VerificationID VARCHAR(255), Created DATETIME, Status INT);
            UPDATE {database}.dbo.ShippingRecords SET Status = 12
            OUTPUT 54, 'SHIPPING RECORD REMOVED', 'Set shipping record inactive', GETDATE(), ?, inserted.ID, inserted.Country, inserted.Tracking, inserted.CaseNumber, inserted.VerificationID, inserted.Created, inserted.Status
            INTO @TempShippingRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ShippingRecordID, Country, Tracking, CaseNumber, VerificationID, Created, Status)
            OUTPUT inserted.ID WHERE CaseNumber = ?
            INSERT INTO {database}.dbo.ShippingRecordLogs OUTPUT inserted.ID SELECT * FROM @TempShippingRecordLogs;
        """
        # fmt: on

        # # get laser record Logs by case
        self.get_bag_record_logs_by_case = "SELECT brl.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.BagRecordLogs as brl OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = brl.VerificationID ORDER BY ID DESC) as vel WHERE CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)"

        # # get all laser records
        self.get_all_bag_records = "SELECT br.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.BagRecords as br OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = br.VerificationID ORDER BY ID DESC) as vel"

        # # get records by case
        self.get_bag_records_by_case = "SELECT br.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.BagRecords as br OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = br.VerificationID ORDER BY ID DESC) as vel WHERE CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)"

        # # get records by id
        self.get_bag_records_by_bag = "SELECT br.*, vel.EmployeeID as CreatedBy FROM {database}.dbo.BagRecords as br OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = br.VerificationID ORDER BY ID DESC) as vel WHERE ID = ?"

        # # create new laser record
        # # input: LaserMark, Aligner, CaseNumber, VerificationID
        self.create_bag_record = """
            DECLARE @TempBagRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, BagRecordID INT, BagUDID INT, Barcode VARCHAR(150), Created DATETIME, VerificationID INT, Status INT, CaseID VARCHAR(36));
            INSERT INTO {database}.dbo.BagRecords (BagUDID, Barcode, Created, VerificationID, Status, CaseID)
            OUTPUT 64, 'BAG RECORD CREATED', 'New', GETDATE(), inserted.VerificationID, inserted.ID, inserted.BagUDID, inserted.Barcode, inserted.Created, inserted.VerificationID, inserted.Status, inserted.CaseID
            INTO @TempBagRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, BagRecordID, BagUDID, Barcode, Created, VerificationID, Status, CaseID)
            OUTPUT inserted.ID
            VALUES (?, ?, GETDATE(), ?, 11, ?)
            INSERT INTO {database}.dbo.BagRecordLogs OUTPUT inserted.ID SELECT * FROM @TempBagRecordLogs;
        """

        # # update laser record
        # # input: LaserMark, Aligner, Change, updateBy, ID
        self.update_bag_record = """
            DECLARE @TempBagRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, BagRecordID INT, BagUDID INT, Barcode VARCHAR(150), Created DATETIME, VerificationID INT, Status INT, CaseID VARCHAR(36));
            UPDATE {database}.dbo.BagRecords SET BagUDID = ?, Barcode = ?, CaseID = ?
            OUTPUT 65, 'BAG RECORD UPDATED', ?, GETDATE(), ?,  inserted.ID, inserted.BagUDID, inserted.Barcode, inserted.Created, inserted.VerificationID, inserted.Status, inserted.CaseID
            INTO @TempBagRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, BagRecordID, BagUDID, Barcode, Created, VerificationID, Status, CaseID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.BagRecordLogs OUTPUT inserted.ID SELECT * FROM @TempBagRecordLogs;
        """

        # # set status of all records for the given case to 12
        self.delete_bag_record_by_case = """
            DECLARE @TempBagRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, BagRecordID INT, BagUDID INT, Barcode VARCHAR(150), Created DATETIME, VerificationID INT, Status INT, CaseID VARCHAR(36));
            UPDATE {database}.dbo.BagRecords SET Status = 12
            OUTPUT 65, 'BAG RECORD REMOVED', 'Set bag record inactive', GETDATE(), ?,  inserted.ID, inserted.BagUDID, inserted.Barcode, inserted.Created, inserted.VerificationID, inserted.Status, inserted.CaseID
            INTO @TempBagRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, BagRecordID, BagUDID, Barcode, Created, VerificationID, Status, CaseID)
            OUTPUT inserted.ID
            WHERE CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?);
            INSERT INTO {database}.dbo.BagRecordLogs OUTPUT inserted.ID SELECT * FROM @TempBagRecordLogs;
        """

        # # set status of the given record id to 12
        self.delete_bag_record_by_bag_record = """
            DECLARE @TempBagRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, BagRecordID INT, BagUDID INT, Barcode VARCHAR(150), Created DATETIME, VerificationID INT, Status INT, CaseID VARCHAR(36));
            UPDATE {database}.dbo.BagRecords SET Status = 12
            OUTPUT 65, 'BAG RECORD REMOVED', 'Set bag record inactive', GETDATE(), ?,  inserted.ID, inserted.BagUDID, inserted.Barcode, inserted.Created, inserted.VerificationID, inserted.Status, inserted.CaseID
            INTO @TempBagRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, BagRecordID, BagUDID, Barcode, Created, VerificationID, Status, CaseID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.BagRecordLogs OUTPUT inserted.ID SELECT * FROM @TempBagRecordLogs;
        """

        ## Waste

        self.get_all_waste_records = "SELECT WasteRecords.*, WasteTypes.Name, WasteTypes.SI FROM {database}.dbo.WasteRecords LEFT JOIN {database}.dbo.WasteTypes on WasteRecords.WasteTypeID = WasteTypes.ID ORDER BY WasteRecords.Created DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        self.get_waste_record_by_waste = "SELECT WasteRecords.*, WasteTypes.Name, WasteTypes.SI FROM {database}.dbo.WasteRecords LEFT JOIN {database}.dbo.WasteTypes on WasteRecords.WasteTypeID = WasteTypes.ID WHERE WasteRecords.ID = ?"
        self.insert_waste_record = """
            DECLARE @TempWasteRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, WasteRecordID INT, Value FLOAT, WasteTypeID INT, Created DATETIME, VerificationID INT, Status INT, LocationID INT);
            INSERT INTO {database}.dbo.WasteRecords (Value, WasteTypeID, Created, VerificationID, Status, LocationID)
            OUTPUT 62, 'WASTE RECORD CREATED', 'New', GETDATE(), inserted.VerificationID, inserted.ID, inserted.Value, inserted.WasteTypeID, inserted.Created, inserted.VerificationID, inserted.Status, inserted.LocationID
            INTO @TempWasteRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, WasteRecordID, Value, WasteTypeID, Created, VerificationID, Status, LocationID)
            OUTPUT inserted.ID
            VALUES (?, ?, GETDATE(), ?, 11, ?)
            INSERT INTO {database}.dbo.WasteRecordLogs OUTPUT inserted.ID SELECT * FROM @TempWasteRecordLogs;
        """
        self.update_waste_record_by_waste_record = """
            DECLARE @TempWasteRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, WasteRecordID INT, Value FLOAT, WasteTypeID INT, Created DATETIME, VerificationID INT, Status INT, LocationID INT);
            UPDATE {database}.dbo.WasteRecords SET Value = ?, WasteTypeID = ?, LocationID = ?
            OUTPUT 63, 'WASTE RECORD UPDATED', ?, GETDATE(), ?, inserted.ID, inserted.Value, inserted.WasteTypeID, inserted.Created, inserted.VerificationID, inserted.Status, inserted.LocationID
            INTO @TempWasteRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, WasteRecordID, Value, WasteTypeID, Created, VerificationID, Status, LocationID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.WasteRecordLogs OUTPUT inserted.ID SELECT * FROM @TempWasteRecordLogs;
        """
        self.delete_waste_record_by_waste_record = """
            DECLARE @TempWasteRecordLogs TABLE (LogTypeID INT, Change VARCHAR(255), LogNote VARCHAR(255), Logged DATETIME, LoggedVerificationID INT, WasteRecordID INT, Value FLOAT, WasteTypeID INT, Created DATETIME, VerificationID INT, Status INT, LocationID INT);
            UPDATE {database}.dbo.WasteRecords SET Status = 12
            OUTPUT 63, 'WASTE RECORD UPDATED', 'Removed', GETDATE(), ?, inserted.ID, inserted.Value, inserted.WasteTypeID, inserted.Created, inserted.VerificationID, inserted.Status, inserted.LocationID
            INTO @TempWasteRecordLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, WasteRecordID, Value, WasteTypeID, Created, VerificationID, Status, LocationID)
            OUTPUT inserted.ID
            WHERE ID = ?;
            INSERT INTO {database}.dbo.WasteRecordLogs OUTPUT inserted.ID SELECT * FROM @TempWasteRecordLogs;
        """
        self.get_all_waste_types = "SELECT * FROM {database}.dbo.WasteTypes"
        self.insert_waste_type = "INSERT INTO {database}.dbo.WasteTypes (Name, SI, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        self.update_waste_type_by_waste_type = "UPDATE {database}.dbo.WasteTypes SET Name = ?, SI = ? OUTPUT Inserted.ID WHERE ID = ?"
