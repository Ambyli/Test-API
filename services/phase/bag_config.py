from .config import Config
from .sql_config import SQLConfig


# bag config
class BagConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # input: PatientName, DoctorName, LegibleStep, Steps, GTIN, LotNumber, SerialNumber, Barcode, MDate, EDate, VerificationID
        # output: [[BagUDID]]
        self.insert_Bag_UDID = "INSERT INTO {database}.dbo.Bags (PatientName, DoctorName, LegibleStep, Steps, GTIN, LotNumber, SerialNumber, Barcode, MDate, EDate, Created, VerificationID, Status, MachineID, StationID) OUTPUT Inserted.BagUDID VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, 11, ?, ?)"
        # input: BagUDID, AlignerID
        # output: [[LinkID]]
        self.insert_Bag_Link = "INSERT INTO {database}.dbo.AlignerBagLinks (BagUDID, AlignerID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        # input: LinkID
        # output: [[BagUDID]]
        self.get_Bags_by_Link = "SELECT BagUDID, PatientName, DoctorName, LegibleStep, Steps, GTIN, LotNumber, SerialNumber, Barcode, MDate, EDate, Created, VerificationID FROM {database}.dbo.Bags WHERE BagUDID = (SELECT BagUDID FROM {database}.dbo.AlignerBagLinks WHERE ID = ?)"
        # input: AlignerID
        # output: [[LinkID]]
        self.get_BagLinks_by_aligner = "SELECT ID as LinkID FROM {database}.dbo.AlignerBagLinks WHERE AlignerID = ? and Status = 11 ORDER BY ID DESC"
        # input: BagUDID
        # output: [[BagUDID]]
        self.get_Bag_by_UDID = "SELECT BagUDID, PatientName, DoctorName, LegibleStep, Steps, GTIN, LotNumber, SerialNumber, Barcode, MDate, EDate, Created, VerificationID FROM {database}.dbo.Bags WHERE BagUDID = ?"
