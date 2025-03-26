from .config import Config
from .sql_config import SQLConfig


# lot config
class LotConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Lot Functions
        self.insert_plastic_sag = "INSERT INTO {database}.dbo.PlasticSag (plasticID, SpotCoverage, SpotAverage, SpotCount, DateIn, VerificationID, ThermCode, TestDiameter, Type, Status, MachineID) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, 11, ?)"
        self.get_plastic_sag_by_plastic = "SELECT ID as plasticSagID, plasticID, SpotCoverage, SpotAverage, SpotCount, DateIn, VerificationID, ThermCode, TestDiameter, Type, Status, MachineID FROM {database}.dbo.PlasticSag WHERE plasticID = ? ORDER BY DateIn DESC"
        self.insert_plastic = "INSERT INTO {database}.dbo.Plastics (Description, Datein, CheckInVerificationID, plasticLotNumber, MaterialID, SecondaryID, ExpirationDate, Amount, Status, Reference, plasticNumber, Type) OUTPUT Inserted.plasticID VALUES (?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self.update_plastic = "UPDATE {database}.dbo.Plastics SET Description = ?, PlasticLotNumber = ?, SecondaryID = ?, Amount = ?, Reference = ?, PlasticNumber = ? OUTPUT Inserted.plasticID WHERE PlasticID = ?"
        self.update_plastic_status = "UPDATE {database}.dbo.Plastics SET Status = ? OUTPUT Inserted.plasticID WHERE plasticID = ?"
        self.update_plastic_amount = "UPDATE {database}.dbo.Plastics SET Amount = ? OUTPUT Inserted.plasticID WHERE plasticID = ?"
        self.insert_plastic_repair = "INSERT INTO {database}.dbo.PlasticRepair (plasticID, RepairTime, DateIn, CheckInVerificationID) OUTPUT Inserted.RepairID VALUES (?, ?, GETDATE(), ?)"
        self.get_repair_by_plastic = "SELECT RepairID, RepairTime, DateIn, CheckInVerificationID FROM {database}.dbo.PlasticRepair WHERE plasticID = ? ORDER BY DateIn DESC"
        self.get_repair_by_yield = "SELECT RepairID, RepairTime, DateIn, CheckInVerificationID FROM {database}.dbo.YieldRepair WHERE yieldID = ? ORDER BY DateIn DESC"
        self.insert_plastic_batch = "INSERT INTO {database}.dbo.PlasticBatch (Count, Created, CreatedBy) OUTPUT Inserted.ID VALUES(?, GETDATE(), ?)"
        self.insert_plastic_batch_link = "INSERT INTO {database}.dbo.PlasticBatchLinks (plasticID, plasticBatchID, Created, CreatedBy, Status) OUTPUT Inserted.ID VALUES(?, ?, GETDATE(), ?, 11)"
        self.get_all_plastics = "SELECT a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = a.MaterialID) as Type, a.Description, a.Datein, a.Dateout, a.CheckInVerificationID, a.CheckoutVerificationID, a.plasticLotNumber, a.MaterialID, a.SecondaryID, a.ExpirationDate, a.Amount, a.Status, a.Reference, a.plasticNumber, a.Type FROM {database}.dbo.Plastics as a ORDER BY a.Datein DESC"
        self.get_all_plastics_by_batch = "SELECT b.plasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, b.Description, b.Datein, b.Dateout, b.CheckInVerificationID, b.CheckoutVerificationID, b.plasticLotNumber, b.MaterialID, b.SecondaryID, b.ExpirationDate, b.Amount, b.Status, b.Type FROM {database}.dbo.PlasticBatchLinks as a, {database}.dbo.Plastics as b where a.PlasticID = b.plasticID and a.plasticBatchID = ?"
        self.get_plastics_by_ID = "SELECT a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = a.MaterialID) as Type, a.Description, a.Datein, a.Dateout, a.CheckInVerificationID, a.CheckoutVerificationID, a.plasticLotNumber, a.MaterialID, a.SecondaryID, a.ExpirationDate, a.Amount, a.Status, a.Reference, a.plasticNumber, a.Type FROM {database}.dbo.Plastics as a WHERE a.PlasticID = ? or a.SecondaryID = ? ORDER BY a.Datein DESC"
        self.get_all_repair_plastics = "SELECT a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = a.MaterialID) as Type, a.Description, a.Datein, a.Dateout, a.CheckInVerificationID, a.CheckoutVerificationID, a.PlasticLotNumber, a.MaterialID, a.SecondaryID, a.ExpirationDate, a.Amount, a.Status, a.Reference, a.PlasticNumber FROM {database}.dbo.Plastics as a WHERE a.Status = 8 ORDER BY a.Datein DESC"
        self.get_all_repair_yields = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.Status = 8 ORDER BY a.Datein DESC"
        self.checkout_plastic = "UPDATE {database}.dbo.Plastics SET Dateout = GETDATE(), CheckoutVerificationID = ? OUTPUT Inserted.plasticID WHERE plasticID = ?"
        self.insert_plastic_log = "INSERT INTO {database}.dbo.PlasticLog (plasticID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, plasticLotNumber, MaterialID, SecondaryID, ExpirationDate, Amount, Status, Reference, plasticNumber, Type) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, (SELECT TOP 1 plasticLotNumber FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT TOP 1 MaterialID FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT TOP 1 SecondaryID FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT TOP 1 ExpirationDate FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT TOP 1 Amount FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT Reference FROM {database}.dbo.Plastics WHERE plasticID = ?), (SELECT plasticNumber FROM {database}.dbo.Plastics WHERE plasticID = ?),(SELECT Type FROM {database}.dbo.Plastics WHERE plasticID = ?))"
        self.insert_yield_sag = "INSERT INTO {database}.dbo.YieldSag (YieldID, SpotCoverage, SpotAverage, SpotCount, DateIn, VerificationID, ThermCode, TestDiameter, Type, Status, MachineID) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, 11, ?)"
        self.get_yield_sag_by_yield = "SELECT ID as YieldSagID, YieldID, SpotCoverage, SpotAverage, SpotCount, DateIn, VerificationID, ThermCode, TestDiameter, Type, Status, MachineID FROM {database}.dbo.YieldSag WHERE YieldID = ? ORDER BY DateIn DESC"
        self.insert_yield = "INSERT INTO {database}.dbo.Yields (plasticID, DateIn, CheckInVerificationID, Length, Total, Quantity, Status) OUTPUT Inserted.YieldID VALUES(?, GETDATE(), ?, ?, ?, ?, ?)"
        self.insert_yield_waste_link = "INSERT INTO {database}.dbo.YieldWasteRecordLinks (YieldID, WasteRecordID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        self.update_yield_status = "UPDATE {database}.dbo.Yields SET Status = ? OUTPUT Inserted.YieldID WHERE YieldID = ?"
        self.update_yield_quantity = "UPDATE {database}.dbo.Yields SET Quantity = ? OUTPUT Inserted.YieldID WHERE YieldID = ?"
        self.insert_yield_repair = "INSERT INTO {database}.dbo.YieldRepair (YieldID, RepairTime, DateIn, CheckInVerificationID) OUTPUT Inserted.RepairID VALUES (?, ?, GETDATE(), ?)"
        self.get_all_yields = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.PlasticID = b.plasticID ORDER BY a.Datein DESC"
        self.get_all_yields_by_plastic = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.PlasticID = b.plasticID and a.PlasticID = ? ORDER BY a.Datein DESC"
        self.get_yields_by_ID = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.PlasticID = b.plasticID and a.YieldID = ? ORDER BY a.Datein DESC"
        self.get_yields_by_status = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.PlasticID = b.plasticID and a.Status in (SELECT value FROM STRING_SPLIT(?, ',')) ORDER BY a.Datein DESC"
        self.get_yield_quantity = "SELECT Length, Total, Quantity FROM {database}.dbo.Yields WHERE YieldID = ?"
        self.checkout_yield = "UPDATE {database}.dbo.Yields SET DateOut = GETDATE(), CheckOutVerificationID = ? OUTPUT Inserted.YieldID WHERE YieldID = ?"
        self.insert_yield_log = "INSERT INTO {database}.dbo.YieldLog (YieldID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, plasticID, Length, Total, Quantity, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, (SELECT TOP 1 plasticID FROM {database}.dbo.Yields WHERE YieldID = ?), (SELECT TOP 1 Length FROM {database}.dbo.Yields WHERE YieldID = ?), (SELECT TOP 1 Total FROM {database}.dbo.Yields WHERE YieldID = ?), (SELECT TOP 1 Quantity FROM {database}.dbo.Yields WHERE YieldID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Yields WHERE YieldID = ?))"
        self.insert_bin = "INSERT INTO {database}.dbo.Bins (Description, Datein, VerificationID, Type, Status) OUTPUT Inserted.BinID VALUES (?, GETDATE(), ?, ?, ?)"
        self.get_bins_by_status = "SELECT BinID, Description, Datein, VerificationID, Type, Status FROM {database}.dbo.Bins WHERE Status = ? ORDER BY Datein DESC"
        self.update_bin_status = "UPDATE {database}.dbo.Bins SET Status = ? OUTPUT Inserted.BinID WHERE BinID = ?"
        self.get_all_bins = "SELECT BinID, Description, Datein, VerificationID, Type, Status FROM {database}.dbo.Bins ORDER BY Datein DESC"
        self.get_plastics_by_status = "SELECT * FROM {database}.dbo.Plastics WHERE Status in (SELECT VALUE FROM STRING_SPLIT(?, ',')) ORDER BY Datein DESC"
        self.get_bins_by_ID = "SELECT BinID, Description, Datein, VerificationID, Type, Status FROM {database}.dbo.Bins WHERE BinID = ? ORDER BY Datein DESC"
        self.insert_bin_log = "INSERT INTO {database}.dbo.BinLog (BinID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, Description, Datein, VerificationID, Type, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, (SELECT TOP 1 Description FROM {database}.dbo.Bins WHERE BinID = ?), (SELECT TOP 1 Datein FROM {database}.dbo.Bins WHERE BinID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Bins WHERE BinID = ?), (SELECT TOP 1 Type FROM {database}.dbo.Bins WHERE BinID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Bins WHERE BinID = ?))"
        self.insert_lot = "INSERT INTO {database}.dbo.Lots (YieldID, BinID, Description, Datein, CheckInVerificationID, Status) OUTPUT Inserted.LotID VALUES (?, ?, ?, GETDATE(), ?, ?)"
        self.update_lot_status = "UPDATE {database}.dbo.Lots SET Status = ? OUTPUT Inserted.LotID WHERE LotID = ?"
        self.update_lot_bin = "UPDATE {database}.dbo.Lots SET BinID = ? OUTPUT Inserted.LotID WHERE LotID = ?"
        self.update_lot_yield = "UPDATE {database}.dbo.Lots SET YieldID = ? OUTPUT Inserted.LotID WHERE LotID = ?"
        self.lots_primer = """
            SELECT 
            PlasticsTable.PlasticID, 
            PlasticsTable.Reference, 
            PlasticsTable.PlasticNumber, 
            PlasticsTable.Type as TypeID, 
            PlasticTypesTable.Description as TypeName,
            YieldRepairTable.Datein as BakeIn,
            YieldRepairTable.RepairTime as BakeTime,
            PlasticsTable.Description, 
            PlasticsTable.PlasticLotNumber, 
            PlasticsTable.SecondaryID, 
            PlasticsTable.Amount, 
            PlasticsTable.MaterialID, 
            PlasticsTable.ExpirationDate,
            MaterialsTable.Type as MaterialType, 
            LotsTable.*, 
            CheckInVerification.EmployeeID as CheckIn,
            CheckOutVerification.EmployeeID as CheckOut,
            PlasticSagTable.ID as PlasticSagID, 
            statusTable.StatusType, 
            YieldsTable.Length as YieldLength, 
            YieldsTable.Total as YieldTotal, 
            YieldsTable.Quantity as YieldQuantity, 
            (TRIM(employeeTable_checkin.FirstName) + ' ' + TRIM(employeeTable_checkin.LastName)) as CheckinEmployee, 
            (TRIM(employeeTable_checkout.FirstName) + ' ' + TRIM(employeeTable_checkout.LastName)) as CheckoutEmployee
            FROM {database}.dbo.Lots as LotsTable 
            LEFT JOIN {database}.dbo.Yields as YieldsTable ON YieldsTable.YieldID = LotsTable.YieldID
            LEFT JOIN (SELECT * FROM {database}.dbo.YieldRepair WHERE RepairID in (SELECT MAX(RepairID) FROM {database}.dbo.YieldRepair GROUP BY YieldID)) as YieldRepairTable ON YieldRepairTable.YieldID = YieldsTable.YieldID
            LEFT JOIN {database}.dbo.Bins as BinsTable ON BinsTable.BinID = LotsTable.BinID
            LEFT JOIN {database}.dbo.Plastics as PlasticsTable ON PlasticsTable.PlasticID = YieldsTable.PlasticID
            LEFT JOIN {database}.dbo.Materials as MaterialsTable ON MaterialsTable.MaterialID = PlasticsTable.MaterialID
            LEFT JOIN {database}.dbo.PlasticTypes as PlasticTypesTable on PlasticTypesTable.ID = PlasticsTable.Type
            LEFT JOIN {database}.dbo.Status as statusTable ON statusTable.ID = LotsTable.Status
            LEFT JOIN (SELECT * FROM {database}.dbo.PlasticSag WHERE ID in (SELECT MAX(ID) FROM {database}.dbo.PlasticSag GROUP BY PlasticID)) as PlasticSagTable ON PlasticSagTable.PlasticID = PlasticsTable.PlasticID
            OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = LotsTable.CheckInVerificationID) as CheckInVerification
			OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = LotsTable.CheckOutVerificationID) as CheckOutVerification
			LEFT JOIN {database}.dbo.Employees as employeeTable_checkin ON employeeTable_checkin.EmployeeID = CheckInVerification.EmployeeID
            LEFT JOIN {database}.dbo.Employees as employeeTable_checkout ON employeeTable_checkout.EmployeeID = CheckOutVerification.EmployeeID
        """
        self.get_all_lots = (
            self.lots_primer
            + """
            ORDER BY LotsTable.Datein DESC
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
            """
        )
        self.get_lots_by_status = (
            self.lots_primer
            + """
            WHERE 
            LotsTable.Status in (SELECT VALUE FROM STRING_SPLIT(?, ','))
            ORDER BY LotsTable.Datein DESC
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
            """
        )
        self.get_lots_by_bin = (
            self.lots_primer
            + """
            WHERE
            LotsTable.BinID = ?
            ORDER BY LotsTable.Datein DESC
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
            """
        )
        self.get_lots_by_yield = (
            self.lots_primer
            + """
            WHERE
            LotsTable.YieldID = ?
            ORDER BY LotsTable.Datein DESC
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
            """
        )
        self.get_lots_by_ID = "SELECT a.LotID, a.YieldID, a.BinID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = c.MaterialID) as Type, a.Description, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Status, b.Quantity FROM {database}.dbo.Lots as a, {database}.dbo.Yields as b, {database}.dbo.Plastics as c WHERE a.YieldID = b.YieldID and b.plasticID = c.plasticID and a.LotID = ? ORDER BY a.Datein DESC"
        self.get_lot_bin = "SELECT BinID, Description, Datein, VerificationID, Type, Status FROM {database}.dbo.Bins WHERE BinID = (SELECT BinID FROM {database}.dbo.Lots WHERE LotID = ?)"
        self.get_lot_yield = "SELECT a.YieldID, a.PlasticID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = b.MaterialID) as Type, a.DateIn, a.DateOut, a.CheckInVerificationID, a.CheckOutVerificationID, a.Length, a.Total, a.Quantity, a.Status FROM {database}.dbo.Yields as a, {database}.dbo.Plastics as b WHERE a.PlasticID = b.plasticID and a.YieldID = (SELECT YieldID FROM {database}.dbo.Lots WHERE LotID = ?)"
        self.insert_material = "INSERT INTO {database}.dbo.Materials (BrandID, Type, Description, SKU, VerificationID) OUTPUT Inserted.MaterialID VALUES (?, ?, ?, ?, ?)"
        self.checkout_lot = "UPDATE {database}.dbo.Lots SET Dateout = GETDATE(), CheckoutVerificationID = ? OUTPUT Inserted.LotID WHERE LotID = ?"
        self.insert_lot_log = "INSERT INTO {database}.dbo.LotLog (LotID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, YieldID, BinID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, (SELECT YieldID FROM {database}.dbo.Lots WHERE LotID = ?), (SELECT BinID FROM {database}.dbo.Lots WHERE LotID = ?), (SELECT Status FROM {database}.dbo.Lots WHERE LotID = ?))"
        self.get_all_lots_by_production_line = "SELECT a.LotID, a.YieldID, a.BinID, (SELECT Type FROM {database}.dbo.Materials WHERE MaterialID = c.MaterialID) as Type, a.Description, a.ProductionLineID, a.DateIn, a.DateOut, a.CheckIn, a.CheckOut, a.Status, b.Quantity FROM {database}.dbo.Lots as a, {database}.dbo.Yields as b, {database}.dbo.Plastics as c WHERE a.YieldID = b.YieldID and b.plasticID = c.plasticID and a.ProductionLineID = ? ORDER BY a.Datein DESC"
        self.update_production_line_of_lot = "UPDATE {database}.dbo.Lots SET ProductionLineID = ? OUTPUT Inserted.LotID WHERE LotID = ?"
