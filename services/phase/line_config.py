from .config import Config
from .sql_config import SQLConfig


# line config
class LineConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        self.get_all_lines = "SELECT lineTable.*, ownerTable.Name as OwnerName  FROM {database}.dbo.Lines lineTable LEFT JOIN {database}.dbo.OwnerLineLinks linkTable ON linkTable.LineID = lineTable.ID LEFT JOIN {database}.dbo.Employees ownerTable ON ownerTable.ID = linkTable.OwnerID WHERE lineTable.Status = 11"
        self.get_line_by_line_id = (
            "SELECT * FROM {database}.dbo.Lines WHERE ID = ? AND Status = 11"
        )
        self.get_lines_by_owner_id = "SELECT lineTable.* FROM {database}.dbo.Lines lineTable LEFT JOIN {database}.dbo.OwnerLineLinks ownerLineLinksTable ON lineTable.ID = ownerLineLinksTable.LineID WHERE ownerLineLinksTable.OwnerID = ? AND ownerLineLinksTable.Status = 11 AND lineTable.Status = 11"
        self.insert_line = "INSERT INTO {database}.dbo.Lines (Name, Description, Status, Created) OUTPUT Inserted.ID VALUES (?, ?, 11, GETDATE())"
        self.update_line = "UPDATE {database}.dbo.Lines Set Name = ?, Description = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_line_status = (
            "UPDATE {database}.dbo.Lines Set Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        )
