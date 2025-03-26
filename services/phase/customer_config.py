from .config import Config
from .sql_config import SQLConfig


# customer config
class CustomerConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        self.get_customers = """
            SELECT
            Customers.CustomerID,
            Customers.PracticeName,
            Customers.Address1,
            Customers.City,
            Customers.State,
            Customers.ZipCode,
            Customers.Country,
            Customers.Email,
            Customers.SalesPerson,
            Customers.BillAddress1,
            Customers.BillCity,
            Customers.BillState,
            Customers.BillZipCode,
            Customers.BillCountry,
            Customers.LabName,
            LabCustomerSettings.Catalog,
            Customers.CreatedBy,
            Customers.CreateDate,
            Customers.ModifiedBy,
            Customers.ModifyDate,
            Customers.BillEmail
            FROM
            {database}.dbo.Customers
            left join
            {database}.dbo.LabCustomerSettings
            on
            Customers.CustomerID = LabCustomerSettings.CustomerID
            WHERE
            Active = 1
            and
            Deleted = 0
        """
        self.get_customer_by_ID = """
            SELECT
            Customers.CustomerID,
            Customers.PracticeName,
            Customers.Address1,
            Customers.City,
            Customers.State,
            Customers.ZipCode,
            Customers.Country,
            Customers.Email,
            Customers.SalesPerson,
            Customers.BillAddress1,
            Customers.BillCity,
            Customers.BillState,
            Customers.BillZipCode,
            Customers.BillCountry,
            Customers.LabName,
            LabCustomerSettings.Catalog,
            Customers.CreatedBy,
            Customers.CreateDate,
            Customers.ModifiedBy,
            Customers.ModifyDate, 
            Customers.BillEmail
            FROM
            {database}.dbo.Customers
            left join
            {database}.dbo.LabCustomerSettings
            on
            Customers.CustomerID = LabCustomerSettings.CustomerID
            WHERE
            Customers.CustomerID = ?
        """
        self.get_customer_account_by_ID = "SELECT ID, CustomerID, AccountID, DateIn, DateOut FROM {database}.dbo.CustomerAccounts WHERE CustomerID = ?"
        self.get_customer_catalog_by_ID = "SELECT Catalog FROM {database}.dbo.LabCustomerSettings WHERE CustomerID = ?"
        self.insert_customeraccount = "INSERT INTO {database}.dbo.CustomerAccounts (CustomerID, AccountID, DateIn) OUTPUT Inserted.ID VALUES (?, ?, GETDATE())"
