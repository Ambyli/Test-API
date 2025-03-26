from .config import Config
from .sql_config import SQLConfig


# product config
class ReportConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # output: [reports]
        # input: N/A
        self.get_all_active_reports = "SELECT ID, Name, Description, Created, VerificationID, HTMLFile, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = reportsTable.VerificationID) as CreatedBy, Status FROM {database}.dbo.Reports reportsTable WHERE Status = 11 AND Name like '%' + ? + '%' ORDER BY Created DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        # output: report
        # input: reportID
        self.get_report_by_report = "SELECT ID, Name, Description, Created, VerificationID, HTMLFile, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = reportsTable.VerificationID) as CreatedBy,Status FROM {database}.dbo.Reports reportsTable WHERE ID = ?"
        # output: report
        # input:  Name, Description, VerificationID
        self.insert_report = "INSERT INTO {database}.dbo.Reports (Name, Description, Created, VerificationID, HTMLFile, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?, 11)"
        # output: [reports]
        # input: caseNumber
        self.get_reports_by_case_number = "SELECT ID, CaseNumber, ReportID, Created, VerificationID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = linksTable.VerificationID) as CreatedBy,Status FROM {database}.dbo.CaseReportLinks linksTable WHERE Status = 11 AND CaseNumber = ?"
        # output: caseReportLink
        # input:  CaseNumber, ReportID, VerificationID
        self.insert_case_report_link = "INSERT INTO {database}.dbo.CaseReportLinks (CaseNumber, ReportID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        # output: CaseReportLinkID
        # input: status, CaseReportLinkID
        self.update_case_report_link_status = "UPDATE {database}.dbo.CaseReportLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # output: ReportID
        # input: status, name, description, htmlFile, reportID
        self.update_info_of_report = "UPDATE {database}.dbo.Reports SET Status = ?, Name = ?, Description = ?, HTMLFile = ? OUTPUT Inserted.ID WHERE ID = ?"
        # output: [reports]
        # input: N/A
        self.get_linked_case_reports = "SELECT ID, CaseNumber, ReportID, Created, VerificationID, Status FROM {database}.dbo.CaseReportLinks WHERE Status = 11"
        # output: [reports]
        # input: caseNumber
        self.get_linked_case_reports_by_caseNumber = "SELECT a.ID, a.ReportID, a.CaseNumber, b.Description, a.Created, b.Name, a.Status, a.VerificationID, (SELECT TOP 1 EmployeeID FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = a.VerificationID) as CreatedBy FROM {database}.dbo.CaseReportLinks as a LEFT JOIN {database}.dbo.Reports as b ON a.ReportID = b.ID WHERE a.CaseNumber = ? and a.Status = 11"
        # output: [queries]
        # input: reportID
        self.get_active_queries_for_report = "SELECT a.QueryID, a.ReportID, a.ID as QueryLinkID, b.QueryString, b.Name as QueryName, b.Description as QueryDescription, a.Status FROM {database}.dbo.ReportQueryLinks as a LEFT JOIN {database}.dbo.Queries as b ON a.QueryID = b.ID WHERE a.ReportID = ? and a.Status = 11 ORDER BY a.QueryID ASC"
        # output:QueryReportLink
        # input: status, QueryReportLinkId
        self.update_report_query_link_status = "UPDATE {database}.dbo.ReportQueryLinks SET Status = ? OUTPUT Inserted.ID WHERE ID = ?"
        # output: queryReportLink
        # input:  QueryID, ReportID, VerificationID
        self.insert_report_query_link = "INSERT INTO {database}.dbo.ReportQueryLinks (QueryID, ReportID, Created, VerificationID, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, 11)"
        # output: reportQueryLinkVariables
        # input: reportQueryLinkIDs
        self.get_active_report_query_link_variables = "SELECT ID, LinkID, Status, Created, VerificationID, QueryRow, QueryColumn, Variable, DefaultValue from {{database}}.dbo.ReportQueryLinkVariables WHERE LinkID in ({0}) and Status = 11"
        # output: reportQueryLinkVariableIDs
        # input:  linkID, status, VerificationID, DefaultValue, QueryRow, QueryColumn, Variable
        self.insert_report_query_link_variable = "INSERT INTO {database}.dbo.ReportQueryLinkVariables (LinkID, Status, Created, VerificationID, DefaultValue, QueryRow, QueryColumn, Variable) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?)"
        # output:ReportID
        # input: reportID
        self.delete_report_by_ID = "UPDATE {database}.dbo.Reports SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        # output: reportQueryLinkVariableID
        # input: reportQueryLinkVariableID
        self.delete_report_query_link_variable_by_ID = "UPDATE {database}.dbo.ReportQueryLinkVariables SET Status = 12 OUTPUT Inserted.ID WHERE ID = ?"
        # output: ReportQueryLinkVariableID
        # input: linkID, QueryColumn, QueryRow, Variable, DefaultValue, ReportQueryLinkVariableID
        self.update_info_of_report_query_link_variable = "UPDATE {database}.dbo.ReportQueryLinkVariables SET linkID = ?, QueryColumn = ?, QueryRow = ?, Variable = ?, DefaultValue = ? OUTPUT Inserted.ID WHERE ID = ?"
