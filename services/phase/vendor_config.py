from .config import Config
from .sql_config import SQLConfig


# vendor config
class VendorConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        self.get_all_vendors = "SELECT * FROM {database}.dbo.Vendors"
        self.insert_vendor = "INSERT INTO {database}.dbo.Vendors (VendorID, Vendor, Address) OUTPUT Inserted.VendorID VALUES (?, ?, ?)"
