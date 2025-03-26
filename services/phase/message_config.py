from .config import Config
from .sql_config import SQLConfig


# owner config
class MessageConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # queries for handling single case
        self.get_case_messages_by_case_number = "SELECT ID, CaseNumber, CaseID, Status, Created FROM {database}.dbo.CaseMessages Where CaseNumber = ?"
        self.get_case_messages_by_case_id = "SELECT ID, CaseNumber, CaseID, Status, Created FROM {database}.dbo.CaseMessages Where CaseID = ?"
        self.create_case_messages = "INSERT INTO {database}.dbo.CaseMessages (CaseNumber, CaseID, Status, Created) OUTPUT Inserted.* VALUES (?, ?, ?, GETDATE())"
        self.update_case_messages_status = "UPDATE {database}.dbo.CaseMessages SET Status = ? OUTPUT INSERTED.ID WHERE ID = ?"

        self.get_messages_by_case_message_id = """
            SELECT M.ID, M.Message, M.Status, M.VerificationID, M.Created, empTable.FirstName, empTable.LastName, empTable.EmployeeID
            FROM {database}.dbo.NotificationMessages M 
            LEFT JOIN {database}.dbo.CaseMessageMessageLinks CMM ON M.ID = CMM.NotificationMessageID
            LEFT JOIN {database}.dbo.VerificationEmployeeLinks velTable ON velTable.VerificationID = M.VerificationID
            LEFT JOIN {database}.dbo.Employees empTable ON empTable.EmployeeID = velTable.EmployeeID
            WHERE CMM.CaseMessageID = ?
        """
        self.insert_message = """
            DECLARE @MessageID UNIQUEIDENTIFIER = NEWID();
            DECLARE @Message NVARCHAR(MAX) = ?;
            DECLARE @VerificationID INT = ?;
            DECLARE @CaseMessageID UNIQUEIDENTIFIER = ?;

            BEGIN TRANSACTION;

            INSERT INTO {database}.dbo.NotificationMessages (ID, Message, Status, VerificationID, Created) OUTPUT Inserted.ID 
            VALUES (@MessageID, @Message, 11, @VerificationID, GETDATE());

            INSERT INTO {database}.dbo.CaseMessageMessageLinks (NotificationMessageID, CaseMessageID, Status, Created) OUTPUT Inserted.ID 
            VALUES (@MessageID, @CaseMessageID, 11, GETDATE());

            SELECT * FROM {database}.dbo.NotificationMessages WHERE ID = @MessageID

            COMMIT TRANSACTION;
        """
        self.update_message_status = "UPDATE {database}.dbo.Messages SET Status = ? OUTPUT INSERTED.ID WHERE ID = ?"

        # queries for handling multiple cases
        self.filter_messages = """
            DECLARE @CaseNumber NVARCHAR(MAX) = ?
            DECLARE @Status NVARCHAR(MAX) = ?
            DECLARE @SortCreated TINYINT = ?
            DECLARE @Offset INT = ?
            DECLARE @RowsPerPage INT = ?
            DECLARE @From Datetime = ?
            DECLARE @To Datetime = ?
            
            -- if search by CaseNumbers, ignore Status, created date, and offset
            IF @CaseNumber IS NOT NULL  
            BEGIN  
                SET @Status = NULL;
                SET @From = NULL;  
                SET @To = NULL;  
                SET @Offset = NULL;  
            END ;
            -- select offset and rows of cases
            WITH Cases AS(
                SELECT * FROM 
                {database}.dbo.CaseMessages CM 
                WHERE (COALESCE(@Status, '') = '' OR CM.Status IN (SELECT value FROM STRING_SPLIT(@Status, ',')))
                AND (COALESCE(@CaseNumber, '') = '' OR CM.CaseNumber IN (SELECT value FROM STRING_SPLIT(@CaseNumber, ',')))
                AND (COALESCE(@From , '') = '' OR CM.Created >= @From)
                AND (COALESCE(@To , '') = '' OR CM.Created <= @To)
                ORDER BY CASE WHEN @SortCreated = 1 THEN CM.Created END ASC, 
                CASE WHEN @SortCreated = 0 THEN CM.Created END DESC
                OFFSET COALESCE(@Offset, 0) ROWS  
	            FETCH NEXT COALESCE(@RowsPerPage, 2147483647) ROWS ONLY
            )
            -- select all messages associate to the cases above
            SELECT M.Message, M.ID as MessageID, M.Created as MessageCreated, M.Status as MessageStatus, E.EmployeeID, E.FirstName, E.LastName, CM.ID as CaseMessageID, CM.CaseNumber, CM.CaseID, CM.Created as CaseMessageCreated, CM.Status as CaseMessageStatus 
            FROM Cases CM
            LEFT JOIN {database}.dbo.CaseMessageMessageLinks Link ON Link.CaseMessageID = CM.ID
            LEFT JOIN {database}.dbo.NotificationMessages M on M.ID = Link.NotificationMessageID
            LEFT JOIN {database}.dbo.VerificationEmployeeLinks VEL on VEL.VerificationID = M.VerificationID
            LEFT JOIN {database}.dbo.Employees E on E.EmployeeID = VEL.EmployeeID
            WHERE M.Status = 11
            ORDER BY CASE WHEN @SortCreated = 1 THEN CM.Created END ASC, 
            CASE WHEN @SortCreated = 0 THEN CM.Created END DESC
        """
