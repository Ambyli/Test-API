from .config import Config
from .sql_config import SQLConfig


class ProductConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # input: ProductID, Name, Description, VerificationID
        # output: [[KitID]]
        self.insert_product_kit = "INSERT INTO {database}.dbo.ProductKits (Catalog, CustomerID, ProductID, Name, Description, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, ?, GETDATE(), ?, 11)"
        # input: KitID, FileID, VerificationID
        # output: [[LinkID]]
        self.insert_product_kit_file_link = "INSERT INTO {database}.dbo.ProductKitFileLinks (KitID, FileID, FileTypeID, Created, VerificationID, Status, OrderID, Description) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, 11, ?, ?)"
        # input: KitID
        # output: [[KitID]]
        self.update_product_kit_file_link_status = "UPDATE {database}.dbo.ProductKitFileLinks SET Status = ? OUTPUT Inserted.ID WHERE ID in (SELECT value FROM STRING_SPLIT(?, ','))"
        # input: [{KitID, OrderID, Description}]
        # output: [[KitID]]
        self.update_product_kit_file_link_order_and_description = """
            SET NOCOUNT ON 

            declare @json nvarchar(max)
            set @json = ?

            DROP TABLE IF EXISTS #TempFiles 
            CREATE TABLE #TempFiles
            (ID int, OrderID int, [Description] varchar(50))

            insert into #TempFiles
            select
            ID,
            OrderID,
            [Description]
            from
            openjson(@json)
            with
            (
                ID int '$.ID',
                OrderID int '$.OrderID',
                [Description] varchar(50) '$.Description'
            )

            update 
            {database}.dbo.ProductKitFileLinks
            set
            OrderID = Input.OrderID,
            [Description] = Input.[Description]
            output inserted.ID
            from
            {database}.dbo.ProductKitFileLinks
            left join
            #TempFiles as Input
            on
            ProductKitFileLinks.ID = Input.ID
            where
            ProductKitFileLinks.ID in (select ID from #TempFiles)

            DROP TABLE IF EXISTS #TempFiles 
        """
        # input: KitID
        # output: [[KitID]]
        self.update_product_kit_status = "UPDATE {database}.dbo.ProductKits SET Status = ? OUTPUT Inserted.ID WHERE ID in (SELECT value FROM STRING_SPLIT(?, ','))"
        # input: ProductIDs
        # output: [[Kits]]
        self.get_product_kits_by_products = "SELECT ID, Catalog, CustomerID, ProductID, Name, Description, Created, VerificationID, Status FROM {database}.dbo.ProductKits WHERE ProductID in (SELECT value FROM STRING_SPLIT(?, ',')) ORDER BY ProductID DESC, ID DESC"
        # input: ProductIDs
        # output: [[Kits]]
        self.get_all_product_kits = "SELECT ID, Catalog, CustomerID, ProductID, Name, Description, Created, VerificationID, Status FROM {database}.dbo.ProductKits ORDER BY ProductID DESC, ID DESC"
        # input: KitIDs
        # output: [[KitLinks]]
        self.get_product_kit_file_links_by_kits = "SELECT a.ID, a.KitID, a.FileID, a.FileTypeID, a.Created, a.VerificationID, a.Status, b.Path, a.OrderID, a.Description FROM {database}.dbo.ProductKitFileLinks as a LEFT JOIN {database}.dbo.Files as b ON b.ID = a.FileID WHERE a.KitID in (SELECT value FROM STRING_SPLIT(?, ',')) ORDER BY a.KitID DESC, a.ID DESC"
        # input: CaseNumber
        # output: [[Products]]
        self.get_case_products_by_case = "SELECT b.ID, b.CaseID, b.Sequence, a.ProductID, a.Description, (CASE WHEN b.TeethNumbers IS NULL or b.TeethNumbers = '' THEN b.Shade ELSE b.TeethNumbers END) as Shade, b.Quantity, b.UnitPrice, b.ExtendedAmount, b.Discount, b.DiscountRate, b.Remake, b.CreatedBy, a.CreateDate, a.ProductionLab, c.Category, c.FDARegNumber FROM {database}.dbo.Products as a LEFT JOIN {database}.dbo.CaseProducts as b ON a.ProductID = b.ProductID LEFT JOIN {database}.dbo.FDAProducts as c ON a.ProductID = c.ProductID WHERE b.CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?) ORDER BY a.ProductID DESC"
        # input: CustomerID
        # output: [[Products]]
        self.get_products_by_customer_catalog = "SELECT a.ProductID, a.Description, a.CreatedBy, a.CreateDate, a.ProductionLab, b.Category, b.FDARegNumber FROM {database}.dbo.Products as a LEFT JOIN {database}.dbo.FDAProducts as b ON a.ProductID = b.ProductID LEFT JOIN {database}.dbo.CatalogProducts as c ON a.ProductID = c.ProductID WHERE c.Catalog = ? ORDER BY a.ProductID DESC"
        # input: ProductID
        # output: [[Products]]
        self.get_product_by_ID = "SELECT a.ProductID, a.Description, a.CreatedBy, a.CreateDate, a.ProductionLab, b.Category, b.FDARegNumber FROM {database}.dbo.Products as a LEFT JOIN {database}.dbo.FDAProducts as b ON a.ProductID = b.ProductID WHERE a.ProductID = ? ORDER BY a.ProductID DESC"
        # input: AlignerID
        # output: [[FDARegNumber, Category]]
        self.get_product_by_alignerID = "SELECT a.ProductID, a.Description, a.CreatedBy, a.CreateDate, a.ProductionLab, b.Category, b.FDARegNumber FROM {database}.dbo.Products as a LEFT JOIN {database}.dbo.FDAProducts as b ON a.ProductID = b.ProductID WHERE a.ProductID = (SELECT TOP 1 ProductID FROM {database}.dbo.Aligners WHERE AlignerID = ?)"
        self.get_all_product_types = """
            SELECT 
            a.CustomerID, 
            a.ProductMaterialLinkID, 
            a.Status, 
            b.ProductID, 
            b.MaterialID, 
            c.Type, 
            c.Description 
            FROM 
            {database}.[dbo].[LabProductMaterialLinks] as a 
            left join 
            {database}.dbo.ProductMaterialLinks as b 
            on 
            a.ProductMaterialLinkID = b.LinkID 
            left join 
            {database}.dbo.Materials as c 
            on 
            b.MaterialID = c.MaterialID 
            where 
            b.Status = 11 
            AND 
            a.Status = 11 
            ORDER BY CustomerID desc
        """
        self.get_all_products_by_catalogs = """
            SELECT
            CatalogProducts.Catalog,
            CustomerCatalog.CustomerID,
            Products.ProductID,
            Products.Description,
            Products.CreatedBy,
            Products.CreateDate,
            Products.ProductionLab,
            FDAProducts.Category,
            FDAProducts.FDARegNumber
            FROM
            {database}.dbo.Products
            LEFT JOIN
            {database}.dbo.FDAProducts
            ON
            Products.ProductID = FDAProducts.ProductID
            LEFT JOIN
            {database}.dbo.CatalogProducts
            ON
            Products.ProductID = CatalogProducts.ProductID
            OUTER APPLY (
                SELECT 
                LabCustomerSettings.*
                FROM 
                {database}.dbo.LabCustomerSettings
                left join
                {database}.dbo.Catalogs
                on
                LabCustomerSettings.Catalog = Catalogs.Catalog
                WHERE 
                LabCustomerSettings.Catalog = CatalogProducts.Catalog
                and
                Catalogs.Inactive = 0
            ) as CustomerCatalog
            WHERE
            Products.Discontinued = 0
            and
            CustomerCatalog.CustomerID is not null
            ORDER BY CatalogProducts.Catalog asc, CustomerCatalog.CustomerID asc, Products.ProductID asc
        """
