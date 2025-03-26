from .config import Config
from .sql_config import SQLConfig


# endpoint config
class EndpointConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # Endpoints Queries
        # Get All Endpoint
        self.get_endpoints = "SELECT ID, Name, Description, TokenCheck, Status FROM {database}.dbo.Endpoints WHERE Status = 11"
        # Get Endpoint by ID
        self.get_endpoint_by_endpoint_id = "SELECT ID, Name, Description, TokenCheck, Status FROM {database}.dbo.Endpoints WHERE ID = ? AND Status = 11"
        # Get Endpoint by Name
        self.get_endpoint_by_endpoint_name = "SELECT ID, Name, Description, TokenCheck, Status FROM {database}.dbo.Endpoints WHERE Name = ? AND Status = 11"
        # Get Endpoint by EmployeeID
        self.get_endpoints_by_employee_id = "SELECT endpointTable.*, linkTable.ID as LinkID FROM {database}.dbo.TokenEndpointLinks linkTable LEFT JOIN {database}.dbo.EmployeeTokenLinks etlinkTable ON etlinkTable.TokenID = linkTable.TokenID LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = linkTable.EndpointID where etlinkTable.EmployeeID = ? AND linkTable.Status = 11"
        # Get Endpoint by token
        self.get_endpoints_by_employee_token = "SELECT endpointTable.*, linkTable.ID as LinkID FROM {database}.dbo.TokenEndpointLinks linkTable LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = linkTable.EndpointID LEFT JOIN {database}.dbo.Tokens tokenTable ON tokenTable.ID = linkTable.TokenID where tokenTable.Token = ? AND linkTable.Status = 11"
        # Insert Endpoint
        self.insert_endpoint = """
        DECLARE @EndpointName NVARCHAR(MAX) = ?;
        DECLARE @Description NVARCHAR(MAX) = ?;
        DECLARE @TokenCheck BIT = ?;
        IF EXISTS (SELECT 1 FROM {database}.dbo.Endpoints WHERE Name = @EndpointName)
        BEGIN
            IF EXISTS (SELECT 1 FROM {database}.dbo.Endpoints WHERE Name = @EndpointName AND Status = 12)
			BEGIN
				UPDATE {database}.dbo.Endpoints SET Status = 11 OUTPUT INSERTED.ID WHERE Name = @EndpointName
			END
			ELSE
			BEGIN
				SELECT ID FROM {database}.dbo.Endpoints WHERE Name = @EndpointName;
			END
        END
        ELSE
        BEGIN
            INSERT INTO {database}.dbo.Endpoints (Name, Description, TokenCheck, Status) 
            OUTPUT INSERTED.ID
            VALUES (@EndpointName, @Description, @TokenCheck, 11);
        END;
        """
        # Insert Endpoints
        self.insert_endpoints = """
        DECLARE @EndpointNames NVARCHAR(MAX) = ?;
        DECLARE @Descriptions NVARCHAR(MAX) = ?;
        DECLARE @TokenChecks NVARCHAR(MAX) = ?;

        WITH EndpointSplit AS (
            SELECT VALUE as EndpointName, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn FROM STRING_SPLIT(@EndpointNames, ',')
        ),
        DescriptionSplit AS (
            SELECT VALUE as Description, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn FROM STRING_SPLIT(@Descriptions, ',')
        ),
        TokenSplit AS (
            SELECT VALUE as TokenCheck, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn FROM STRING_SPLIT(@TokenChecks, ',')
        ),
        JoinTable AS (
            SELECT e.EndpointName, d.Description, T.TokenCheck FROM EndpointSplit as e
            LEFT JOIN DescriptionSplit d ON d.rn = e.rn
            LEFT JOIN TokenSplit t ON t.rn = e.rn
        )
        INSERT INTO {database}.dbo.Endpoints (Name, Description, TokenCheck, Status) OUTPUT INSERTED.ID
        SELECT EndpointName, Description, CAST(TokenCheck AS BIT), 11 FROM JoinTable
        """
        # Update Endpoint
        self.update_endpoint = "UPDATE {database}.dbo.Endpoints SET Name = ?, Description = ?, TokenCheck = ? OUTPUT Inserted.ID WHERE ID = ?"
        # Update Endpoint TokenCheck
        self.update_endpoint_token_check_by_ids = "UPDATE {database}.dbo.Endpoints SET TokenCheck = ? OUTPUT Inserted.ID WHERE ID IN (SELECT CONVERT(INT, value) FROM STRING_SPLIT(?,','))"
        # Update Endpoints Status
        self.update_endpoint_status = "UPDATE {database}.dbo.Endpoints SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT CONVERT(INT, value) FROM STRING_SPLIT( ? , ','))"

        # Endpoint Params Queries
        # Get endpoint params by endpoint ID
        self.get_endpoint_params_by_endpoint_ID = """
            SELECT 
            a.ID, 
            a.ParamID, 
            a.EndpointID, 
            a.Status, 
            a.DefaultValue, 
            b.Name, 
            b.PythonType 
            FROM 
            {database}.dbo.EndpointParamLinks as a 
            LEFT JOIN 
            {database}.dbo.Params as b 
            on 
            b.ID = a.ParamID 
            WHERE 
            a.EndpointID = ? 
            and 
            a.Status = 11
        """
        # Get all endpoint params
        self.get_endpoint_params = (
            "SELECT * FROM {database}.dbo.EndpointParams WHERE Status = 11"
        )
        # Insert Endpoint Param
        # Get all Endpoint Param Links
        self.get_all_endpoint_param_links = """
            SELECT linkTable.ID AS LinkID, endpointTable.ID as EndpointID, endpointTable.Name as EndpointName, paramTable.ID as ParamID, paramTable.Name as ParamName, paramTable.PythonType, linkTable.DefaultValue
            FROM {database}.dbo.EndpointParamLinks linkTable
            LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = linkTable.EndpointID
            LEFT JOIN {database}.dbo.Params paramTable ON paramTable.ID = linkTable.ParamID
            WHERE linkTable.Status = 11 AND endpointTable.Status = 11
        """
        # Update Endpoint Param Link Statuses
        self.update_endpoint_param_link_statuses_by_link_ids = "UPDATE {database}.dbo.EndpointParamLinks SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(CAST(? AS nvarchar(max)), ','))"
        # Get all Params
        self.get_all_params = "SELECT * FROM {database}.dbo.Params"
        # Get param by endpointID
        self.get_params_by_endpoint_id = "SELECT paramTable.* FROM {database}.dbo.EndpointParamLinks linkTable LEFT JOIN {database}.dbo.Params paramTable on paramTable.ID = linkTable.ParamID WHERE linkTable.EndpointID = ?"
        # Create params
        self.insert_params = """
            DECLARE @Names NVARCHAR(MAX) = ?
            DECLARE @Types NVARCHAR(MAX) = ?;
            WITH NAMETABLE AS (
                SELECT VALUE as Name, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn FROM string_split(@Names,',')
            ),
            TYPETABLE AS (
                SELECT VALUE as Type, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn FROM string_split(@Types,',')
            ),
            JOINTABLE as (
                SELECT N.Name, T.Type FROM NAMETABLE N
                LEFT JOIN TYPETABLE T ON N.rn = T.rn
            )
            INSERT INTO {database}.dbo.Params (Name, PythonType) OUTPUT inserted.ID
            SELECT j.Name, j.Type
            FROM JOINTABLE j
            WHERE NOT EXISTS(
                SELECT 1 FROM {database}.dbo.Params p
                WHERE p.Name = j.Name
            )
        """
        # Create param
        # only create param that does not exist in Params table, otherwise return ID of the existing param
        self.insert_param = """
            DECLARE @Name NVARCHAR(MAX) = ?
            DECLARE @Type NVARCHAR(MAX) = ?
            DECLARE @ExistingID INT
            IF NOT EXISTS (
                SELECT 1 
                FROM {database}.dbo.Params AS p 
                WHERE p.Name = @Name
            )
            BEGIN
                INSERT INTO {database}.dbo.Params (Name, PythonType)
                OUTPUT INSERTED.ID
                VALUES (@Name, @Type);
            END
            ELSE
            BEGIN
                SELECT @ExistingID = p.ID
                FROM {database}.dbo.Params AS p 
                WHERE p.Name = @Name;
                SELECT @ExistingID AS ID;
            END
        """
        # Update param
        self.update_param = "UPDATE {database}.dbo.Params SET Name = ?, PythonType = ? OUTPUT INSERTED.ID WHERE ID = ?"

        # Create Endpoint Param Link
        # Input: ParamID, EndpointID, DefaultValue
        self.insert_endpoint_param_link = "INSERT INTO {database}.dbo.EndpointParamLinks (ParamID, EndpointID, DefaultValue, Status) OUTPUT inserted.ID VALUES (?, ?, ?, 11)"
        # Create Endpoint Param Links bulk
        # Input: ParamIDs, EndpointIDs, DefaultValues
        # this query only insert link if there is no combination of paramID and endpointID in the db. if there is, update Status to 11.
        self.insert_endpoint_param_links = """
            DECLARE @ParamIDs NVARCHAR(MAX) = ?
            DECLARE @EndpointIDs NVARCHAR(MAX) = ?
            DECLARE @DefaultValues NVARCHAR(MAX) = ?;

            WITH ParamIDSep AS (
                SELECT VALUE as ParamID, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn  FROM STRING_SPLIT(@ParamIDs, ';')
            ),
            EndpointIDSep AS (
                SELECT VALUE as EndpointID, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn  FROM STRING_SPLIT(@EndpointIDs, ';')
            ),
            DefaultValueSep AS (
                SELECT VALUE as DefaultValue, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rn  FROM STRING_SPLIT(@DefaultValues, ';')
            ),
            JoinAll AS (
                SELECT p.ParamID, e.EndpointID, CASE WHEN d.DefaultValue = '' THEN NULL ELSE d.DefaultValue END AS DefaultValue FROM ParamIDSep p
                LEFT JOIN EndpointIDSep e on e.rn = p.rn
                LEFT JOIN DefaultValueSep d on d.rn = p.rn
            )
            MERGE INTO {database}.dbo.EndpointParamLinks as Target
            USING JoinAll as Source ON Source.ParamID = Target.ParamID AND Source.EndpointID = Target.EndpointID
            WHEN MATCHED AND Target.Status = 12 THEN
                UPDATE SET Target.Status = 11, Target.DefaultValue = Source.DefaultValue
            WHEN NOT MATCHED BY Target THEN
                INSERT (ParamID, EndpointID, DefaultValue, Status)
                VALUES (Source.ParamID, Source.EndpointID, Source.DefaultValue, 11)
            OUTPUT inserted.ID;
        """
        # update Endpoint Param Link
        # Input: defaultValue, ID
        self.update_endpoint_param_link_default_value = "UPDATE {database}.dbo.EndpointParamLinks SET DefaultValue = ? OUTPUT inserted.ID WHERE ID = ?"
        # Update Endpoint Param Links bulk
        # Input: LinkIDs, DefaultValues
        # this query bulk update default value.
        self.update_endpoint_param_link_default_values = """
            DECLARE @linkIDs NVARCHAR(MAX) = ?
            DECLARE @defaultValues NVARCHAR(MAX) = ?;

            WITH linkID_split as (
                SELECT VALUE AS LinkID, ROW_NUMBER() over (ORDER BY (SELECT NULL)) as rn FROM STRING_SPLIT(@linkIDs,',')
            ),
            defaultValue_split as (
                SELECT VALUE AS defaultValue, ROW_NUMBER() over (ORDER BY (SELECT NULL)) as rn FROM STRING_SPLIT(@defaultValues,',')	
            ),
            joinAll as (
                SELECT LinkID, defaultValue from linkID_split ls
                LEFT JOIN defaultValue_split ds ON ds.rn = ls.rn
            )
            MERGE INTO {database}.dbo.EndpointParamLinks as Target
            USING joinAll as Source on Source.LinkID = Target.ID
            WHEN MATCHED THEN
                UPDATE SET DefaultValue = Source.defaultValue
            OUTPUT INSERTED.ID;
        """
        # Update Endpoint Param
        self.update_endpoint_param = "UPDATE {database}.dbo.EndpointParams SET Name = ? OUTPUT Inserted.ID WHERE ID = ?"
        # Update Endpoint Param Status
        self.update_endpoint_params_status = "UPDATE {database}.dbo.EndpointParams SET Status = ? OUTPUT Inserted.ID WHERE ID IN (SELECT CONVERT(INT, value) FROM STRING_SPLIT( ? , ','))"
        # Gets an tokens endpoints
        self.get_token_endpoints_by_token = "SELECT ID, TokenID, EndpointID, Status, Created FROM {database}.dbo.TokenEndpointLinks WHERE TokenID = ?"
        # Gets an tokens endpoints
        self.get_token_endpoint_by_token_and_endpoint = "SELECT TOP 1 ID, TokenID, EndpointID, Status, Created FROM {database}.dbo.TokenEndpointLinks WHERE EndpointID = ? and TokenID = ? and Status in (11)"
        # Gets an tokens endpoints params and overrides
        self.get_token_endpoint_params_by_token_and_endpoint = """
            SELECT 
            a.ID, 
            a.TokenID, 
            b.EndpointID, 
            a.EndpointParamLinkID, 
            a.VerificationID, 
            a.Status, 
            a.Value, 
            a.Created, 
            a.Locked, 
            b.DefaultValue, 
            c.ID as ParamID, 
            c.Name, 
            c.PythonType 
            FROM 
            (
                /* extract most recent paramlink combination to be used */
                select
                MAX(ID) as ID,
                TokenID,
                EndpointParamLinkID
                from
                {database}.dbo.TokenEndpointParamLinks
                WHERE
                TokenID = ?
                and
                Status in (11, 12) --check for active and inactive, but not cancelled instances
                GROUP BY TokenID, EndpointParamLinkID
            ) as d 
            LEFT JOIN
            {database}.dbo.TokenEndpointParamLinks as a
            on
            d.ID = a.ID
            LEFT JOIN 
            {database}.dbo.EndpointParamLinks as b 
            on 
            a.EndpointParamLinkID = b.ID 
            LEFT JOIN 
            {database}.dbo.Params as c 
            on 
            b.ParamID = c.ID
            WHERE
            b.EndpointID = ?
        """
