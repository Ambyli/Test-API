from .config import Config
from .sql_config import SQLConfig


# gauge config
class GaugeConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Gauge functions
        self.get_gauge_by_ID = "SELECT ID, Title, Label, Limit, [Index], Length, Constant, Percentage, Status, Created, VerificationID, LockID FROM {database}.dbo.Gauges WHERE ID = ? ORDER BY Created DESC"
        self.insert_gauge = "INSERT INTO {database}.dbo.Gauges (Title, Label, Limit, [Index], Length, Constant, Percentage, Status, Created, VerificationID) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)"
        self.insert_gauge_with_lock = "INSERT INTO {database}.dbo.Gauges (Title, Label, Limit, [Index], Length, Constant, Percentage, Status, Created, VerificationID, LockID) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?)"
        self.update_gauge_values = "UPDATE {database}.dbo.Gauges SET Title = ?, Label = ?, Limit = ?, [Index] = ?, Length = ?, Constant = ?, Percentage = ?, Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.insert_gauge_log = "INSERT INTO {database}.dbo.GaugeLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, GaugeID, Title, [Label], Limit, [Index], [Length], Constant, [Percentage], [Status], Created, VerificationID, LockID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 Title FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 [Label] FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 Limit FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 [Index] FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 [Length] FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 Constant FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 [Percentage] FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 [Status] FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Gauges WHERE ID = ?), (SELECT TOP 1 LockID FROM {database}.dbo.Gauges WHERE ID = ?))"
