from .config import Config
from .sql_config import SQLConfig


# customer config
class NotificationsConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Notification Functions
        self.select_notification_automations = """
            DECLARE @name NVARCHAR(255) = ?;

            WITH automation AS (
                SELECT an.ID, an.Name, an.Description, an.Func, an.Interval, an.Created, an.VerificationID, an.Status, link.EmployeeID as CreatedBy
                FROM {database}.dbo.NotificationAutomations an
				LEFT JOIN {database}.dbo.VerificationEmployeeLinks link ON an.VerificationID = link.VerificationID
            )
            SELECT 
                a.*,
                (
                    SELECT STRING_AGG(EmployeeID, ',') 
                    FROM {database}.dbo.EmployeeNotificationAutomationLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS EmployeeIDs,
                (
                    SELECT STRING_AGG(RoleID, ',') 
                    FROM {database}.dbo.RoleNotificationAutomationLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS RoleIDs,
				(
                    SELECT STRING_AGG(QueryID, ',') 
                    FROM {database}.dbo.NotificationAutomationQueryLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS QueryIDs
            FROM automation a
            WHERE (@name IS NULL OR Name LIKE '%' + @name + '%') AND Status IN (5,11) 
            ORDER BY Name DESC;
        """
        # # Notification Functions
        self.select_notification_automation_by_id = """
            DECLARE @id uniqueidentifier = ?;

            WITH automation AS (
                SELECT an.ID, an.Name, an.Description, an.Func, an.Interval, an.Created, an.VerificationID, an.Status, link.EmployeeID as CreatedBy
                FROM {database}.dbo.NotificationAutomations an
				LEFT JOIN {database}.dbo.VerificationEmployeeLinks link ON an.VerificationID = link.VerificationID
            )
            SELECT 
                a.*,
                (
                    SELECT STRING_AGG(EmployeeID, ',') 
                    FROM {database}.dbo.EmployeeNotificationAutomationLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS EmployeeIDs,
                (
                    SELECT STRING_AGG(RoleID, ',') 
                    FROM {database}.dbo.RoleNotificationAutomationLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS RoleIDs,
				(
                    SELECT STRING_AGG(QueryID, ',') 
                    FROM {database}.dbo.NotificationAutomationQueryLinks 
                    WHERE NotificationAutomationID = a.ID AND Status = 11
                ) AS QueryIDs
            FROM automation a
            WHERE ID = @id AND Status IN (5,11)
        """
        # # Get all notification automation by employeeID
        self.select_notification_automation_by_employee_id = """
            DECLARE @employeeID INT = ?;

            SELECT na.ID, na.Name, na.Description, na.Func, na.Interval, na.Created
            FROM {database}.dbo.NotificationAutomations na
            LEFT JOIN {database}.dbo.EmployeeNotificationAutomationLinks enal ON na.ID = enal.NotificationAutomationID
            WHERE enal.EmployeeID = @employeeID and na.Status IN (5,11) and enal.Status = 11

            UNION ALL

            SELECT na.ID, na.Name, na.Description, na.Func, na.Interval, na.Created
            FROM {database}.dbo.NotificationAutomations na
            LEFT JOIN {database}.dbo.RoleNotificationAutomationLinks rnal ON na.ID = rnal.NotificationAutomationID
            LEFT JOIN {database}.dbo.UserAccounts ua ON ua.role = rnal.RoleID
            WHERE ua.employeeID = @employeeID and na.Status IN (5,11) and rnal.Status = 11
        """
        self.select_notification_automations_pagination = """
            DECLARE @name NVARCHAR(255) = ?;
            DECLARE @offset INT = ?;
            DECLARE @rowsPerPage INT = ?;
            DECLARE @status NVARCHAR(255) = ?;
            DECLARE @roles NVARCHAR(255) = ?;

            WITH automation AS (
                SELECT an.ID, an.Name, an.Description, an.Func, an.Interval, an.Created, an.VerificationID, an.Status, link.EmployeeID as CreatedBy
                FROM {database}.dbo.NotificationAutomations an
				LEFT JOIN {database}.dbo.VerificationEmployeeLinks link ON an.VerificationID = link.VerificationID
            ),
            notificationAutomation AS (
                SELECT 
                    a.*,
                    (
                        SELECT STRING_AGG(EmployeeID, ',') 
                        FROM {database}.dbo.EmployeeNotificationAutomationLinks 
                        WHERE NotificationAutomationID = a.ID AND Status = 11
                    ) AS EmployeeIDs,
                    (
                        SELECT STRING_AGG(RoleID, ',') 
                        FROM {database}.dbo.RoleNotificationAutomationLinks 
                        WHERE NotificationAutomationID = a.ID AND Status = 11 
                        AND (@roles IS NULL OR RoleID IN (SELECT VALUE FROM STRING_SPLIT(@roles, ',')))
                    ) AS RoleIDs,
                    (
                        SELECT STRING_AGG(QueryID, ',') 
                        FROM {database}.dbo.NotificationAutomationQueryLinks 
                        WHERE NotificationAutomationID = a.ID AND Status = 11
                    ) AS QueryIDs
                FROM automation a

            )
            SELECT * 
            FROM notificationAutomation nt
            WHERE (@name IS NULL OR Name LIKE '%' + @name + '%') 
                AND (
                        (@status IS NULL AND Status IN (5, 11))
                        OR 
                        (@status IS NOT NULL AND Status IN (SELECT VALUE FROM STRING_SPLIT(@status, ',')))
                ) 
                AND	(
                        (@roles IS NOT NULL AND RoleIDs IS NOT NULL) 
                        OR 
                        (@roles IS NULL AND 1 = 1)
                    )
            ORDER BY Name ASC
            OFFSET @offset ROWS FETCH NEXT @rowsPerPage ROWS ONLY;

        """
        self.insert_notification_automation = """
            DECLARE @Name NVARCHAR(MAX) = ?; 
            DECLARE @Desc NVARCHAR(MAX) = ?;
            DECLARE @Func NVARCHAR(MAX) = ?;
            DECLARE @Interval INT = ?;
            DECLARE @VerificationID INT = ?;
            DECLARE @RoleIDs NVARCHAR(MAX) = ?;
            DECLARE @LinkEmployeeIDs NVARCHAR(MAX) = ?;
            DECLARE @Status INT = ?;

            -- Create temp table to store UUID for new automation
            DECLARE @NotiTempTable Table (ID uniqueidentifier)
            -- Create temp table to store created UUID above with all given roleIDs
            DECLARE @NotiRoleTempTable Table (ID uniqueidentifier, RoleID INT)
            -- Create temp table to store created UUID above with all given employeeIDs
            DECLARE @NotiEmpTempTable Table (ID uniqueidentifier, EmployeeID INT)

            -- Insert UUID to @NotiTempTable temp table
            INSERT INTO @NotiTempTable (ID) OUTPUT Inserted.ID  values (NEWID()) 

            -- Insert UUID from NotiTempTable associate with all given roleIDs to @NotiRoleTempTable temp table
            INSERT INTO @NotiRoleTempTable (ID, RoleID)
            OUTPUT Inserted.ID 
            SELECT (SELECT ID FROM @NotiTempTable) AS ID, VALUE 
            FROM STRING_SPLIT(@RoleIDs, ',')

            -- Insert UUID from NotiTempTable associate with all given employeeIDs to @NotiEmpTempTable temp table
            INSERT INTO @NotiEmpTempTable (ID, EmployeeID)
            OUTPUT Inserted.ID 
            SELECT (SELECT ID FROM @NotiTempTable) AS ID, VALUE 
            FROM STRING_SPLIT(@LinkEmployeeIDs, ',')

            -- Insert data to NotificationAutomations using given data and UUID from @NotiTempTable
            INSERT INTO {database}.dbo.NotificationAutomations 
            (ID, Name, Description, Func, Interval, Created, VerificationID, Status) 
            OUTPUT Inserted.ID 
            SELECT ID, @Name, @Desc, @Func, @Interval, GETDATE(), @VerificationID, @Status
            FROM @NotiTempTable

            -- Insert data to RoleNotificationAutomationLinks using RoleID and NotificationAutomationID from @NotiRoleTempTable temp table
            INSERT INTO {database}.dbo.RoleNotificationAutomationLinks (RoleID, NotificationAutomationID, Created, VerificationID, Status)
            OUTPUT Inserted.ID 
            SELECT RoleID, ID, GETDATE(), @VerificationID, 11
            FROM @NotiRoleTempTable

            -- Insert data to EmployeeNotificationAutomationLinks using EmployeeID and NotificationAutomationID from @NotiEmpTempTable temp table
            INSERT INTO {database}.dbo.EmployeeNotificationAutomationLinks (EmployeeID, NotificationAutomationID, Created, VerificationID, Status)
            OUTPUT Inserted.ID
            SELECT EmployeeID, ID, GETDATE(), @VerificationID, 11
            FROM @NotiEmpTempTable
        """
        self.update_notification_automation_by_id = "UPDATE {database}.dbo.NotificationAutomations SET Name = ?, Description = ?, Func = ?, Interval = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_notification_automation_status_by_id = "UPDATE {database}.dbo.NotificationAutomations SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"

        self.select_role_notification_automation_links = "SELECT ID, RoleID, NotificationAutomationID, Created, VerificationID, Status FROM {database}.dbo.RoleNotificationAutomationLinks"
        self.insert_role_notification_automation_links = """
            DECLARE @roleIDs NVARCHAR(MAX) = ?;
            DECLARE @NotificationAutomationID uniqueidentifier = ?;
            DECLARE @VerificationID INT = ?;

            WITH SplitRoleIDs AS (
                SELECT value AS RoleID
                FROM STRING_SPLIT(@roleIDs, ',')
            )
            INSERT INTO {database}.dbo.RoleNotificationAutomationLinks (RoleID, NotificationAutomationID, Created, VerificationID, Status) OUTPUT Inserted.ID 
            SELECT RoleID, @NotificationAutomationID, GETDATE(), @VerificationID, 11
            FROM SplitRoleIDs
        """
        self.update_role_notification_automation_link_by_id = "UPDATE {database}.dbo.RoleNotificationAutomationLinks SET RoleID = ?, NotificationAutomationID = ?, Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_role_notification_automation_link_statuses = "UPDATE {database}.dbo.RoleNotificationAutomationLinks SET Status = ? OUTPUT Inserted.ID WHERE NotificationAutomationID = ? AND RoleID IN (SELECT value FROM STRING_SPLIT(?, ','));"

        self.select_employee_notification_links = "SELECT ID, NotificationAutomationID, EmployeeID, Created, VerificationID, Status FROM {database}.dbo.EmployeeNotificationAutomationLinks"
        self.insert_employee_notification_links = """
            DECLARE @employeeIDs NVARCHAR(MAX) = ?;
            DECLARE @NotificationAutomationID uniqueidentifier = ?;
            DECLARE @VerificationID INT = ?;

            WITH SplitEmployeeIDs AS (
                SELECT value AS EmployeeID
                FROM STRING_SPLIT(@employeeIDs, ',')
            )
            INSERT INTO {database}.dbo.EmployeeNotificationAutomationLinks (NotificationAutomationID, EmployeeID, Created, VerificationID, Status) OUTPUT Inserted.ID 
            SELECT @NotificationAutomationID, EmployeeID, GETDATE(), @VerificationID, 11
            FROM SplitEmployeeIDs
        """
        self.update_employee_notification_link_statuses = "UPDATE {database}.dbo.EmployeeNotificationAutomationLinks SET Status = ? OUTPUT Inserted.ID WHERE NotificationAutomationID = ? AND EmployeeID IN (SELECT value FROM STRING_SPLIT(?, ','));"

        self.select_notification_automation_logs = "SELECT ID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, NotificationAutomationID, Name, Description, Func, Interval, Created, VerificationID, Status FROM {database}.dbo.NotificationAutomationLogs"
        self.insert_notification_automation_log = "INSERT INTO {database}.dbo.NotificationAutomationLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, NotificationAutomationID, Name, Description, Func, Interval, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, GETDATE(), ?, 11)"
        self.update_notification_automation_log_by_id = "UPDATE {database}.dbo.NotificationAutomationLogs SET LogTypeID = ?, Change = ?, LogNote = ?, LoggedVerificationID = ?, NotificationAutomationID = ?, Name = ?, Description = ?, Func = ?, Interval = ?, Status = ? OUTPUT Inserted.ID WHERE ID = ?"

        self.select_notification_automation_query_links = "SELECT ID, QueryID, VariableName, Created, VerificationID, Status, NotificationAutomationID FROM {database}.dbo.NotificationAutomationQueryLinks WHERE Status = 11"
        self.insert_notification_automation_query_link = "INSERT INTO {database}.dbo.NotificationAutomationQueryLinks (QueryID, VariableName, Created, VerificationID, Status, NotificationAutomationID) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11, ?)"
        self.update_notification_automation_query_link_by_id = "UPDATE {database}.dbo.NotificationAutomationQueryLinks SET VariableName = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_notification_automation_query_link_status_by_ids = "UPDATE {database}.dbo.NotificationAutomationQueryLinks SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT value FROM STRING_SPLIT(?, ','))"

        self.select_notification_automation_message_links = "SELECT ID, NotificationAutomationID, NotificationMessageID, Created, VerificationID, Status FROM {database}.dbo.NotificationAutomationMessageLinks"
        self.insert_notification_automation_message_link = "INSERT INTO {database}.dbo.NotificationAutomationMessageLinks (NotificationAutomationID, NotificationMessageID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        self.update_notification_automation_message_link_by_id = "UPDATE {database}.dbo.NotificationAutomationMessageLinks SET NotificationAutomationID = ?, NotificationMessageID = ?, Status = ? OUTPUT Inserted.ID WHERE ID = ?"

        self.select_notification_messages = "SELECT nm.ID, nm.Message, nm.Created, nm.VerificationID, nm.Status, na.Name as NotificationAutomationName, na.ID as NotificationAutomationID FROM {database}.dbo.NotificationMessages nm LEFT JOIN {database}.dbo.NotificationAutomationMessageLinks link ON nm.ID = link.NotificationMessageID LEFT JOIN {database}.dbo.NotificationAutomations na ON link.NotificationAutomationID = na.ID WHERE nm.Status = 11"
        self.insert_notification_message = "INSERT INTO {database}.dbo.NotificationMessages (Message, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, GETDATE(), ?, 11)"
        self.update_notification_message_status_by_ids = "UPDATE {database}.dbo.NotificationMessages SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT value FROM STRING_SPLIT(?, ','));"

        self.insert_notifications = """
            DECLARE @EmployeeIDs NVARCHAR(MAX) = ?;
            DECLARE @MessageID uniqueidentifier = ?;
            DECLARE @VerificationID int = ?;

            DECLARE @EmpIDsTempTable Table (ID uniqueidentifier, EmployeeID int);

            -- Insert EmployeeIDs and UUIDs as NotificationIDs into Temp Table
            INSERT INTO @EmpIDsTempTable (ID, EmployeeID)
            OUTPUT INSERTED.ID, INSERTED.EmployeeID
            SELECT NEWID(), value
            FROM STRING_SPLIT(@EmployeeIDs, ',');

            -- Insert into Notifications
            INSERT INTO {database}.dbo.Notifications (ID, MessageID, Created, VerificationID, Status, Viewed) 
            OUTPUT INSERTED.ID
            SELECT ID, @MessageID, GETDATE(), @VerificationID, 11, NULL 
            FROM @EmpIDsTempTable;

            -- Insert into NotificationEmployeeLinks
            INSERT INTO {database}.dbo.NotificationEmployeeLinks (EmployeeID, NotificationID, Created, VerificationID, Status) 
            OUTPUT INSERTED.EmployeeID, INSERTED.NotificationID
            SELECT e.EmployeeID, ID, GETDATE(), @VerificationID, 11
            FROM @EmpIDsTempTable as t
			JOIN {database}.dbo.Employees AS e ON t.EmployeeID = e.EmployeeID;
        """
        self.update_notification_by_id = "UPDATE {database}.dbo.Notifications SET MessageID = ?, Status = ?, Viewed = ? OUTPUT Inserted.ID WHERE ID = ?"
        self.update_notification_status_by_notifications = "UPDATE {database}.dbo.Notifications SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(CAST(? AS NVARCHAR(MAX)), ','))"
        # mark all as viewed by employeeID
        self.update_all_notification_viewed_by_employee = """
            UPDATE {database}.dbo.Notifications SET Viewed = GETDATE() 
            OUTPUT Inserted.ID 
            FROM  {database}.dbo.Notifications n
            LEFT JOIN {database}.dbo.NotificationEmployeeLinks nel ON nel.NotificationID = n.ID
            WHERE nel.EmployeeID = ? AND n.Viewed IS NULL
        """
        # mark all selected as viewed by ids
        self.update_notification_viewed_by_ids = """
            UPDATE {database}.dbo.Notifications SET Viewed = GETDATE() 
            OUTPUT Inserted.ID 
            FROM  {database}.dbo.Notifications
            WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?,',')) AND Viewed IS NULL
        """
        self.select_queries_by_automation_id = """
            SELECT q.ID, q.QueryString, q.Status, q.Created, q.VerificationID, q.Name, q.Description, naql.VariableName, naql.ID as LinkID
            FROM {database}.dbo.NotificationAutomationQueryLinks naql
            LEFT JOIN {database}.dbo.Queries q ON naql.QueryID = q.ID
            WHERE naql.NotificationAutomationID = ? AND naql.Status = 11 AND q.Status = 11
        """
        self.select_employee_ids_by_automation_id = """
            SELECT EmployeeID
            FROM {database}.dbo.EmployeeNotificationAutomationLinks
            WHERE NotificationAutomationID = ? AND Status = 11

            UNION

            SELECT ua.employeeID
            FROM {database}.dbo.UserAccounts ua
            LEFT JOIN {database}.dbo.RoleNotificationAutomationLinks rnal ON ua.role = rnal.RoleID
            WHERE rnal.NotificationAutomationID = ? AND ua.status = 11 AND rnal.Status = 11
        """
        self.select_notifications_by_employee_id = """
            DECLARE @offset INT = ?;
            DECLARE @rowsPerPage INT = ?;
            DECLARE @Viewed BIT = ?;
            DECLARE @EmployeeID INT = ?;
            DECLARE @AutomationIDs NVARCHAR(MAX) = ?;

            SELECT nm.*, n.ID as NotificationID, na.ID as NotificationAutomationID, na.Name as NotificationAutomationName, n.Viewed, links.EmployeeID  
            FROM {database}.dbo.NotificationMessages nm
            LEFT JOIN {database}.dbo.NotificationAutomationMessageLinks naml ON naml.NotificationMessageID = nm.ID
			LEFT JOIN {database}.dbo.NotificationAutomations na ON na.ID = naml.NotificationAutomationID
            LEFT JOIN {database}.dbo.Notifications n ON n.MessageID = nm.ID
            LEFT JOIN {database}.dbo.NotificationEmployeeLinks links ON links.NotificationID = n.ID
            WHERE links.EmployeeID = @EmployeeID 
			AND links.Status = 11 
			AND n.Status = 11 
			AND nm.Status = 11
			AND (
				(@AutomationIDs is not NULL AND NotificationAutomationID IN (SELECT VALUE FROM STRING_SPLIT(@AutomationIDs, ',')))
				OR 
				(@AutomationIDs is NULL)
			)
            AND (
                (@Viewed = 0 AND n.Viewed IS NULL)
                OR
                (@Viewed = 1 AND n.Viewed IS NOT NULL)
                OR
                (@Viewed IS NULL)
            )
            ORDER BY nm.Created DESC
        """

        self.select_notifications_by_employee_id_pagination = (
            self.select_notifications_by_employee_id
            + " OFFSET @offset ROWS FETCH NEXT @rowsPerPage ROWS ONLY"
        )
