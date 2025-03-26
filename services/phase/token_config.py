from .config import Config
from .sql_config import SQLConfig


# token config
class TokenConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # Token Queries
        self.insert_token = "INSERT INTO {database}.dbo.Tokens (Company, Token, Created, VerificationID, AccountKey, AccountName, Status, TokenTypeID) OUTPUT Inserted.ID, Inserted.Company, Inserted.Token, Inserted.Created, Inserted.VerificationID, Inserted.AccountName, Inserted.AccountKey, Inserted.Status, Inserted.TokenTypeID VALUES (?, ?, GETDATE(), ?, ?, ?, 11, ?)"
        self.get_token = "SELECT TOP 1 ID, Company, Token, Created, AccountKey, AccountName, Status, TokenTypeID FROM {database}.dbo.Tokens where AccountKey = ? and AccountName = ? and Status = 11 and TokenTypeID = ? order by Created desc"
        self.get_token_without_account = "SELECT TOP 1 ID, Company, Token, Created, AccountKey, AccountName, Status, TokenTypeID FROM {database}.dbo.Tokens where Status = 11 and TokenTypeID = ? order by Created desc"
        self.get_tokens_info_by_token = """
            SELECT
            TOP 1
            ID,
            Created,
            VerificationID,
            Company,
            Token,
            AccountKey,
            AccountName,
            Status,
            TokenTypeID
            FROM
            {database}.dbo.Tokens
            WHERE
            Token = ?
            and
            Status in (11)
            ORDER By ID DESC
        """
        self.update_token_status_by_token_ids = "UPDATE {database}.dbo.Tokens SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(?, ','))"
        # Verify owner by token
        self.verify_token_owner = """
            DECLARE @Token NVARCHAR(MAX) = ?;
            DECLARE @EmployeeIDs NVARCHAR(MAX) = ?;

            WITH OwnerTokenCheck AS (
                SELECT TOP (1) ownerTable.ID as OwnerID FROM {database}.dbo.Tokens tokenTable 
                LEFT JOIN {database}.dbo.Employees ownerTable ON ownerTable.TokenID = tokenTable.ID
                WHERE Token = @Token
            ),
            OwnerEmployeeLinksCheck AS (
                SELECT linkTable.EmployeeID, linkTable.OwnerID FROM OwnerTokenCheck ownerTokenTable
                LEFT JOIN {database}.dbo.OwnerEmployeeLinks linkTable ON linkTable.OwnerID = ownerTokenTable.OwnerID
                WHERE EmployeeID IN (SELECT VALUE FROM STRING_SPLIT(@EmployeeIDs, ',')) AND linkTable.Status = 11
            )
            SELECT EmployeeID, OwnerID FROM OwnerEmployeeLinksCheck
        """
        # Verify owner and endpoint then return params
        self.verify_endpoint_and_return_params = """
            DECLARE @OwnerID INT = ?
            DECLARE @EndpointID INT = ?

            SELECT ep.* FROM {database}.dbo.OwnerEndpointLinks oel
            LEFT JOIN {database}.dbo.OwnerEndpointParamLinks oepl ON oel.EndpointID = oepl.EndpointID
            LEFT JOIN {database}.dbo.EndpointParams ep ON ep.ID = oepl.ParamID
            WHERE oel.OwnerID = @OwnerID AND oel.EndpointID = @EndpointID AND oel.Status = 11 AND oepl.Status = 11 AND ep.Status = 11
        """
        # Retrieve SQL Info for the given token
        self.get_sql_info_by_token = "SELECT ID, SqlUserID, TokenID, OwnerVerificationID, Status, (Select name FROM sysusers where uid = SqlUserID) as Username, Password from {database}.dbo.SqlAccounts where TokenID = ?"
        self.get_all_token_endpoint_links = """
            SELECT linkTable.ID as LinkID, endpointTable.ID as EndpointID, endpointTable.Name as EndpointName, tokenTable.ID as TokenID, tokenTable.Token 
            FROM {database}.dbo.TokenEndpointLinks linkTable 
            LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = linkTable.EndpointID
            LEFT JOIN {database}.dbo.Tokens tokenTable ON tokenTable.ID = linkTable.TokenID
            WHERE endpointTable.Status = 11 and linkTable.Status = 11 and tokenTable.Status = 11
        """
        # INSERT TOKEN ENDPOINT LINKS
        # INPUT: TokenID, EndpointIDs as string
        self.insert_token_endpoint_links = "INSERT INTO {database}.dbo.TokenEndpointLinks (TokenID, EndpointID, Status, Created) OUTPUT INSERTED.ID SELECT ?, VALUE, 11, GETDATE() FROM STRING_SPLIT(CAST(? AS NVARCHAR(MAX)), ',')"
        # UPDATE TOKEN ENDPOINT LINK STATUSES
        # INPUT: status. LinkIDs as string
        self.update_token_endpoint_links_statuses_by_ids = "UPDATE {database}.dbo.TokenEndpointLinks SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(CAST(? AS NVARCHAR(MAX)), ','))"
        # GET TOKEN ENDPOINT PARAM LINKS BY EMPLOYEE ID
        self.get_token_endpoint_param_links_by_token = """
            SELECT teplTable.ID as LinkID, teplTable.EndpointParamLinkID, tokenTable.ID as TokenID, endpointTable.ID as EndpointID, paramTable.ID as ParamID, teplTable.Locked, endpointTable.*, paramTable.Name as ParamName, teplTable.Value, paramTable.PythonType, teplTable.Status as LinkStatus 
            FROM {database}.dbo.TokenEndpointParamLinks teplTable
            LEFT JOIN {database}.dbo.Tokens tokenTable ON tokenTable.ID = teplTable.TokenID
            LEFT JOIN {database}.dbo.SqlAccounts empTable ON empTable.TokenID = tokenTable.ID
            LEFT JOIN {database}.dbo.EndpointParamLinks eplTable ON eplTable.ID = teplTable.EndpointParamLinkID
            LEFT JOIN {database}.dbo.Endpoints endpointTable ON endpointTable.ID = eplTable.EndpointID
            LEFT JOIN {database}.dbo.Params paramTable ON paramTable.ID = eplTable.ParamID
            WHERE tokenTable.Token = ? AND teplTable.Status in (6,11) AND tokenTable.Status = 11 AND endpointTable.Status = 11 AND eplTable.Status = 11
            ORDER BY Name ASC
        """
        # INSERT TOKEN ENDPOINT PARAM LINK
        self.insert_token_endpoint_param_link = "INSERT INTO {database}.dbo.TokenEndpointParamLinks (TokenID, EndpointParamLinkID, VerificationID, Status, Value, Created, Locked) OUTPUT INSERTED.ID VALUES (?, ?, ?, 11, ?, GETDATE(), ?)"
        # INSERT TOKEN ENDPOINT PARAM LINKS (BULK) OR
        # UPDATE STATUS TO 11 IF LINK EXIST AND STATUS IS 12
        self.insert_token_endpoint_param_links = """
            DECLARE @TokenID NVARCHAR(MAX) = ?
            DECLARE @EndpointParamLinkIDs NVARCHAR(MAX) = ?
            DECLARE @Values NVARCHAR(MAX) = ?
            DECLARE @Locked NVARCHAR(MAX) = ?
            DECLARE @Verification int = ?;

            WITH LinkIDSplit AS (
                SELECT VALUE AS LinkID, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as rn FROM STRING_SPLIT(@EndpointParamLinkIDs, ',')
            ),
            ValueSplit AS (
                SELECT CASE WHEN VALUE = 'None' THEN NULL ELSE VALUE END AS Value, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as rn FROM STRING_SPLIT(@Values, ',')
            ),
            LockedSplit AS (
                SELECT CAST(VALUE AS INT) AS Locked, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as rn FROM STRING_SPLIT(@Locked, ',')
            ),
            JoinTables AS (
                SELECT @TokenID AS TokenID, linkTable.LinkID, @Verification as Verification, valueTable.Value, lockedTable.Locked FROM LinkIDSplit linkTable
                LEFT JOIN ValueSplit valueTable ON valueTable.rn = linkTable.rn
                LEFT JOIN LockedSplit lockedTable ON lockedTable.rn = linkTable.rn
            )
            -- set target as TokenEndpointParamLinks table
			MERGE INTO {database}.dbo.TokenEndpointParamLinks as Target
			-- using JoinTables as source to check if item exist or not
			USING JoinTables as Source ON Source.TokenID = Target.TokenID AND Source.LinkID = Target.EndpointParamLinkID
			-- if item exist and status is 12 -> update to 11
			WHEN MATCHED AND Target.Status = 12 THEN
				UPDATE SET Target.Status = 11
			-- if item does not exist -> create
			WHEN NOT MATCHED BY TARGET THEN
				INSERT (TokenID, EndpointParamLinkID, VerificationID, Status, Value, Created, Locked)
				VALUES (Source.TokenID, Source.LinkID, Verification, 11, Source.Value, GETDATE(), Source.Locked)
			OUTPUT INSERTED.ID;
        """
        self.update_token_endpoint_param_links_by_ids = "UPDATE {database}.dbo.TokenEndpointParamLinks SET Value = ?, Locked = ? OUTPUT INSERTED.ID WHERE ID = ?"
        # UPDATE TOKEN ENDPOINT PARAM LINK STATUSES
        # INPUT: status. LinkIDs as string
        self.update_token_endpoint_param_links_statuses_by_ids = "UPDATE {database}.dbo.TokenEndpointParamLinks SET Status = ? OUTPUT INSERTED.ID WHERE ID IN (SELECT VALUE FROM STRING_SPLIT(CAST(? AS NVARCHAR(MAX)), ','))"
