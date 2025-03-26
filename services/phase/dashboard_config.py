from .config import Config
from .sql_config import SQLConfig


# dashboard config
class DashboardConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)
        # fmt: off

        # # dashboard select base
        dashboard_select_base = """
            SELECT 
            dashboardTable.*, 
            TRIM(employeeTable.FirstName) + ' ' + TRIM(employeeTable.LastName) as CreatorName,
            verifications.EmployeeID as CreatedBy
            FROM 
            {database}.dbo.Dashboards dashboardTable 
            OUTER APPLY (SELECT TOP 1 EmployeeID, VerificationID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = dashboardTable.VerificationID) as verifications
            LEFT JOIN {database}.dbo.Employees employeeTable ON verifications.EmployeeID = employeeTable.EmployeeID 
            WHERE 
            dashboardTable.Status IN (SELECT VALUE FROM STRING_SPLIT(?, ','))
        """
        
        # # Get All Dashboards
        # # input: PageSize, PageNumber, PageSize
        self.get_dashboards = dashboard_select_base + " AND LOWER(dashboardTable.Name) LIKE '%' + LOWER(?) + '%' ORDER BY dashboardTable.Created DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"

        # # Get Dashboard by ID
        self.get_dashboard_by_dashboard_id = dashboard_select_base + " AND dashboardTable.ID = ? ORDER BY dashboardTable.Created DESC"

        # # Get Dashboard by Creator
        self.get_dashboards_employee_id = dashboard_select_base + " AND verification.EmployeeID = ? ORDER BY dashboardTable.Created DESC"

        # # Get Dashboard by ChartID
        self.get_dashboards_by_chart_id = "SELECT dashboardTable.* FROM {database}.dbo.ChartDashboardLinks linkTable LEFT JOIN {database}.dbo.Dashboards dashboardTable ON dashboardTable.ID = linkTable.DashboardID WHERE linkTable.ChartID = ? AND linkTable.Status = 11 AND dashboardTable.Status = 11"

        # # Create Dashboard
        self.create_dashboard = "INSERT INTO {database}.dbo.Dashboards (Name, Description, VerificationID, Created, Status, RefreshRate, Visibility, Data) OUTPUT inserted.ID VALUES (?, ?, ?, GETDATE(), 11, ?, ?, ?)"

        # # Update Dashboard
        self.update_dashboard = "UPDATE {database}.dbo.Dashboards SET Name = ?, Description = ?, RefreshRate = ?, Data = ?, ThumbnailLink = ?, Visibility = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Update Dashboard Status
        self.update_dashboard_status_by_dashboard_id = "UPDATE {database}.dbo.Dashboards SET Status = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Get All Chart Types
        self.get_chart_types = "SELECT * FROM {database}.dbo.ChartTypes"

        # # chart select base
        chart_select_base = """
            SELECT 
            chartTable.*, 
            chartTypesTable.Name as Type, 
            statusTable.StatusType as StatusType, 
            TRIM(employeeTable.FirstName) + ' ' + TRIM(employeeTable.LastName) as CreatorName, 
            queriesTable.ID AS QueryID, 
            queriesTable.Name as QueryName, 
            queriesTable.Description as QueryDescription, 
            queriesTable.QueryString as QueryString 
            FROM 
            {database}.dbo.Charts chartTable 
            OUTER APPLY (SELECT TOP 1 EmployeeID, VerificationID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = chartTable.VerificationID) as verifications
            LEFT JOIN 
            {database}.dbo.ChartTypes chartTypesTable ON chartTable.TypeID = chartTypesTable.ID 
            LEFT JOIN 
            {database}.dbo.Status statusTable ON chartTable.Status = statusTable.ID 
            LEFT JOIN 
            {database}.dbo.Queries queriesTable on queriesTable.ID = chartTable.QueryID 
            LEFT JOIN 
            {database}.dbo.Employees employeeTable ON verifications.EmployeeID = employeeTable.EmployeeID 
            WHERE 
            chartTable.Status IN (SELECT VALUE FROM STRING_SPLIT(?, ','))
        """

        # # Get All Charts
        # # input: [SearchKey], [Statuses], [TypeIDs], [TypeIDs], PageNumber, PageSize
        self.get_charts = chart_select_base + " AND LOWER(chartTable.Name) LIKE '%' + LOWER(?) + '%' AND ( LEN(?) = 0 OR chartTable.TypeID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))) ORDER BY chartTable.Created DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        
        # # Get Charts by Type
        self.get_charts_by_type = chart_select_base + " AND chartTable.TypeID = ? ORDER BY chartTable.Name ASC"
        
        # # Get Charts by Creator
        self.get_charts_by_creator = chart_select_base + " AND verification.EmployeeID = ? ORDER BY chartTable.Name ASC"
        
        # # Get Charts by Creator
        self.get_charts_by_dashboard_id = "SELECT chartTable.*, linkTable.DashboardID FROM {database}.dbo.ChartDashboardLinks linkTable LEFT JOIN {database}.dbo.Charts chartTable on chartTable.ID = linkTable.ChartID WHERE DashboardID = ? AND linkTable.Status = 11"
        
        # # Get Charts by ID
        self.get_chart_by_chart = chart_select_base + " AND chartTable.ID = ? ORDER BY chartTable.Name ASC"

        # # Get Charts by IDs
        self.get_chart_by_charts = chart_select_base + " AND chartTable.ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))) ORDER BY chartTable.Created DESC"
        
        # # Get Charts by Query
        self.get_chart_by_query_id = "SELECT chartTable.* FROM {database}.dbo.Queries queryTable LEFT JOIN {database}.dbo.Charts chartTable ON chartTable.QueryID = queryTable.ID WHERE queryTable.ID = ? AND queryTable.Status = 11 AND chartTable.Status = 11"

        # # Create Chart
        self.create_chart = "INSERT INTO {database}.dbo.Charts  (Name, Description, VerificationID, TypeID, QueryID, Status, Data, Created) OUTPUT inserted.ID VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())"

        # # Update Chart
        self.update_chart_by_chart_id = "UPDATE {database}.dbo.Charts SET Name = ?, Description = ?, QueryID = ?, Data = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Update Chart Status
        self.update_chart_status_by_chart_ids = "UPDATE {database}.dbo.Charts SET Status = ? OUTPUT inserted.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"

        # # Get Chart Dashboard Link by Dashboard ID
        self.get_chart_dashboard_link_by_dashboard_id = "SELECT * FROM {database}.dbo.ChartDashboardLinks WHERE DashboardID = ? AND Status IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"

        # # Create Links
        self.create_chart_dashboard_link = "INSERT INTO {database}.dbo.ChartDashboardLinks (ChartID, DashboardID, Created, VerificationID, Status) OUTPUT INSERTED.ID SELECT VALUE, ?, GETDATE(), ?, 11 FROM STRING_SPLIT(?,',')"
        
        # # Update Link Status
        self.Update_chart_dashboard_links_status_by_link_id = "UPDATE {database}.dbo.ChartDashboardLinks SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"

        # # Get All Queries
        # # input: PageSize, PageNumber, PageSize
        self.get_queries = """
            SELECT 
            queriesTable.*, 
            TRIM(employeeTable.FirstName) + ' ' + TRIM(employeeTable.LastName) as CreatorName,
            verifications.EmployeeID as CreatedBy 
            FROM 
            {database}.dbo.Queries queriesTable 
            OUTER APPLY (SELECT TOP 1 EmployeeID, VerificationID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = queriesTable.VerificationID) as verifications
            LEFT JOIN 
            {database}.dbo.Employees employeeTable ON verifications.EmployeeID = employeeTable.EmployeeID 
            WHERE 
            queriesTable.Status IN (SELECT VALUE FROM STRING_SPLIT(?, ',')) 
            AND 
            LOWER(Name) LIKE '%' + LOWER(?) + '%' 
            ORDER BY queriesTable.Created DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """

        # # Get Queries by ID
        self.get_queries_by_query_id = "SELECT * FROM {database}.dbo.Queries WHERE ID = ?"

        # # Get Queries by IDs
        self.get_queries_by_query_ids = "SELECT * FROM {database}.dbo.Queries WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"

        # # Create Query
        self.create_query = "INSERT INTO {database}.dbo.Queries (QueryString, Status, Created, VerificationID, Name, Description) OUTPUT INSERTED.ID VALUES (?, 11, GETDATE(), ?, ?, ?)"

        # # Update Query
        self.update_query_by_query_id = "UPDATE {database}.dbo.Queries SET Name = ?, Description = ?, QueryString = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Update Query Status
        self.update_query_status_by_query_id = "UPDATE {database}.dbo.Queries SET Status = ? OUTPUT inserted.ID WHERE ID = ?"
        # fmt: on

        # Creates a new Query log
        # input: LogTypeID, Change, LogNote, Logged, VerificationID, QueryID, QueryID, QueryID, QueryID, QueryID, QueryIDm, QueryID
        self.insert_query_log = "INSERT INTO {database}.dbo.QueryLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, QueryID, QueryString, Status, Created, VerificationID, Name, Description) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 QueryString FROM {database}.dbo.Queries WHERE ID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Queries WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Queries WHERE ID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Queries WHERE ID = ?), (SELECT TOP 1 Name FROM {database}.dbo.Queries WHERE ID = ?), (SELECT TOP 1 Description FROM {database}.dbo.Queries WHERE ID = ?))"

        # Creates a new ChartDashboardLink log
        # input: LogTypeID, Change, LogNote, Logged, ChartDashboardLinkID, ChartDashboardLinkID, ChartDashboardLinkID, ChartDashboardLinkID, ChartDashboardLinkID, ChartDashboardLinkID, ChartDashboardLinkID
        self.insert_chart_dashboard_link_log = "INSERT INTO {database}.dbo.ChartDashboardLinkLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ChartDashboardLinkID, ChartID, DashboardID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 ChartID FROM {database}.dbo.ChartDashboardLinks WHERE ID = ?), (SELECT TOP 1 DashboardID FROM {database}.dbo.ChartDashboardLinks WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.ChartDashboardLinks WHERE ID = ?),(SELECT TOP 1 VerificationID FROM {database}.dbo.ChartDashboardLinks WHERE ID = ?), (SELECT TOP 1 Status FROM {database}.dbo.ChartDashboardLinks WHERE ID = ?))"

        # Creates a new ChartLog
        # input: LogTypeID, Change, LogNote, ChartID, ChartID, ChartID, ChartID, ChartID, ChartID, ChartID, ChartID, ChartID, ChartID
        self.insert_chart_log = "INSERT INTO {database}.dbo.ChartLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, ChartID, Name, Description, Created, VerificationID, TypeID, Link, Status, QueryID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 Name FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 Description FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Charts WHERE ID = ?),(SELECT TOP 1 VerificationID FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 TypeID FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 Link FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Charts WHERE ID = ?), (SELECT TOP 1 QueryID FROM {database}.dbo.Charts WHERE ID = ?))"

        # Creates a new DashboardLog
        # input: LogTypeID, Change, LogNote, VerificationID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID, DashboardID
        self.insert_dashboard_log = "INSERT INTO {database}.dbo.DashboardLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, DashboardID, Name, Description, VerificationID, Created, Status, Link, Visibility, RefreshRate) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT TOP 1 Name FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 Description FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 Created FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 Link FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 VISIBILITY FROM {database}.dbo.Dashboards WHERE ID = ?), (SELECT TOP 1 RefreshRate FROM {database}.dbo.Dashboards WHERE ID = ?))"
