from .config import Config
from .sql_config import SQLConfig


# case config
class CaseConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Case functions
        self.lookup_template = """
            WITH
            case_info as
            (
                SELECT
                cases.CaseNumber,
                cases.CustomerID,
                cases.PanNumber,
                cases.Status,
                cases.RXNumber as PatientID,
                cases.DoctorName,
                -- Acquire the serial number whether it is inserted in PatientChart or DigitalScanner
                (
                    CASE
                        WHEN cases.PatientChart is NULL
                        THEN 
                            cases.DigitalScanner
                        ELSE 
                            cases.PatientChart
                    END
                ) as Serial,
                cases.PatientLast,
                cases.PatientFirst,
                cases.ShipDate,
                cases.InvoiceDate,
                cases.InvoicedBy,
                cases.CaseID,
                cases.CreateDate,
                cases.CreatedBy,
                cases.Deleted,
                cases.DueDate,
                cases.LabName,
                labsettings.Catalog,
                caseproducts.ProductID,
                cases.Shade as GrandShade,
                -- Acquire the last submission date for the given case
                (SELECT MAX(Created) as created FROM {{database}}.dbo.Stations where CaseID = cases.CaseID) as LastSubmission,
                -- Concat all fixits into a single string for the given case
                (SELECT STRING_AGG(case when [Status] = 2 then FixitID else null end, ',') FROM {{database}}.dbo.Fixits WHERE CaseID = cases.CaseID) AS Fixits,
                -- Concat all flags into a single string for the given case
                (SELECT STRING_AGG(case when [Status] = 11 then FlagID else null end, ',') FROM {{database}}.dbo.CaseFlagLinks WHERE CaseNumber = cases.CaseNumber) AS Flags,
                -- Acquire the products shade whether it is inserted in TeethNumbers or Shade
                (
                    CASE
                        WHEN caseproducts.TeethNumbers IS NULL or caseproducts.TeethNumbers = ''
                        THEN
                            caseproducts.Shade
                        ELSE
                            caseproducts.TeethNumbers
                    END
                ) as Shade,
                COUNT(aligners.AlignerID) as Units,
                -- Calculate the completion percentage of the case based on the location's weight
                (Case WHEN aligners.Status = 2 then ISNULL(AVG(locations.Weight), 0) else null end) as Completion,
                -- Combine all locations into a single string for the given case's product where active
                (SELECT STRING_AGG([Location], ',') FROM (SELECT DISTINCT [Location] FROM {{database}}.dbo.Aligners as b WHERE cases.CaseID = b.CaseID and caseproducts.ProductID = b.ProductID and b.Status = 2) as a) as Locations,
                caseproducts.Quantity,
                -- Acquire the total quantity of the products that are linked to the materials, this is to not include product quantities that aren't related to aligners
                (SELECT SUM(Quantity) FROM (SELECT b.ProductID, b.Quantity FROM {{database}}.dbo.CaseProducts as b left join {{database}}.dbo.Products as c on b.ProductID = c.ProductID WHERE cases.CaseID = b.CaseID and b.ProductID in (SELECT DISTINCT ProductID FROM {{database}}.dbo.ProductMaterialLinks)) as a) as TotalQuantity,
                caseproducts.CreateDate as ProductCreateDate,
                caseproducts.CreatedBy as ProductCreatedBy,
                products.Description as ProductDescription,
                products.UnitPrice,
                aligners.FixitID,
                aligners.FixitCID
                FROM
                {{database}}.dbo.CaseProducts as caseproducts
                join
                {{database}}.dbo.Cases as cases
                on
                caseproducts.CaseID = cases.CaseID
                join
                {{database}}.dbo.Products as products
                on
                caseproducts.ProductID = products.ProductID
                left join
                {{database}}.dbo.Aligners as aligners
                on
                caseproducts.CaseID = aligners.CaseID and aligners.Status in (2,4)
                and
                products.ProductID = aligners.ProductID
                left join
                {{database}}.dbo.Locations as locations
                on
                aligners.[Location] = locations.ID
                left join
                {{database}}.dbo.LabCustomerSettings as labsettings
                on
                cases.CustomerID = labsettings.CustomerID
                {0}
                GROUP BY cases.CaseNumber, cases.CustomerID, cases.PanNumber, cases.[Status], cases.RXNumber, cases.DoctorName, cases.PatientChart, cases.DigitalScanner, cases.PatientLast, cases.PatientFirst, cases.ShipDate, cases.DueDate, cases.InvoiceDate, cases.InvoicedBy, cases.LabName, cases.CaseID, cases.CreateDate, cases.CreatedBy, cases.Deleted, caseproducts.ProductID, cases.Shade, caseproducts.TeethNumbers, caseproducts.Shade, caseproducts.Quantity, caseproducts.CreateDate, caseproducts.CreatedBy, products.[Description], products.UnitPrice, aligners.Status, aligners.FixitID, aligners.FixitCID, labsettings.Catalog
            )
            SELECT
            CaseNumber,
            CustomerID,
            PanNumber,
            Status,
            PatientID,
            DoctorName,
            Serial,
            PatientLast,
            PatientFirst,
            DueDate,
            ShipDate,
            InvoiceDate,
            InvoicedBy,
            CaseID,
            CreateDate,
            CreatedBy,
            Deleted,
            -- Calculate the days late the case is from its shipdate
            (SELECT datediff(day, ShipDate, GETDATE())) as [Days Late],
            ProductID,
            GrandShade,
            Shade,
            Units,
            Completion,
            Quantity,
            TotalQuantity,
            Fixits,
            Flags,
            LastSubmission,
            Locations,
            LabName,
            Catalog,
            -- Cacluate time case is waiting at a given station
            (SELECT DATEDIFF(MINUTE, CONVERT(datetime, (LastSubmission)), CONVERT(datetime, GETDATE()))) as Waiting,
            FixitID,
            FixitCID
            FROM
            case_info as inner_query
            
            {1}
            {2}
        """
        self.lookup_with_row_offset = (
            self.lookup_template + " OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        )
        self.case_filters = {
            "case": {
                "OUTER_WHERE": "CHARINDEX('{0}', CaseNumber) > 0",
            },
            "shade": {
                "OUTER_WHERE": "CHARINDEX('{0}', Shade) > 0",
                "ORDER": "Shade DESC",
            },
            "customer": {
                "OUTER_WHERE": "CHARINDEX('{0}', CustomerID) > 0",
                "ORDER": "CustomerID DESC",
            },
            "pan": {
                "OUTER_WHERE": "CHARINDEX('{0}', PanNumber) > 0",
                "ORDER": "PanNumber DESC",
            },
            "pid": {
                "OUTER_WHERE": "CHARINDEX('{0}', PatientID) > 0",
                "ORDER": "PatientID DESC",
            },
            "lastname": {
                "OUTER_WHERE": "CHARINDEX('{0}', PatientLast) > 0",
                "ORDER": "PatientLast DESC",
            },
            "firstname": {
                "OUTER_WHERE": "CHARINDEX('{0}', PatientFirst) > 0",
                "ORDER": "PatientFirst DESC",
            },
            "due": {
                "OUTER_WHERE": "CHARINDEX('{0}', DueDate) > 0",
                "ORDER": "DueDate DESC",
            },
            "ship": {
                "OUTER_WHERE": "CHARINDEX('{0}', ShipDate) > 0",
                "ORDER": "ShipDate DESC",
            },
            "invoice": {
                "OUTER_WHERE": "CHARINDEX('{0}', Invoiced) > 0",
                "ORDER": "Invoiced DESC",
            },
            "invoiceby": {
                "OUTER_WHERE": "CHARINDEX('{0}', InvoicedBy) > 0",
                "ORDER": "InvoicedBy DESC",
            },
            "isnotinvoiced": {"OUTER_WHERE": "Invoiced is NULL"},
            "created": {
                "OUTER_WHERE": "CHARINDEX('{0}', CreateDate) > 0",
                "ORDER": "CreateDate DESC",
            },
            "createdby": {
                "OUTER_WHERE": "CHARINDEX('{0}', CreatedBy) > 0",
                "ORDER": "CreatedBy DESC",
            },
            "late": {"OUTER_WHERE": "[Days Late] = {0}"},
            "extra": {
                "ORDER": "(SELECT datediff(day, DueDate, GETDATE())) DESC",
            },
            "shipdaterange": {
                "OUTER_WHERE": "(DATEDIFF(SECOND, '{0}', ShipDate) >= 0 and DATEDIFF(SECOND, '{1}', ShipDate) <= 0)"
            },
            "invoicedaterange": {
                "OUTER_WHERE": "(DATEDIFF(SECOND, '{0}', InvoiceDate) >= 0 and DATEDIFF(SECOND, '{1}', InvoiceDate) <= 0)"
            },
            "status": {
                "OUTER_WHERE": "(Status = '{0}')",
                "ORDER": "Status ASC",
            },
            "deleted": {"OUTER_WHERE": "Deleted = 0"},
            "units": {"OUTER_WHERE": "(Units = {0})"},
            "caseorder": {
                "ORDER": "CaseNumber DESC",
            },
            "product": {
                "OUTER_WHERE": "CHARINDEX('{0}', ProductID) > 0",
                "ORDER": "ProductID DESC",
            },
            "production": {
                "INNER_WHERE": "(aligners.Status in (2, 4)) or (aligners.[Location] IS NULL)",
            },
            "cad": {
                "INNER_WHERE": "(aligners.[Location] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 23, 34, 35, 36, 37, 47, 63, 64)) or (aligners.[Location] IS NULL)",
                "ORDER": "[Days Late] DESC",
            },
            "carbon": {
                "INNER_WHERE": "(aligners.[Location] in (35, 36, 12) and aligners.Status in (2, 4))",
                "OUTER_WHERE": "((SELECT SUM(Units) FROM case_info as temporary WHERE temporary.CaseID = inner_query.CaseID and temporary.ProductID = inner_query.ProductID) = Quantity)",
                "ORDER": "[Days Late] DESC",
            },
            "test": {
                "INNER_WHERE": "aligners.[Location] in ({0}, {1})",
                "OUTER_WHERE": "(Status = '{0}')",
                "ORDER": "[Days Late] DESC",
            },
            "alignerstatus": {"INNER_WHERE": "aligners.Status in (2, 4)"},
            "hasShipDate": {"OUTER_WHERE": "ShipDate IS NOT NULL"},
            "shadecheck": {"OUTER_WHERE": "Shade IS NOT NULL and Shade != ''"},
            "fixitlimit": {"INNER_WHERE": "aligners.FixitCID IS NOT NULL"},
            "nofixit": {"INNER_WHERE": "aligners.FixitCID IS NULL"},
            "ncgeneration": {
                "INNER_WHERE": "(SELECT COUNT(History) FROM (SELECT DISTINCT LocationID as History FROM {database}.dbo.Stations WHERE AlignerID = aligners.AlignerID and [Status] in (11) and LocationID in (35, 34)) as inner_query) = 2 and (SELECT COUNT(AlignerID) as History FROM {database}.dbo.Stations WHERE AlignerID = aligners.AlignerID and [Status] in (11) and LocationID in (45, 46)) = 0",
                "OUTER_WHERE": "((SELECT SUM(Units) FROM case_info as temporary WHERE temporary.CaseID = inner_query.CaseID and temporary.ProductID = inner_query.ProductID) = Quantity)",
                "ORDER": "[Days Late] DESC",
            },
            "rlineflag": {
                "INNER_WHERE": "(SELECT COUNT(ID) FROM {database}.dbo.CaseFlagLinks WHERE CaseNumber = cases.CaseNumber and FlagID in (10) and [Status] in (11)) > 0"
            },
            "inteware": {
                "INNER_WHERE": "(aligners.[Location] in (47) and aligners.Status in (2, 4))",
                "ORDER": "[Days Late] DESC",
            },
            "intewarelaser": {
                "INNER_WHERE": "((aligners.[Location] in (9) and aligners.Status in (2, 4)) or (aligners.[Location] IS NULL)) and (SELECT COUNT(AlignerID) as History FROM {database}.dbo.Stations WHERE AlignerID = aligners.AlignerID and [Status] in (11) and LocationID in (9, 11)) = 0",
                "ORDER": "[Days Late] DESC",
            },
            "intewareflag": {
                "INNER_WHERE": "(SELECT COUNT(ID) FROM {database}.dbo.CaseFlagLinks WHERE CaseNumber = cases.CaseNumber and FlagID in (20) and [Status] in (11)) > 0"
            },
        }
        # input: CaseIDs
        # output: [[CaseID, CaseNumber, Shade]]
        self.phase_case_query = """
            SELECT
            *
            FROM
            {database}.dbo.Cases
            WHERE
            CaseID in (SELECT value FROM STRING_SPLIT(?, ','))
        """
        # input: CaseIDs
        # output: [[CaseID, CaseNumber, Shade]]
        self.ids_query = """
            SELECT 
            cases.CaseID, 
            cases.CaseNumber, 
            cases.Shade, 
            cases.CustomerID, 
            cases.PanNumber, 
            cases.Status,
            cases.RXNumber as PatientID, 
            cases.DoctorName, 
            (CASE WHEN cases.PatientChart is NULL THEN cases.DigitalScanner ELSE cases.PatientChart END) as Serial, 
            cases.PatientLast, 
            cases.PatientFirst,
            cases.DueDate,
            cases.ShipDate,
            cases.InvoiceDate,
            cases.InvoicedBy,
            cases.CaseID,
            cases.CreateDate,
            cases.CreatedBy,
            cases.LabName,
            labsettings.Catalog,
            (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) as [Days Late], 
            cases.WorkOrderNotes,
            CONCAT(cases.ShipAddress1, COALESCE(cases.ShipAddress2, ''),', ', cases.ShipCity, ' ', cases.ShipState, ', ', cases.ShipCountry, ' ', cases.ShipZipCode) as 'ShipAddress',
            phasecases.LocationID
            FROM 
            {database}.dbo.Cases as cases 
            left join
            {database}.dbo.CasePairings as phasecases
            on
            cases.CaseID = phasecases.CaseID
            left join
            {database}.dbo.LabCustomerSettings as labsettings
            on
            labsettings.CustomerID = cases.CustomerID
            WHERE 
            cases.CaseID in (SELECT value FROM STRING_SPLIT(?, ','))
        """
        # input: CaseID
        # output: [[CaseID, CaseNumber, Shade]]
        self.id_query = """
            SELECT 
            cases.CaseID, 
            cases.CaseNumber, 
            cases.Shade, 
            cases.CustomerID, 
            cases.PanNumber, 
            cases.Status,
            cases.RXNumber as PatientID, 
            cases.DoctorName, 
            (CASE WHEN cases.PatientChart is NULL THEN cases.DigitalScanner ELSE cases.PatientChart END) as Serial, 
            cases.PatientLast, 
            cases.PatientFirst,
            cases.DueDate,
            cases.ShipDate,
            cases.InvoiceDate,
            cases.InvoicedBy,
            cases.CaseID,
            cases.CreateDate,
            cases.CreatedBy,
            cases.LabName,
            labsettings.Catalog,
            (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) as [Days Late], 
            cases.WorkOrderNotes,
            CONCAT(cases.ShipAddress1, COALESCE(cases.ShipAddress2, ''),', ', cases.ShipCity, ' ', cases.ShipState, ', ', cases.ShipCountry, ' ', cases.ShipZipCode) as 'ShipAddress',
            phasecases.LocationID
            FROM 
            {database}.dbo.Cases as cases 
            left join
            {database}.dbo.CasePairings as phasecases
            on
            cases.CaseID = phasecases.CaseID
            left join
            {database}.dbo.LabCustomerSettings as labsettings
            on
            labsettings.CustomerID = cases.CustomerID
            WHERE
            cases.CaseID = ?
        """
        # input: CaseNumber
        # output: [[CaseID, CaseNumber, Shade]]
        self.case_query = """
            SELECT 
            cases.CaseID, 
            cases.CaseNumber, 
            cases.Shade, 
            cases.CustomerID, 
            cases.PanNumber, 
            cases.Status,
            cases.RXNumber as PatientID, 
            cases.DoctorName, 
            (CASE WHEN cases.PatientChart is NULL THEN cases.DigitalScanner ELSE cases.PatientChart END) as Serial, 
            cases.PatientLast, 
            cases.PatientFirst,
            cases.DueDate,
            cases.ShipDate,
            cases.InvoiceDate,
            cases.InvoicedBy,
            cases.CaseID,
            cases.CreateDate,
            cases.CreatedBy,
            cases.LabName,
            labsettings.Catalog,
            (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) as [Days Late], 
            cases.WorkOrderNotes,
            CONCAT(cases.ShipAddress1, COALESCE(cases.ShipAddress2, ''),', ', cases.ShipCity, ' ', cases.ShipState, ', ', cases.ShipCountry, ' ', cases.ShipZipCode) as 'ShipAddress',
            phasecases.LocationID
            FROM 
            {database}.dbo.Cases as cases 
            left join
            {database}.dbo.CasePairings as phasecases
            on
            cases.CaseID = phasecases.CaseID
            left join
            {database}.dbo.LabCustomerSettings as labsettings
            on
            labsettings.CustomerID = cases.CustomerID
            WHERE 
            cases.CaseNumber = ?
        """
        # input: CaseNumber
        # output: [[ProductID, Shade, Quantity, CustomerID]]
        self.product_query = "SELECT b.ProductID, (CASE WHEN b.TeethNumbers IS NULL or b.TeethNumbers = '' THEN b.Shade ELSE b.TeethNumbers END) as Shade, b.Quantity, a.CustomerID FROM {database}.dbo.Cases as a, {database}.dbo.CaseProducts as b WHERE a.CaseID = b.CaseID and a.CaseNumber = ?"
        # input: Date, Range, Offset, Row
        # output [[CaseNumber, Shade, CustomerID, PanNumber, Status, PatientID, DoctorName, Serial, PatientLast, PatientFirst, DueDate, ShipDate, InvoiceDate, InvoicedBy, CaseID, CreateDate, CreatedBy, DaysLate]]
        self.get_cases_by_range = """
            SELECT 
            cases.CaseNumber, 
            cases.CaseID,
            cases.Shade,
            cases.CustomerID,
            cases.PanNumber,
            cases.Status,
            cases.RXNumber as PatientID,
            cases.DoctorName,
            (CASE WHEN cases.PatientChart is NULL THEN cases.DigitalScanner ELSE cases.PatientChart END) as Serial,
            cases.PatientLast,
            cases.PatientFirst,
            cases.DueDate,
            cases.ShipDate,
            cases.InvoiceDate,
            cases.InvoicedBy,
            cases.CreateDate,
            cases.CreatedBy,
            cases.LabName,
            labsettings.Catalog,
            (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) as [Days Late],
            b.VerificationID 
            FROM 
            {database}.dbo.Cases as cases 
            left join
            {database}.dbo.LabCustomerSettings as labsettings
            on
            labsettings.CustomerID = cases.CustomerID
            WHERE 
            DATEDIFF(day, ?, CONVERT(datetime, cases.ShipDate)) >= ? 
            and
            DATEDIFF(day, ?, CONVERT(datetime, cases.ShipDate)) <= 0 
            ORDER BY cases.CreateDate ASC, (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) DESC
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
        """
        self.get_cases_by_range_by_case = """
            SELECT
            cases.CaseNumber,
            cases.CaseID,
            cases.Shade, 
            cases.CustomerID, 
            cases.PanNumber, 
            cases.Status,
            cases.RXNumber as PatientID, 
            cases.DoctorName, 
            (CASE WHEN cases.PatientChart is NULL THEN cases.DigitalScanner ELSE cases.PatientChart END) as Serial, 
            cases.PatientLast, 
            cases.PatientFirst, 
            cases.DueDate, 
            cases.ShipDate, 
            cases.InvoiceDate, 
            cases.InvoicedBy, 
            cases.CreateDate, 
            cases.CreatedBy, 
            cases.LabName,
            labsettings.Catalog,
            (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) as [Days Late], 
            b.VerificationID 
            FROM 
            {database}.dbo.Cases as cases 
            left join
            {database}.dbo.LabCustomerSettings as labsettings
            on
            labsettings.CustomerID = cases.CustomerID
            WHERE 
            CHARINDEX(?, CaseNumber) > 0 
            ORDER BY CaseNumber DESC, (SELECT DATEDIFF(day, cases.DueDate, GETDATE())) DESC 
            OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY
        """
        # input: StartDate, EndDate, Offset, Rows
        # output: [[CaseNumbers, Shades, Dates, Cases, Name]]
        self.get_duplicate_cases_by_shade_patientname = "WITH CasesInRange as (SELECT TOP 1000 *, concat(PatientLast, ', ', PatientFirst) as [Name] FROM {database}.dbo.Cases WHERE (DATEDIFF(SECOND, ?, ShipDate) >= 0 and DATEDIFF(SECOND, ?, ShipDate) <= 0) and ([Status] = 'In Production' or [Status] = 'Invoiced') and Deleted = 0 ORDER BY CaseNumber DESC) SELECT * FROM (SELECT stuff((SELECT ',' + Cast(CaseNumber as varchar(12)) FROM CasesInRange WHERE [Name] = a.[Name] and Shade = a.Shade for xml path ('')), 1, 1, '') as CaseNumbers, stuff((SELECT ',' + Cast(Shade as varchar(12)) FROM CasesInRange WHERE [Name] = a.[Name] and Shade = a.Shade for xml path ('')), 1, 1, '') as Shades, stuff((SELECT ',' + Cast(CreateDate as varchar(24)) FROM CasesInRange WHERE [Name] = a.[Name] and Shade = a.Shade for xml path('')), 1, 1, '') as CreationDates, stuff((SELECT ',' + Cast(Status as varchar(24)) FROM CasesInRange WHERE [Name] = a.[Name] and Shade = a.Shade for xml path('')), 1, 1, '') as Statuses, Count(a.CaseNumber) as Cases, a.[Name] FROM CasesInRange as a GROUP BY a.[Name], a.Shade) as outer_query WHERE Cases > 1 and [Name] != ',' ORDER BY[Name] ASC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # input: IncludedLocations, ExcludedLocations
        # output: [[Cases]]
        self.get_cases_pending_by_location = "SELECT CaseNumber, CustomerID, Shade, ShipDate, CAST(SUM(Quantity) as Int) as Quantity, SUM(Units) as Units, MIN(Created) as Created, LocationID FROM ( SELECT top 100 b.CaseNumber, b.CustomerID, b.Shade, (CASE WHEN d.TeethNumbers IS NULL or d.TeethNumbers = '' THEN d.Shade ELSE d.TeethNumbers END) as SubShade, b.ShipDate, d.Quantity, COUNT(a.AlignerID) as Units, c.MachineID, MIN(c.Created) as Created, a.[Location] as LocationID FROM {{database}}.dbo.Aligners as a left join ( SELECT ID, VerificationID, MachineID, AlignerID, Created, LocationID, row_number() over (partition by AlignerID order by Created DESC) as Row# FROM {{database}}.dbo.Stations ) as c on a.AlignerID = c.AlignerID and Row# = 1 left join {{database}}.dbo.Cases as b on a.CaseID = b.CaseID left join {{database}}.dbo.CaseProducts as d on b.CaseID = d.CaseID and a.ProductID = d.ProductID WHERE a.Status in (2, 4) and c.LocationID in ({0}) and c.LocationID not in ({1}) and c.MachineID = -1 GROUP BY b.CaseNumber, b.CustomerID, b.Shade, d.TeethNumbers, d.Shade, b.ShipDate, d.Quantity, c.MachineID, a.[Location] ) as outer_query WHERE CAST(Quantity as int) != Units GROUP BY CaseNumber, CustomerID, Shade, ShipDate, LocationID ORDER BY Created ASC"
        # input: N/A
        # output: [case_flags]
        self.get_all_case_flags = "SELECT ID as FlagID, FlagType, Color, Icon, Weight, Description, Status from {database}.dbo.CaseFlags"
        # Input: FlagType, Color, Weight, Icon
        # Output: Case_Flag_ID
        self.insert_case_flag = "INSERT INTO {database}.dbo.CaseFlags (FlagType, Color, Weight, Icon, Description, Status) OUTPUT INSERTED.ID VALUES (?, ?, ?, ?, ?, 11)"
        # Input: FlagType, Color, Weight, Icon, CaseFlagID, Status
        # Output: Case_Flag_ID
        self.edit_case_flag = "UPDATE {database}.dbo.CaseFlags SET FlagType = ?, Color = ?, Weight = ?, Description = ?, Icon = ?, Status = ? OUTPUT INSERTED.ID WHERE ID = ?"
        # input: Statuses
        # output: [case_flag_links]
        self.get_case_flag_links_by_status = "SELECT ID as FlagLinkID, FlagID, CaseNumber, CaseID, CheckedIn, CheckedOut, Status from {database}.dbo.CaseFlagLinks where Status in (SELECT value FROM STRING_SPLIT(?, ','))"
        # Input: CaseID, flagID, employeeID
        # Output: Case_Flag_Link_ID
        self.insert_case_flag_link = "INSERT INTO {database}.[dbo].[CaseFlagLinks] ([FlagID], [CaseNumber], [CaseID], [CheckedInVerificationID], [CheckedIn], [Status]) OUTPUT inserted.ID VALUES (?, ?, ?, ?, GETDATE(), 11)"
        # Input: employeeID, case_flag_link_ID
        # Output: CaseFlagLinkID
        self.change_case_flag_link = "UPDATE {{database}}.dbo.CaseFlagLinks SET {0} OUTPUT Inserted.ID WHERE ID = ?"
        # Input: case, status
        # Output: caseflags
        self.get_case_flags_for_given_case = "SELECT caseFlagLinksTable.ID as FlagLinkID, caseFlagTable.FlagType, caseFlagTable.Color, caseFlagTable.Weight, caseFlagTable.Icon, caseFlagTable.Description, FlagID, CaseNumber, CheckedIn, CheckedOut, caseFlagLinksTable.Status from {database}.dbo.CaseFlagLinks as caseFlagLinksTable LEFT JOIN {database}.dbo.CaseFlags caseFlagTable on caseFlagTable.ID = caseFlagLinksTable.FlagID WHERE caseFlagLinksTable.Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseNumber in (SELECT value from STRING_SPLIT(?,','))"
        # Input: case
        # Output: caseFlagLinkLogs
        self.get_case_flag_link_logs_for_caseNumber = "SELECT [ID], [LogTypeID], Change, LogNote, Logged, LoggedVerificationID, [LinkID], [FlagID], [CaseNumber], [CheckedInVerificationID], velin.EmployeeID as CheckedInBy, [CheckedIn], [CheckedOutVerificationID], velout.EmployeeID as CheckedOutBy, [CheckedOut], [Status] FROM {database}.dbo.CaseFlagLinkLogs as a OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckedInVerificationID) as velin OUTER APPLY (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.CheckedOutVerificationID) as velout WHERE CaseNumber = ?"
        # Input: LogTypeID, LinkID, FlagID, CaseID, VerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status, Change, Description
        # Output: [flagLinkLog]
        self.insert_flag_link_log = "INSERT INTO {database}.dbo.CaseFlagLinkLogs (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, FlagID, CaseNumber, CaseID, CheckedInVerificationID, CheckedIn, CheckedOutVerificationID, CheckedOut, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT FlagID FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CaseNumber FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CaseID FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CheckedInVerificationID FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CheckedIn FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CheckedOutVerificationID FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT CheckedOut FROM {database}.dbo.CaseFlagLinks WHERE ID = ?), (SELECT Status FROM {database}.dbo.CaseFlagLinks WHERE ID = ?))"
        # input: Statuses
        # output: [case_employee_links]
        self.get_case_employee_links_by_status = "SELECT ID as CaseEmployeeLinkID, CaseNumber, CaseID, CheckedIn, VerificationID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy, Status from {database}.dbo.CaseEmployeeLinks as a where Status in (SELECT value FROM STRING_SPLIT(?, ','))"
        # input: Statuses, caseNumber
        # output: [case_employee_links]
        self.get_case_employee_links_by_case_and_status = "SELECT TOP (1) ID as CaseEmployeeLinkID, CaseNumber, CaseID, CheckedIn, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CheckedInBy, VerificationID, Status from {database}.dbo.CaseEmployeeLinks as a where Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseNumber = ? order by CheckedIn asc"
        # input: Statuses, caseIDs
        # output: [case_employee_links]
        self.get_case_employee_links_by_cases_and_status = "SELECT ID as CaseEmployeeLinkID, CaseNumber, CaseID, CheckedIn, VerificationID,(SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CheckedInBy, Status from {database}.dbo.CaseEmployeeLinks as a where Status in (SELECT value FROM STRING_SPLIT(?, ',')) and CaseNumber in (SELECT value from STRING_SPLIT(?,',')) order by CheckedIn asc"
        # Input: EmployeeID, CaseID
        # Output: case_employee_link_ID
        self.insert_case_employee_link = "INSERT INTO {database}.[dbo].[CaseEmployeeLinks] ([CaseNumber], [CaseID], [VerificationID], [CheckedIn], [Status]) OUTPUT inserted.ID, inserted.VerificationID VALUES (?, ?, ?, GETDATE(), 11)"
        # Input: LogTypeID, LinkID, CaseID, DateIn, CheckIn, DateOut, CheckOut, Status, Change, Description
        # Output: [case_employee_link_log]
        self.insert_case_employee_link_log = "INSERT INTO {database}.[dbo].[CaseEmployeeLinkLogs] (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, CaseNumber, CaseID, VerificationID, Status) OUTPUT inserted.ID VALUES (?, ?, ?, GETDATE(), ?, ?, (SELECT CaseNumber FROM {database}.dbo.CaseEmployeeLinks WHERE ID = ?), (SELECT CaseID FROM {database}.dbo.CaseEmployeeLinks WHERE ID = ?), (SELECT VerificationID FROM {database}.dbo.CaseEmployeeLinks WHERE ID = ?), (SELECT Status FROM {database}.dbo.CaseEmployeeLinks WHERE ID = ?))"
        # Input: LogTypeID, LinkID, CaseID, DateIn, CheckIn, DateOut, CheckOut, Status, Change, Description
        # Output: [case_employee_link_log]
        self.get_case_employee_link_logs_by_caseNumber = "SELECT ID, LogTypeID, Change, LogNote, Logged, LoggedVerificationID, LinkID, CaseNumber, CaseID, Created, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy, Status FROM {database}.dbo.CaseEmployeeLinkLogs as a WHERE Status in (11, 12) and CaseNumber = ? order by Created asc"
        # Input: EmployeeID
        # Output: [case_employee_link_log]
        self.get_case_employee_link_logs_by_employeeID = "SELECT ID, LogTypeID, LinkID, CaseNumber, Logged, LoggedVerificationID, Status, Change,(SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy, LogNote FROM {database}.[dbo].[CaseEmployeeLinkLogs] as a where Status in (11, 12) and Logged >= DATEADD(HOUR, -48, GETDATE()) and CAST(? as varchar) in (SELECT EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = LoggedVerificationID) order by Created asc"
        # Input: CaseNumber
        # Output: [case_employee_links]
        self.remove_employees_from_case = "UPDATE {database}.dbo.CaseEmployeeLinks SET Status = 12 OUTPUT Inserted.LinkID WHERE CaseNumber = ?"
        # Input: employeeID, case_employee_link_ID
        # Output: CaseEmployeeLinkID
        self.change_case_employee_link = "UPDATE {database}.dbo.CaseEmployeeLinks SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        # input: CaseID, FileTypeID
        # output: [[LinkID, FileTypeID, Path, Created, VerificationID, Status, CaseID]]
        self.get_active_case_files_by_all = "SELECT a.ID, b.ID as FileID, b.FileTypeID, c.Name as FileTypeName, c.Description as FileTypeDescription, c.Extension as FileTypeExtension, a.VerificationID, c.Description as FileTypeDescription, c.Extension as FileTypeExtension, b.Path,  a.Created, a.Status, a.CaseID FROM {database}.dbo.CaseFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID Left JOIN {database}.dbo.FileTypes as c ON b.FileTypeID = c.ID WHERE a.Status = 11 and CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)"
        # input: CaseID, FileTypeID
        # output: [[LinkID, FileTypeID, Path, Created, VerificationID, Status, CaseID]]
        self.get_active_case_files_by_type = "SELECT a.ID, b.ID as FileID, b.FileTypeID, b.Path, a.Created, a.VerificationID, a.Status, a.CaseID FROM {database}.dbo.CaseFileLinks as a LEFT JOIN {database}.dbo.Files as b ON a.FileID = b.ID WHERE a.CaseID = CaseID and b.FileTypeID = ? and a.Status = 11 and CaseID = (SELECT TOP 1 CaseID FROM {database}.dbo.Cases WHERE CaseNumber = ?)"
        # input: CaseID, FileID, Path, EmployeeID
        # output: [[ID]]
        self.insert_case_file = "INSERT INTO {database}.dbo.CaseFileLinks (CaseID, FileID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?)"
        # # Update Case File Link Status
        # Input: Status, ID
        self.update_case_file_link_status = "UPDATE {database}.dbo.CaseFileLinks SET [Status] = ? OUTPUT Inserted.ID WHERE ID IN (SELECT value FROM STRING_SPLIT(?, ','))"
        # Input: ProductionLine, offset, rows
        # Output: [cases]
        self.fetch_cases_by_production_line = "SELECT [ID],[LineID],[CaseNumber],[Status] FROM {database}.[dbo].[CaseProductionLineLinks] where Status = 11 and LineID = ? ORDER BY CaseNumber desc OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        # Input: N/A
        # Output: [LineID, AlignerQTY]
        self.get_total_aligners_in_production_lines = "SELECT SUM(a.Quantity) as Quantity, LineID FROM {database}.dbo.CaseProducts as a join {database}.dbo.Cases as b ON a.CaseID = b.CaseID join {database}.dbo.CaseProductionLineLinks as c ON b.CaseNumber = c.CaseNumber AND b.[Status] IN ('In Production') AND c.[Status] = 11 GROUP BY LineID"
        # input: caseNumber, lineID
        # output: [ID]
        self.insert_production_line_link = "INSERT INTO {database}.dbo.CaseProductionLineLinks (CaseNumber, LineID, Status) OUTPUT Inserted.ID VALUES (?, ?, 11)"
        # input: VerificationID, CaseID
        # output: [ID]
        self.insert_case = "INSERT INTO {database}.dbo.CasePairings (CaseID, Created, VerificationID, LocationID) OUTPUT Inserted.ID VALUES (?, GETDATE(), ?, ?)"
        # input: Status, CaseID
        # output: ID
        self.update_phase_case_status = "UPDATE {database}.dbo.CasePairings SET Status = ? OUTPUT INSERTED.ID WHERE CaseID = ?"
        # input: Status, CaseID
        # output: ID
        self.update_mt_case_status = "Update {database}.dbo.CasePairings set Status = ? OUTPUT Inserted.CaseID, Inserted.Status WHERE CaseID = ?"
        # input: CaseID, InvoicedBy, NewCaseStatus, NewInvoiceDate, ApplyCreditOption, CreateDelivery, LastStDate, BatchNumber, FromCreateShipment
        # output: CaseID
        self.invoice_mt_case = """
            SET NOCOUNT ON;
            DECLARE @RC int;
            DECLARE @NewDate datetime;
            Set @NewDate = GETDATE()
            EXEC @RC = {database}.dbo.InvoiceCase @CaseID=?, @InvoicedBy=?, @NewCaseStatus=?, @NewInvoiceDate=@NewDate, @ApplyCreditOption=?, @CreateDelivey=?, @LastStDate=@NewDate, @BatchNumber=?, @FromCreateStatement=?
            SELECT @RC AS success;
            """
        # input: CaseID, InvoicedBy, NewCaseStatus, NewInvoiceDate, ApplyCreditOption, CreateDelivery, LastStDate, BatchNumber, FromCreateShipment
        # output: Success int
        self.uninvoice_mt_case = """
            SET NOCOUNT ON;
            DECLARE @RC int;
            EXEC @RC = {database}.dbo.UnInvoiceCase @CaseID=?, @UserID=?, @ResetShippingInfo=?
            SELECT @RC AS success;
            """
        # input: CaseID, NewCaseID, Remake, RemakeReason, RemakeValue, UserName, NC_SetAsRemake
        # output: Success int
        self.remake_mt_case = """
            SET NOCOUNT ON;
            DECLARE @RC int;
            EXEC @RC = {database}.dbo.RemakeCase @CaseID=?, @NewCaseID=?, @Remake=?, @RemakeReason=?, @RemakeValue=?, @UserName=?, @NC_SetAsRemake=?
            SELECT @RC AS success;
            """
        # input: Location, CaseID
        # output: CaseID
        self.update_case_location = "UPDATE {database}.dbo.CasePairings SET LocationID = ? OUTPUT Inserted.CaseID WHERE CaseID = ?"
        # input: CaseID, Change, VerificationID, Location
        # output: [[LogID]]
        self.insert_case_log = "INSERT INTO {database}.dbo.CaseLog (LogTypeID, Change, LogNote, Logged, LoggedVerificationID, PhaseID, CaseID, Created, VerificationID, Status, LocationID) OUTPUT Inserted.ID VALUES (?, ?, ?, GETDATE(), ?, (SELECT TOP 1 ID FROM {database}.dbo.CasePairings WHERE CaseID = ?), ?, (SELECT TOP 1 Created FROM {database}.dbo.CasePairings WHERE CaseID = ?), (SELECT TOP 1 VerificationID FROM {database}.dbo.CasePairings WHERE CaseID = ?), (SELECT TOP 1 Status FROM {database}.dbo.Cases WHERE CaseID = ?), (SELECT TOP 1 LocationID FROM {database}.dbo.CasePairings WHERE CaseID = ?))"
