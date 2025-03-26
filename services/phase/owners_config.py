from .config import Config
from .sql_config import SQLConfig


# owner config
class OwnerConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        self.get_all_owners = """
            SELECT sqlTable.ID, tokenTable.ID as TokenID, tokenTable.Token, empTable.* 
            FROM {database}.dbo.SqlAccounts sqlTable
            LEFT JOIN {database}.dbo.Tokens tokenTable ON tokenTable.ID = sqlTable.TokenID
            LEFT JOIN {database}.dbo.VerificationEmployeeLinks velTable ON velTable.VerificationID = sqlTable.OwnerVerificationID
            LEFT JOIN {database}.dbo.Employees empTable ON empTable.EmployeeID = velTable.EmployeeID
            WHERE sqlTable.Status = 2 AND velTable.Status = 11 AND empTable.Status = 11
            ORDER BY FirstName ASC
         """
        self.get_owner_employee_links_by_owner_id = """
            SELECT linkTable.ID as LinkID, ownerTable.ID as OwnerID, ownerTable.Name as OwnerName, trim(empTable.FirstName) as FirstName, trim(empTable.LastName) as LastName, empTable.EmployeeID
            FROM {database}.dbo.OwnerEmployeeLinks linkTable
            LEFT JOIN {database}.dbo.Employees ownerTable ON ownerTable.ID = linkTable.OwnerID
            LEFT JOIN {database}.dbo.Employees empTable ON CAST(empTable.EmployeeID AS VARCHAR) = CAST(linkTable.EmployeeID AS VARCHAR) 
            WHERE linkTable.OwnerID = ? AND linkTable.Status = 11
        """
        self.insert_owner_employee_links = """
            DECLARE @OwnerID INT = ?;
            DECLARE @EmployeeIDs NVARCHAR(max) = ?

            MERGE INTO {database}.dbo.OwnerEmployeeLinks AS Target
            USING (
                SELECT @OwnerID as OwnerID, VALUE AS EmployeeID
                FROM STRING_SPLIT(@EmployeeIDs, ',')
            ) AS Source
            ON Target.EmployeeID = Source.EmployeeID AND Target.OwnerEmployeeID = Source.OwnerID
            WHEN MATCHED AND Target.Status = 12 THEN
                UPDATE SET Status = 11
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (OwnerEmployeeID, EmployeeID, Status, Created)
                VALUES (Source.OwnerID, Source.EmployeeID, 11, GETDATE())
            OUTPUT INSERTED.ID;
        """
        self.update_owner_status_by_id = "UPDATE {database}.dbo.SqlAccounts SET Status = ? OUTPUT INSERTED.ID WHERE ID = ?"
        self.update_owner_employee_links_statuses = "UPDATE {database}.dbo.OwnerEmployeeLinks SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"
