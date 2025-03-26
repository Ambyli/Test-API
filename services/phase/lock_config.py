from .config import Config
from .sql_config import SQLConfig


# locking config
class LockConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # lock queries
        self.get_lock_types = "SELECT ID, [Type] FROM {database}.dbo.LockTypes"
        self.get_lock_queue_by_type = "SELECT TOP 100 ID, Description, LockType, Status, Created, VerificationID FROM {database}.dbo.LockQueue WHERE LockType = ? and Status = 11 ORDER BY Created ASC"
        self.get_lock_by_id = "SELECT ID, Description, LockType, Status, Created, VerificationID FROM {database}.dbo.LockQueue WHERE ID = ?"
        self.insert_lock = "INSERT INTO {database}.dbo.LockQueue (Description, LockType, Status, Created, VerificationID) OUTPUT Inserted.ID VALUES (?, ?, 11, GETDATE(), ?)"
        self.disable_lock_by_id = "UPDATE {database}.dbo.LockQueue SET Status = 12, Disabled = GETDATE(), DisabledVerificationID = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.insert_lock_log = "INSERT INTO {database}.dbo.LockQueueLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LockID, Description, LockType, Status, Created, VerificationID, Disabled, DisabledVerificationID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 Description FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 LockType FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 Status FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 Disabled FROM {database}.dbo.LockQueue WHERE ID = ?), (SELECT TOP 1 DisabledVerificationID FROM {database}.dbo.LockQueue WHERE ID = ?))"
