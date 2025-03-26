from .config import Config
from .sql_config import SQLConfig


# carbon config
class CarbonConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        self.Printers = {
            "5D00GJ": "alpha",
            "5D00GV": "bravo",
            "7C00WU": "charlie",
            "7G0092": "delta",
        }
        # input: qty of plates
        # output: [{ID, PlateID, Created, VerificationID, Status}]
        self.get_carbon_plate_history = "SELECT TOP (?) ID, PlateID, Created, VerificationID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = PlateLogTable.VerificationID) as CreatedBy, Status FROM {database}.dbo.CarbonPlateLogs PlateLogTable WHERE status = 11 ORDER BY Created DESC"
        # input: qty of plates
        # output: [{ID, PlateID, Created, VerificationID, Status}]
        self.create_carbon_plate_history = "INSERT INTO {database}.dbo.CarbonPlateLogs (PlateID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, GETDATE(), ?, 11)"
