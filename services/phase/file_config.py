from .config import Config
from .sql_config import SQLConfig


class FileConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Get All Files
        self.get_files = "SELECT * FROM {database}.dbo.Files"

        # # Get File by ID
        self.get_file_by_id = "SELECT * FROM {database}.dbo.Files WHERE ID = ?"

        # # Get Files by BulletinID
        self.get_file_by_bulletin_id = "SELECT * FROM {database}.dbo.Files f LEFT JOIN {database}.dbo.BulletinFileLinks dfl ON dfl.FileID = f.ID WHERE dfl.BulletinID = ? AND Status = 11"

        # # Get Files by TypeID
        self.get_file_by_type_id = "SELECT * FROM {database}.dbo.Files WHERE FileTypeID IN (SELECT VALUE FROM STRING_SPLIT(?,','))  ORDER BY ID DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"

        # # Get Files by BatchID
        self.get_file_by_storage_batch_id = "SELECT fileTable.*, batchTable.ID as BatchID, batchFileLinkTable.ID as BatchFileLinkID FROM {database}.[dbo].[Files] fileTable LEFT JOIN {database}.[dbo].StockStorageBatchFileLinks batchFileLinkTable ON batchFileLinkTable.FileID = fileTable.ID LEFT JOIN {database}.[dbo].StockStorageBatch batchTable ON batchTable.ID = batchFileLinkTable.StockStorageBatchID WHERE batchTable.ID = ?"

        # # Create New Files
        self.create_files = "INSERT INTO {database}.dbo.Files (Path, FileTypeID, Created, VerificationID) OUTPUT inserted.ID AS FileID, inserted.Path, inserted.FileTypeID VALUES "
