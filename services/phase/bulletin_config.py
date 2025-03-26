from .config import Config
from .sql_config import SQLConfig


# bulletin config
class BulletinConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Get All Bulletin
        self.get_all_bulletin = (
            "SELECT * FROM {database}.dbo.Bulletin ORDER BY CREATED DESC"
        )

        # # filter Bulletin
        # Input: tags "ID,ID,ID", searchKeyword "str", createdFrom "2022-01-19 00:00:00.000", createdTo "2022-01-19 00:00:00.000", VerificationID, sortOrder "DESC", offset int, rows int
        # Output: List of Bulletins
        self.filter_bulletin = """
            SELECT 
            * 
            FROM 
            (
                SELECT 
                d.ID as ID, 
                d.Title, 
                d.Body, 
                d.Created, 
                d.ExpireDate, 
                d.VerificationID, 
                eb.FirstName, 
                eb.LastName, 
                eb.EmployeeID, 
                d.[Status], 
                tg.ID as TagID, 
                tg.Tag, 
                dtg.ID as LinkID, 
                ROW_NUMBER() OVER (ORDER BY CASE ? WHEN 'DESC' THEN d.Created END DESC, d.Created ASC) as RowNumber 
                FROM 
                {database}.[dbo].[Bulletin] as d 
                LEFT JOIN 
                {database}.[dbo].[BulletinTagLinks] as dtg 
                ON 
                d.ID = dtg.BulletinID 
                LEFT JOIN 
                {database}.[dbo].[Tags] as tg 
                ON 
                dtg.TagID = tg.ID
                OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = d.VerificationID ORDER BY ID DESC) as vel 
                LEFT JOIN 
                {database}.dbo.Employees eb 
                ON 
                eb.EmployeeID = vel.EmployeeID 
                WHERE 
                d.[Status] = 11 
                AND 
                (
                    dtg.[Status] = 11 
                    OR 
                    dtg.[Status] IS NULL
                ) 
                AND 
                (
                    ? IS NULL 
                    OR 
                    TagID IN (SELECT CONVERT(INT,value) FROM STRING_SPLIT(?,','))) 
                    AND 
                    (
                        ? IS NULL 
                        OR 
                        [Title] LIKE '%'+?+'%'
                    ) 
                    AND 
                    (
                        ? IS NULL 
                        OR 
                        d.[Created] >= CONVERT(datetime, ?)
                    ) 
                    AND 
                    (
                        ? IS NULL 
                        OR 
                        d.[Created] <= CONVERT(datetime, ?)
                    ) 
                    AND 
                    (
                        ? IS NULL 
                        OR 
                        d.[VerificationID] = ?
                    )
                ) as Aligners 
                WHERE 
                RowNumber 
                BETWEEN ? + 1 AND ? + ?
        """

        # # Filter Unexpired Bulletins with Tags ORDER by expire short to long
        # Input: TagIDs x2, Order by Column only "Created" or "ExpireLength" x2
        # Output: List of Bulletin
        self.filter_unexpired_bulletin = "SELECT * FROM (SELECT d.ID as ID, d.Title, d.Body, d.Created, d.ExpireDate, (ExpireDate - CURRENT_TIMESTAMP) as ExpireLength, d.VerificationID, eb.FirstName, eb.LastName, d.Status, dtl.ID as LinkID, dtl.Status as LinkStatus, dtl.TagID, tg.Tag FROM {database}.dbo.Bulletin d LEFT JOIN {database}.dbo.BulletinTagLinks dtl ON dtl.BulletinID = d.ID LEFT JOIN {database}.dbo.Tags tg ON dtl.TagID = tg.ID OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = d.VerificationID ORDER BY ID DESC) as vel LEFT JOIN {database}.dbo.Employees eb ON eb.EmployeeID = vel.EmployeeID WHERE d.Status = 11 AND dtl.Status = 11 AND ExpireDate > CURRENT_TIMESTAMP AND (? IS NULL OR TagID IN (SELECT CONVERT(INT,value) FROM STRING_SPLIT(?,',')))) AS A ORDER BY  CASE ? WHEN 'ExpireLength' THEN [ExpireLength] WHEN 'Created' THEN [Created] END ASC"

        # # Get Bulletin by ID
        # Input: ID
        # Output: Bulletin object
        self.get_bulletin_by_ID = "SELECT d.[ID], d.[Title], d.[Body], d.[Created], d.[ExpireDate], d.[VerificationID], eb.FirstName, eb.LastName, eb.EmployeeID, d.[Status], tg.ID as TagID, tg.[Tag], dtg.[ID] as TagLinkID, dtg.[Status] FROM {database}.[dbo].[Bulletin] d LEFT JOIN {database}.[dbo].[BulletinTagLinks] dtg ON d.ID = dtg.BulletinID LEFT JOIN {database}.[dbo].[Tags] tg ON dtg.TagID = tg.ID OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = d.VerificationID ORDER BY ID DESC) as vel LEFT JOIN {database}.dbo.Employees eb ON eb.EmployeeID = vel.EmployeeID WHERE d.ID = ? AND dtg.Status = 11"

        # # Get Latest Bulletin at each TagID
        # Output: List of Bulletin
        self.get_latest_bulletin_at_each_tag = "SELECT * FROM ( SELECT d.ID as ID, d.Title, d.Body, d.Created, d.[ExpireDate], d.VerificationID, eb.FirstName, eb.LastName, eb.EmployeeID, d.[Status], dtl.ID as LinkID, dtl.[Status] as LinkStatus, dtl.TagID, tg.Tag, ROW_NUMBER() OVER (PARTITION BY dtl.TagID ORDER BY d.Created DESC) AS rn	FROM {database}.dbo.Bulletin d LEFT JOIN {database}.dbo.BulletinTagLinks dtl ON dtl.BulletinID = d.ID LEFT JOIN {database}.dbo.Tags tg ON dtl.TagID = tg.ID OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = d.VerificationID ORDER BY ID DESC) as vel LEFT JOIN {database}.dbo.Employees eb ON eb.EmployeeID = vel.EmployeeID WHERE d.[Status] = 11 AND dtl.[Status] = 11) t WHERE rn = 1"

        # # Get Tags
        # Output: List of Tags
        self.get_tags = "SELECT * FROM {database}.dbo.Tags"

        # # Get Tag by ID
        # Input: ID
        # Output: Tag object
        self.get_tag_by_ID = "SELECT * FROM {database}.dbo.Tags WHERE ID = ?"

        # # Get All Links
        # Output: List of Links
        self.get_all_bulletin_tag_link = "SELECT * FROM {database}.dbo.BulletinTagLinks"

        # # Get Bulletin Tag Link by ID
        # Input: ID
        # Output:  Bulletin Tag Link object
        self.get_bulletin_tag_link_by_ID = (
            "SELECT * FROM {database}.dbo.BulletinTagLinks WHERE ID = ?"
        )

        # # Get Bulletin Tag Links by Bulletin ID
        # Input: Bulletin ID
        self.get_bulletin_tag_links_by_bulletinID = "SELECT dtg.[ID], dtg.[BulletinID], dtg.[TagID], dtg.[Status], t.[Tag] FROM {database}.[dbo].[BulletinTagLinks] dtg LEFT JOIN {database}.[dbo].[Tags] t ON T.ID = dtg.TagID WHERE BulletinID = ?"

        # # Insert Bulletin
        # Input: Title, Body, Created, VerificationID, Status
        # Output: Bulletin ID
        self.insert_bulletin = "INSERT INTO {database}.dbo.Bulletin (Title, Body, Created, VerificationID, Status, ExpireDate) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?, ?)"

        # # Insert Tag
        # Input: Tags "ID,ID,ID"
        # Output: Bulletin ID
        self.insert_tags = "INSERT INTO {database}.dbo.Tags (Tag) OUTPUT inserted.ID SELECT VALUE FROM STRING_SPLIT(?,',')"

        # # Insert Bulletin Tag Links
        # Input: BulletinID int, Status int, TagIDs "ID,ID,ID"
        # Output: Bulletin ID
        self.insert_bulletin_tag_links = "INSERT INTO {database}.[dbo].[BulletinTagLinks] ([BulletinID], [Status], [TagID], [Created], [VerificationID]) OUTPUT inserted.ID as LinkID SELECT ?, ?, CONVERT(VARCHAR(MAX),value), GETDATE(), ? FROM STRING_SPLIT(?,',')"

        # # Update Bulletin
        # Input: Title, Body, Status, ID
        # Output: Bulletin ID
        self.update_bulletin = "UPDATE {database}.dbo.Bulletin SET Title = ? ,Body = ?, ExpireDate = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Update Bulletin Status
        # Input: ID
        # Output: Bulletin ID
        self.update_bulletin_status = "UPDATE {database}.dbo.Bulletin SET Status = ? OUTPUT inserted.ID WHERE ID = ?"

        # # Update Bulletin Tag Links Status
        # Input: StatusID, TagID
        # Output: Bulletin Tag Links ID
        self.update_bulletin_tag_link_status = "UPDATE {database}.dbo.BulletinTagLinks SET Status = ? OUTPUT inserted.ID as LinkID WHERE ID IN (SELECT CONVERT(INT, value) FROM STRING_SPLIT( ? , ','))"

        # # Update Tag
        # Input: Tag, TagID
        # Output: TagID
        self.update_tag = (
            "UPDATE {database}.dbo.Tags SET Tag = ? OUTPUT inserted.ID WHERE ID = ?"
        )

        # # Delete Tag
        # Input: TagID
        self.delete_tag = (
            "DELETE FROM {database}.dbo.Tags WHERE ID = ? AND ID IS NOT NULL"
        )

        # # Delete bulletin tag links
        # Input: LinkIDs
        self.delete_bulletin_tag_link = "DELETE FROM {database}.dbo.BulletinTagLinks WHERE ID IN (SELECT CONVERT(INT, value) FROM STRING_SPLIT( ? , ','))"

        # # Bulletin File Links

        # # Get All Bulletin File Links
        self.get_bulletin_file_links = "SELECT * FROM {database}.dbo.BulletinFileLinks"

        # # Get Bulletin File Links by ID
        self.get_bulletin_file_links_by_id = "SELECT dfl.ID, dfl.BulletinID, dfl.FileID, dfl.FileTypeID, dfl.Created, dfl.VerificationID, dfl.Status, f.Path FROM {database}.dbo.BulletinFileLinks dfl LEFT JOIN {database}.dbo.Files f ON f.id = dfl.FileID WHERE dfl.ID = ?"

        # # Get Bulletin File Links by Bulletin
        self.get_bulletin_file_links_by_bulletin = "SELECT dfl.ID, dfl.BulletinID, dfl.FileID, dfl.FileTypeID, dfl.Created, dfl.VerificationID, dfl.Status, f.Path FROM {database}.dbo.BulletinFileLinks dfl LEFT JOIN {database}.dbo.Files f ON f.id = dfl.FileID WHERE BulletinID = ?"

        # # Create Bulletin File Link
        # Input: BulletinID , VerificationID, Status, FileID ,FileTypeID
        self.create_bulletin_file_links = "INSERT INTO {database}.dbo.BulletinFileLinks (BulletinID, FileID, FileTypeID, Created, VerificationID, [Status]) OUTPUT inserted.ID, inserted.FileID, inserted.FileTypeID as typeID VALUES (?, ?, ?, GETDATE(), ?, 11)"

        # # Update Bulletin File Link Status
        # Input: Status, ID
        self.update_bulletin_file_link_status = "UPDATE {database}.dbo.BulletinFileLinks SET Status = ? OUTPUT inserted.ID WHERE ID IN (SELECT value FROM STRING_SPLIT( ? , ','))"
