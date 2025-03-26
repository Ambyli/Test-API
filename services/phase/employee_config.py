from .config import Config
from .sql_config import SQLConfig


# employee config
class EmployeeConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Employee Functions
        # input: EmployeeID
        # output: [[EmployeeID, BadgeID, FirstName, LastName, EMail]]
        self.get_Employee = "SELECT EmployeeID, BadgeID, HEXBadgeID, FirstName, LastName, Technician, Manager, EMail, Position, LabName, Department, PIN FROM {database}.dbo.Employees WHERE ((FirstName + ' ' + LastName) = ? or CAST(EmployeeID as varchar(50)) = ? or BadgeID = ? or HEXBadgeID = ?)"
        self.get_Employee_Manager = "SELECT EmployeeID, BadgeID, HEXBadgeID, FirstName, LastName, Technician, Manager, EMail, Position, PIN FROM {database}.dbo.Employees WHERE ((FirstName + ' ' + LastName) = ? or CAST(EmployeeID as varchar(50)) = ? or BadgeID = ? or HEXBadgeID = ?) and Manager = 1"
        # input: N/A
        # output: [[EmployeeID, BadgeID, FirstName, LastName, EMail]]
        self.get_Employees = "SELECT EmployeeID, BadgeID, HEXBadgeID, FirstName, LastName, Technician, Manager, EMail, Position, LabName, Department, PIN, Status FROM {database}.dbo.Employees"
        # input: N/A
        # output: [[EmployeeID, BadgeID, FirstName, LastName, EMail]]
        self.get_employees_by_token_id = """
            SELECT 
            a.EmployeeID, 
            a.BadgeID, 
            a.HEXBadgeID, 
            a.FirstName, 
            a.LastName, 
            a.Technician, 
            a.Manager, 
            a.EMail, 
            a.Position, 
            a.PIN
            FROM 
            {database}.dbo.Employees as a 
            LEFT JOIN 
            {database}.dbo.EmployeeTokenLinks as c 
            on 
            a.EmployeeID = c.EmployeeID 
            WHERE 
            c.TokenID = ? 
            and 
            c.Status = 11
        """
        # input: N/A
        # output: [[ID, Name, Created, VerificationID]]
        self.get_team_info = "SELECT ID, Name, Created, VerificationID FROM {database}.dbo.Teams ORDER BY Created DESC"
        # input: N/A
        # output: [[ID, EmployeeID, TeamID, Role, Created, VerificationID]]
        self.get_teams_employees_by_team = "SELECT ID, EmployeeID, TeamID, Role, Created, VerificationID, Status FROM {database}.dbo.EmployeeTeamLinks WHERE TeamID = ? ORDER BY Created DESC"
        # input: N/A
        # output: [[RoleID, Title]]
        self.get_roles = "SELECT ID, Title FROM {database}.dbo.Roles ORDER BY ID DESC"
        # input: Location, EmployeeID, StartDate, EndDate, VerificationID, Status
        # output: [[ID]]
        self.insert_employee_location_link = "INSERT INTO {database}.dbo.EmployeeLocationLinks (Location, EmployeeID, StartDate, EndDate, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, GETDATE(), ?, ?)"
        # input: Status, LinkID
        # output: [[ID]]
        self.update_employee_location_link_status = "UPDATE {database}.dbo.EmployeeLocationLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: Date1, Date2, Location
        # output: [[ID, Location, StartDate, EndDate, Created, VerificationID, Status]]
        self.get_active_links_for_employee_location_by_location = "SELECT ID, Location, StartDate, EndDate, Created, VerificationID, Status FROM {database}.dbo.EmployeeLocationLinks WHERE ((DATEDIFF(SECOND, ?, StartDate) >= 0 and DATEDIFF(SECOND, ?, StartDate) <= 0) or (DATEDIFF(SECOND, ?, EndDate) >= 0 and DATEDIFF(SECOND, ?, EndDate) <= 0)) and Location = ? and Status = 11 ORDER BY Location DESC, Created DESC"
        # input: Date1, Date2, EmployeeID
        # output: [[ID, Location, StartDate, EndDate, Created, VerificationID, Status]]
        self.get_active_links_for_employee_location_by_employee = "SELECT ID, Location, StartDate, EndDate, Created, VerificationID, Status FROM {database}.dbo.EmployeeLocationLinks WHERE ((DATEDIFF(SECOND, ?, StartDate) >= 0 and DATEDIFF(SECOND, ?, StartDate) <= 0) or (DATEDIFF(SECOND, ?, EndDate) >= 0 and DATEDIFF(SECOND, ?, EndDate) <= 0)) and EmployeeID = ? and Status = 11 ORDER BY Location DESC, Created DESC"
        # input: Date1, Date2
        # output: [[ID, Location, StartDate, EndDate, Created, VerificationID, Status]]
        self.get_active_links_for_employee_location = "SELECT ID, Location, StartDate, EndDate, Created, VerificationID, Status FROM {database}.dbo.EmployeeLocationLinks WHERE ((DATEDIFF(SECOND, ?, StartDate) >= 0 and DATEDIFF(SECOND, ?, StartDate) <= 0) or (DATEDIFF(SECOND, ?, EndDate) >= 0 and DATEDIFF(SECOND, ?, EndDate) <= 0)) and Status = 11 ORDER BY Location DESC, Created DESC"
        # input: EmployeeID, Status, FileID, Path
        # output: [[LinkID]]
        self.insert_employee_asset_link = "INSERT INTO {database}.dbo.EmployeeAssetLinks (EmployeeID, FileID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?)"
        # input: EmployeeID, FileID
        # output: [[ID, EmployeeID, FileID, Path, Created, VerificationID, Status]]
        self.get_active_links_for_employee_assets = "SELECT ID, EmployeeID, FileID, Path, Created, VerificationID, Status FROM {database}.dbo.EmployeeAssetLinks WHERE FileID = ? and Status = 11 ORDER BY Created DESC"
        # input: FileID
        # output: [[ID, EmployeeID, FileID, Path, Created, VerificationID, Status]]
        self.get_active_links_for_employee_assets_by_employee = "SELECT ID, EmployeeID, FileID, Path, Created, VerificationID, Status FROM {database}.dbo.EmployeeAssetLinks WHERE EmployeeID = ? and FileID = ? and Status = 11 ORDER BY Created DESC"
        # input: LinkID
        # output: [[LinkID]]
        self.update_employee_asset_link_status = "UPDATE {database}.dbo.EmployeeAssetLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: Location, EmployeeID, Date1, Date2
        # output: [[Cases, Units, Location, Date]]
        self.get_location_stats_by_employee = "SELECT COUNT(CaseNumber) as Cases, SUM(Units) as Units, SelectedLocation, SelectedLocationName, [Hour] FROM (SELECT CaseNumber, COUNT(AlignerID) as Units, SelectedLocation,b.[Location] as SelectedLocationName, [Hour] FROM ( SELECT c.CaseNumber, a.AlignerID, b.PreviousLocationID as SelectedLocation, a.Logged as ExactDate, DATETIMEFROMPARTS(DATEPART(year, a.Logged), DATEPART(month, a.Logged), DATEPART(day, a.Logged), DATEPART(hour, a.Logged), 0, 0, 0) as [Hour] FROM {database}.dbo.AlignerLog as a left join {database}.dbo.PreviousLocations as b on a.Location = b.LocationID left join {database}.dbo.Cases as c on a.CaseID = c.CaseID WHERE b.[Status] = 16 and a.Location = (SELECT FollowingLocationID FROM {database}.dbo.FollowingLocations WHERE LocationID = ? and [Status] = 16) and a.LoggedVerificationID = (SELECT TOP 1 VerificationID FROM {database}.dbo.VerificationEmployeeLinks WHERE EmployeeID = ?) and a.LogNote = 'Location Updated' and DATEDIFF(SECOND, ?, a.Logged) >= 0 and DATEDIFF(SECOND, ?, a.Logged) <= 0 ) as inner_query, {database}.dbo.Locations as b WHERE inner_query.SelectedLocation = b.ID GROUP BY CaseNumber, SelectedLocation, b.Location, [Hour]) as outer_query GROUP BY SelectedLocation, SelectedLocationName, [Hour]"
        self.get_location_stats_by_employee_per_location = "SET NOCOUNT ON DECLARE @Location as int DECLARE DB_Cursor CURSOR FOR SELECT ID FROM {database}.dbo.Locations ORDER BY ID ASC DROP TABLE IF EXISTS #TempFiles CREATE TABLE #TempFiles (Cases int, Units int, ID int, [Location] varchar(50), [Date] datetime) OPEN DB_Cursor FETCH NEXT FROM DB_Cursor INTO @Location WHILE @@FETCH_STATUS = 0 BEGIN INSERT INTO #TempFiles (Cases, Units, ID, [Location], [Date]) (SELECT COUNT(CaseNumber) as Cases, SUM(Units) as Units, SelectedLocation, SelectedLocationName, [Hour] FROM (SELECT CaseNumber, COUNT(AlignerID) as Units, SelectedLocation,b.[Location] as SelectedLocationName, [Hour] FROM ( SELECT c.CaseNumber, a.AlignerID, b.PreviousLocationID as SelectedLocation, a.Logged as ExactDate, DATETIMEFROMPARTS(DATEPART(year, a.Logged), DATEPART(month, a.Logged), DATEPART(day, a.Logged), DATEPART(hour, a.Logged), 0, 0, 0) as [Hour] FROM {database}.dbo.AlignerLog as a left join {database}.dbo.PreviousLocations as b on a.Location = b.LocationID left join {database}.dbo.Cases as c on a.CaseID = c.CaseID WHERE b.[Status] = 16 and a.Location = (SELECT FollowingLocationID FROM {database}.dbo.FollowingLocations WHERE LocationID = @Location and [Status] = 16) and a.LoggedVerificationID = (SELECT TOP 1 VerificationID FROM {database}.dbo.VerificationEmployeeLinks WHERE EmployeeID = ?) and a.LogNote = 'Location Updated' and DATEDIFF(SECOND, ?, a.Logged) >= 0 and DATEDIFF(SECOND, ?, a.Logged) <= 0 ) as inner_query, {database}.dbo.Locations as b WHERE inner_query.SelectedLocation = b.ID GROUP BY CaseNumber, SelectedLocation, b.Location, [Hour]) as outer_query GROUP BY SelectedLocation, SelectedLocationName, [Hour]) FETCH NEXT FROM DB_Cursor INTO @Location END SELECT * FROM #TempFiles ORDER BY [Date] DESC, [ID] ASC DROP TABLE #TempFiles CLOSE DB_Cursor DEALLOCATE DB_Cursor"
        # input: Location, StartDate, EndDate
        # output: [[Cases, Units, Date]]
        self.get_location_stats_for_all_employees = "SELECT COUNT(CaseNumber) as Cases, SUM(Units) as Units, SelectedLocation, SelectedLocationName, [Hour] FROM (SELECT (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = inner_query.VerificationID) as EmployeeID, CaseNumber, COUNT(AlignerID) as Units, SelectedLocation, b.[Location] as SelectedLocationName, [Hour] FROM ( SELECT a.VerificationID, c.CaseNumber, a.AlignerID, b.PreviousLocationID as SelectedLocation, a.Logged as ExactDate, DATETIMEFROMPARTS(DATEPART(year, a.Logged), DATEPART(month, a.Logged), DATEPART(day, a.Logged), DATEPART(hour, a.Logged), 0, 0, 0) as [Hour] FROM {database}.dbo.ALignerLog as a left join {database}.dbo.PreviousLocations as b on a.Location = b.LocationID left join {database}.dbo.Cases as c on a.CaseID = c.CaseID WHERE b.[Status] = 16 and a.Location = (SELECT FollowingLocationID FROM {database}.dbo.FollowingLocations WHERE LocationID = ? and [Status] = 16) and a.LogNote = 'Location Updated' and DATEDIFF(SECOND, ?,a.Logged) >= 0 and DATEDIFF(SECOND, ?,a.Logged) <= 0 ) as inner_query, {database}.dbo.Locations as b WHERE inner_query.SelectedLocation = b.ID GROUP BY EmployeeID, CaseNumber, SelectedLocation, b.Location, [Hour]) as outer_query GROUP BY EmployeeID, SelectedLocation, SelectedLocationName, [Hour]"
        # input: EmployeeID, AssigneeID, Location
        # output: [[LinkID]]
        self.insert_employee_punch_link = "INSERT INTO {database}.dbo.EmployeePunchLinks (Location, EmployeeID, CheckedInVerificationID, CheckedIn, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), 11)"
        # input: Status, LinkID
        # output: [[LinkID]]
        self.update_employee_punch_link_status = "UPDATE {database}.dbo.EmployeePunchLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # input: EmployeeID, LinkID
        # output: [[LinkID]]
        self.checkout_employee_punch_link = "UPDATE {database}.dbo.EmployeePunchLinks SET CheckedOutVerificationID = ?, CheckedOut = GETDATE(), Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        # input: EmployeeID
        # output: [[ID, Location, EmployeeID, CheckedInVerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status]]
        self.get_active_employee_punch_links = "SELECT ID, Location, EmployeeID, CheckedInVerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status FROM {database}.dbo.EmployeePunchLinks WHERE EmployeeID = ? and CheckedOutVerificationID IS NULL and Status = 11 ORDER BY ID ASC"
        # input: EmployeeID, Date1, Date2
        # output: [[ID, Location, EmployeeID, CheckedInVerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status]]
        self.get_employee_punch_links_by_date = "SELECT ID, Location, EmployeeID, CheckedInVerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status FROM {database}.dbo.EmployeePunchLinks WHERE EmployeeID = ? and (((DATEDIFF(SECOND, ?, CheckedIn) >= 0 and DATEDIFF(SECOND, ?, CheckedIn) <= 0) or (DATEDIFF(SECOND, ?, CheckedOut) >= 0 and DATEDIFF(SECOND, ?, CheckedOut) <= 0))) ORDER BY ID DESC"
        # input: FirstName, LastName, BadgeID, HEXBadgeID, EmployeeID, PIN
        # output: [[ID, FirsName, LastName, BadgeID, HEXBadgeID, EmployeeID, PIN]]
        self.insert_employee = "INSERT INTO {database}.dbo.Employees (Active, FirstName, LastName, Technician, Department, LabName, Manager, CreatedVerificationID, BadgeID, HEXBadgeID, PIN, Created, Status) OUTPUT Inserted.EmployeeID, Inserted.FirstName, Inserted.LastName, Inserted.Technician, Inserted.Department, Inserted.LabName, Inserted.Manager, Inserted.Created, Inserted.BadgeID, Inserted.HEXBadgeID, Inserted.PIN, Inserted.Status VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 11)"
        # output: [[ID, FirsName, LastName, BadgeID, HEXBadgeID, EmployeeID, PIN]]
        self.update_selected_employee = "UPDATE {database}.dbo.Employees SET FirstName = ?, LastName = ?, Technician = ?, Department = ?, LabName = ?, Manager = ?, BadgeID = ?, HEXBadgeID = ?, Status = ? OUTPUT Inserted.EmployeeID, Inserted.FirstName, Inserted.LastName, Inserted.Technician, Inserted.Department, Inserted.LabName, Inserted.Manager, Inserted.BadgeID, Inserted.HEXBadgeID, Inserted.Status WHERE EmployeeID = ?"
        # input: BadgeID, HEXBadgeID, EmployeeID
        # output: [[ID, Name, Description]]
        self.get_employee_endpoint_links = "SELECT endpointTable.ID, endpointTable.Name, endpointTable.Description FROM {database}.dbo.EmployeeEndpointLinks empEndLinkTable LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = empEndLinkTable.EndpointID WHERE empEndLinkTable.EmployeeID = ? AND empEndLinkTable.Status = 11 AND endpointTable.Status = 11"
        # input: EmployeeID
        # output: [[ID, Company, Token]
        self.get_employee_tokens_by_employee = "SELECT tokenTable.ID, tokenTable.Company, tokenTable.Token FROM {database}.dbo.Tokens tokenTable LEFT JOIN {database}.dbo.EmployeeTokenLinks empTokLinkTable ON empTokLinkTable.TokenID = tokenTable.ID WHERE empTokLinkTable.EmployeeID = ? AND tokenTable.Status = 11 AND empTokLinkTable.Status = 11"
        # input: EmployeeID,, TokenID, VerificationID
        # output: [[ID]]
        self.insert_employee_token_link = "INSERT INTO {database}.dbo.EmployeeTokenLinks (EmployeeID, TokenID, VerificationID, Created, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), 11)"
        # input: EmployeeID, Verification, EndpointIDs as string
        # output: [[ID]]
        self.insert_employee_endpoint_links = "INSERT INTO {database}.dbo.EmployeeEndpointLinks (EmployeeID, EndpointID, VerificationID, Status, Created) OUTPUT Inserted.ID SELECT ?, CAST(VALUE as INT), ?, 11, GETDATE() FROM STRING_SPLIT(?,',')"
        # input: Status, LinkIDs as string
        # output [[ID]]
        self.update_employee_endpoint_link_status = "UPDATE {database}.dbo.EmployeeEndpointLinks SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT CONVERT(INT, VALUE) FROM STRING_SPLIT(?, ','))"
        # Employee Endpoint Params Queries
        # Get employee endpoint params
        # input: employeeID, endpointID
        self.get_employee_endpoint_params_by_employee_endpoint = "SELECT ep.Name FROM {database}.dbo.EmployeeEndpointParamLinks eep LEFT JOIN {database}.dbo.EndpointParams ep ON ep.ID = eep.EndpointParamID WHERE eep.EmployeeID = ? AND eep.EndpointID = ? AND eep.Status = 11 AND ep.Status = 11"
        # insert employees endpoint params
        # input: employeeIDs, paramIDs, endpointID, verification
        self.insert_employees_endpoint_params = """
            DECLARE @EmployeeIDs NVARCHAR(255) = ?;
            DECLARE @EndpointParamIDs NVARCHAR(255) = ?;

            INSERT INTO {database}.dbo.EmployeeEndpointParamLinks (EmployeeID, EndpointParamID, EndpointID, VerificationID, Status) OUTPUT INSERTED.ID
            SELECT CAST(e.value AS INT) AS EmployeeID,
                CAST(ep.value AS INT) AS EndpointParamID,
                ? AS EndpointID,
                ? AS VerificationID,
                11 AS Status
            FROM STRING_SPLIT(@EmployeeIDs, ',') AS e
            CROSS JOIN STRING_SPLIT(@EndpointParamIDs, ',') AS ep
        """
        # # this insert query only insert link if there is no OwnerID and EndpointID in database
        # # if OwnerID and EndpointID is in database, but status is 12, query will update status to 11 instead of creating new item
        self.insert_employee_endpoint_links = """
            DECLARE @EmployeeID INT = ?;
            DECLARE @EndpointIDs NVARCHAR(MAX) = ?;
            DECLARE @Verification INT = ?;

            MERGE INTO {database}.dbo.EmployeeEndpointLinks AS Target
            USING (
                SELECT EmployeeID AS EmployeeID, VALUE AS EndpointID
                FROM STRING_SPLIT(@EndpointIDs, ',')
            ) AS Source
            ON Target.EndpointID = Source.EndpointID AND Target.EmployeeID = Source.EmployeeID
            WHEN MATCHED AND Target.Status = 12 THEN
                UPDATE SET Status = 11
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (EmployeeID, EndpointID, VerificationID, Status, Created)
                VALUES (Source.EmployeeID, Source.EndpointID, @Verification, 11, GETDATE())
            OUTPUT INSERTED.ID;
        """
        self.update_employee_endpoint_link_status_by_link_id = "UPDATE {database}.dbo.EmployeeEndpointLinks SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"
        self.get_Departments = "SELECT ID, Department, ManagerID, Status FROM {database}.dbo.Departments WHERE Status = 11"
