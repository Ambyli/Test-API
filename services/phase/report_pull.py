#!/usr/bin/env python3.7
import logging
from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .report_config import ReportConfig
from .verification_pull import Verification

from .sql_pull import SQL_Pull
from .gauge_pull import Gauge


class Report(ReportConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        ReportConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # Current working values
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # gets active reports
    # input: Offset, Rows, searchName
    # output: active reports on success, [] on error
    def get_active_reports(self, offset: int, rows: int, searchName: str) -> list:
        try:
            self.LOG.info(
                f"get_active_reports: offset={offset} rows={rows} searchName={searchName}"
            )

            reports = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_active_reports, (searchName, offset, rows))
                if len(sql.table) != 0:
                    reports = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_active_reports query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_reports: error={}".format(e))
            self.LOG.info("get_active_reports: END")
            return []  # other error

        self.LOG.info("get_active_reports: vendors={}".format(reports))
        self.LOG.info("get_active_reports: END")
        return reports  # no error

    # gets report by ID
    # input: ID
    # output: report on success
    def get_report_by_ID(self, reportID: int) -> list:
        try:
            self.LOG.info("get_report_by_ID: reportID={}".format(reportID))

            report = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_report_by_report, (reportID))
                if len(sql.table) != 0:
                    report = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_report_by_report query!"
                    )

        except Exception as e:
            self.LOG.error("get_report_by_ID: error={}".format(e))
            self.LOG.info("get_report_by_ID: END")
            return []  # other error

        self.LOG.info("get_report_by_ID: vendors={}".format(report))
        self.LOG.info("get_report_by_ID: END")
        return report  # no error

    # Creates a new report
    # input: name, description, createdBy, html
    # output: reportID
    def create_report(
        self, name: str, description: str, verification: Verification, html: str
    ) -> dict:
        try:
            self.LOG.info(
                "create_report: name={} description={} verification={} html={}".format(
                    name, description, verification, html
                )
            )
            report = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # add report
                    sql.execute(
                        self.insert_report,
                        (name, description, verification.get_verification(), html),
                    )

                    if len(sql.table) > 0:
                        report = sql.table[0]
                    else:
                        raise Exception("Unable to create new report!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_report: error={}".format(e))
            self.LOG.info("create_report: END")
            return {}  # other error

        self.LOG.info("create_report: entry={}".format(report))
        self.LOG.info("create_report: END")
        return report  # no error

    # Gets all active reports linked to a case
    # input: [reports]
    # output: [reports]
    def get_reports_by_case(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_reports_by_case: caseNumber={} ".format(caseNumber))
            reports = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get reports for the given case
                sql.execute(self.get_reports_by_case_number, (caseNumber))

                if len(sql.table) != 0:
                    reports = sql.table
                else:
                    raise Exception(f"No reports found for case: {caseNumber}!")

        except Exception as e:
            self.LOG.error("get_reports_by_case: error={}".format(e))
            self.LOG.info("get_reports_by_case: END")
            return reports  # other error

        self.LOG.info("get_reports_by_case: entry={}".format(reports))
        self.LOG.info("get_reports_by_case: END")
        return reports  # no error

    # Delete Report
    # input: reportID
    # output: 0 on success, -1 on fail
    def delete_report(self, reportID: int) -> list:
        try:
            self.LOG.info(f"delete_report: reportID = {reportID}")
            success = -1

            with SQL_Pull()(self.sql_config)() as sql:
                # delete report
                sql.execute(self.delete_report_by_ID, (reportID))

                if len(sql.table) != 0:
                    success = 0
                else:
                    raise Exception(f"Delete Report Failed for Report {reportID}")

        except Exception as e:
            self.LOG.error("delete_report: error={}".format(e))
            self.LOG.info("delete_report: END")
            return success  # other error

        self.LOG.info("delete_report: entry={}".format(success))
        self.LOG.info("delete_report: END")
        return success  # no error

    # Creates a new Case Report Link
    # input: CaseNumber, ReportID, CreatedBy
    # output: CaseReportLink
    def create_case_report_link(
        self, caseNumber: int, reportID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "create_case_report_link: caseNumber={} reportID={} verification={} ".format(
                    caseNumber, reportID, verification
                )
            )
            case_report_link = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # add case report link
                    sql.execute(
                        self.insert_case_report_link,
                        (caseNumber, reportID, verification.get_verification()),
                    )

                    if len(sql.table) != 0:
                        case_report_link = str(sql.table[0]["ID"])
                    else:
                        raise Exception("Unable to create new case_report_link!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_case_report_link: error={}".format(e))
            self.LOG.info("create_case_report_link: END")
            return -1  # other error

        self.LOG.info("create_case_report_link: entry={}".format(case_report_link))
        self.LOG.info("create_case_report_link: END")
        return case_report_link  # no error

    # Changes the information for a given report
    # input: reportID , name, description, html_file, status, verification
    # output: 0 on success, -1 on failure
    def update_report(
        self,
        reportID: int,
        status: int,
        verification: Verification,
        name: str,
        description: str,
        html_file: str,
    ) -> int:
        try:
            self.LOG.info(
                "update_report: reportID={} status={} verification={} name={} description={} html_file:{}".format(
                    reportID, status, verification, name, description, html_file
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # update report with given information
                    sql.execute(
                        self.update_info_of_report,
                        (status, name, description, html_file, reportID),
                    )

                    if len(sql.table) != 0:
                        reportID = str(sql.table[0]["ID"])
                    else:
                        raise Exception("Unable to Update report!")
                else:
                    raise Exception("Invalid verification!")

                self.LOG.info("update_report: END")
                return 0
        except Exception as e:
            self.LOG.error("update_report: error={}".format(e))
            self.LOG.info("update_report: END")
        return -1  # other error

    # Changes the status of a CaseReportLink
    # input: CaseReportLinkID, Status, Verification
    # output: ID on success, -1 on failure
    def update_status_case_report_link(
        self, verification: Verification, caseReportLinkID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_case_report_link: employee={} caseReportLinkID={} status={} ".format(
                    verification, caseReportLinkID, status
                )
            )

            case_report_link = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # update case report link status
                    sql.execute(
                        self.update_case_report_link_status,
                        (status, caseReportLinkID),
                    )

                    if len(sql.table) != 0:
                        case_report_link = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to Update case_report_link!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status_case_report_link: error={}".format(e))
            self.LOG.info("update_status_case_report_link: END")
            return -1  # other error

        self.LOG.info(
            "update_status_case_report_link: entry={}".format(case_report_link)
        )
        self.LOG.info("update_status_case_report_link: END")
        return case_report_link  # no error

    # Gets all active case report links
    # input: N/A
    # output: [reports]
    def get_case_report_links(self) -> list:
        try:
            self.LOG.info("get_case_report_links: START")
            reports = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get case report links
                sql.execute(self.get_linked_case_reports)

                if len(sql.table) != 0:
                    reports = sql.table
                else:
                    raise Exception(f"No case report links found")

        except Exception as e:
            self.LOG.error("get_case_report_links: error={}".format(e))
            self.LOG.info("get_case_report_links: END")
            return reports  # other error

        self.LOG.info("get_case_report_links: entry={}".format(reports))
        self.LOG.info("get_case_report_links: END")
        return reports  # no error

    # Gets all active case report links for given caseNumber
    # input: CaseNumber
    # output: [reports]
    def get_case_report_links_by_case_number(self, caseNumber: int) -> list:
        try:
            self.LOG.info(
                f"get_case_report_links_by_case_number: caseNumber={caseNumber}"
            )
            reports = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get case report links by case
                sql.execute(self.get_linked_case_reports_by_caseNumber, (caseNumber))

                if len(sql.table) != 0:
                    reports = sql.table
                else:
                    raise Exception(f"No case report links found for case:{caseNumber}")

        except Exception as e:
            self.LOG.error("get_case_report_links_by_case_number: error={}".format(e))
            self.LOG.info("get_case_report_links_by_case_number: END")
            return reports  # other error

        self.LOG.info("get_case_report_links_by_case_number: entry={}".format(reports))
        self.LOG.info("get_case_report_links_by_case_number: END")
        return reports  # no error

    # Gets all active report query links
    # input: N/A
    # output: [reports]
    def get_report_query_links(self) -> list:
        try:
            self.LOG.info(f"get_report_query_links: START")
            report_query_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get report query links
                sql.execute(self.get_active_report_query_links)

                if len(sql.table) != 0:
                    report_query_links = sql.table
                else:
                    raise Exception(f"No report query links found")

        except Exception as e:
            self.LOG.error("get_report_query_links: error={}".format(e))
            self.LOG.info("get_report_query_links: END")
            return report_query_links  # other error

        self.LOG.info("get_report_query_links: entry={}".format(report_query_links))
        self.LOG.info("get_report_query_links: END")
        return report_query_links  # no error

    # Creates a link between the list of queries given and the report given
    # input:queryIDs, ReportID, verification
    # output: Query Report Links
    def create_report_query_link(
        self, queryIDs: list, reportID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "create_report_query_links: queryIDs={} reportID={} verification={} ".format(
                    queryIDs, reportID, verification
                )
            )
            report_query_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    for queryID in queryIDs:
                        # add report query link
                        sql.execute(
                            self.insert_report_query_link,
                            (queryID, reportID, verification.get_verification()),
                        )

                        if len(sql.table) != 0:
                            report_query_links.append(
                                {"QueryID": queryID, "LinkID": str(sql.table[0]["ID"])}
                            )
                        else:
                            report_query_links.append(
                                {"QueryID": queryID, "LinkID": ""}
                            )

                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_report_query_link: error={}".format(e))
            self.LOG.info("create_report_query_link: END")
            return []  # other error

        self.LOG.info("create_report_query_link: entry={}".format(report_query_links))
        self.LOG.info("create_report_query_link: END")
        return report_query_links  # no error

    # Creates a link between the list of queryVariables given and the reportQueryID given
    # input: reportQueryLinkIDs, reportID, verification
    # output: Query Report Links
    def create_report_query_link(
        self, queryIDs: list, reportID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "create_report_query_links: queryIDs={} reportID={} verification={} ".format(
                    queryIDs, reportID, verification
                )
            )
            report_query_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    for queryID in queryIDs:
                        # add report query link
                        sql.execute(
                            self.insert_report_query_link,
                            (queryID, reportID, verification.get_verification()),
                        )

                        if len(sql.table) != 0:
                            report_query_links.append(
                                {"QueryID": queryID, "LinkID": str(sql.table[0]["ID"])}
                            )
                        else:
                            report_query_links.append(
                                {"QueryID": queryID, "LinkID": ""}
                            )

                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_report_query_link: error={}".format(e))
            self.LOG.info("create_report_query_link: END")
            return []  # other error

        self.LOG.info("create_report_query_link: entry={}".format(report_query_links))
        self.LOG.info("create_report_query_link: END")
        return report_query_links  # no error

    # Changes the status of a ReportQueryLink
    # input: ReportQueryLinkID, Status
    # output: ID on success, -1 on failure
    def update_status_report_query_link(
        self, verification: int, reportQueryLinkID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_report_query_link: employee={} queryReportLinkID={} status={} ".format(
                    verification, reportQueryLinkID, status
                )
            )

            report_query_link = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # update query report link status
                    sql.execute(
                        self.update_report_query_link_status,
                        (status, reportQueryLinkID),
                    )

                    if len(sql.table) != 0:
                        report_query_link = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to Update report_query_link!")

        except Exception as e:
            self.LOG.error("update_status_report_query_link: error={}".format(e))
            self.LOG.info("update_status_report_query_link: END")
            return -1  # other error

        self.LOG.info(
            "update_status_report_query_link: entry={}".format(report_query_link)
        )
        self.LOG.info("update_status_report_query_link: END")
        return report_query_link  # no error

    # Gets queries linked to given report
    # input: reportID
    # output: queries
    def get_queries_for_report(self, reportID: int) -> list:
        try:
            self.LOG.info(f"get_queries_for_report: reportID = {reportID}")
            queries = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get queries for reports
                sql.execute(self.get_active_queries_for_report, (reportID))

                if len(sql.table) != 0:
                    queries = sql.table
                else:
                    raise Exception(f"No queries found for report {reportID}")

        except Exception as e:
            self.LOG.error("get_queries_for_report: error={}".format(e))
            self.LOG.info("get_queries_for_report: END")
            return queries  # other error

        self.LOG.info("get_queries_for_report: entry={}".format(queries))
        self.LOG.info("get_queries_for_report: END")
        return queries  # no error

    # Gets Variables linked to given ReportQueryLink
    # input: reportQueryLink
    # output: variables
    def get_report_query_link_variables(self, reportQueryLinkIDs: list) -> list:
        try:
            self.LOG.info(
                f"get_report_query_link_variables:reportQueryLinkIDs = {reportQueryLinkIDs}"
            )
            queries = []

            with SQL_Pull()(self.sql_config)() as sql:
                # Generate placeholder ? for each querylinkID
                link_ID_placeholders = ",".join("?" * len(reportQueryLinkIDs))
                # get queries for reports
                sql.execute(
                    self.get_active_report_query_link_variables.format(
                        link_ID_placeholders
                    ),
                    (reportQueryLinkIDs),
                )

                if len(sql.table) != 0:
                    queries = sql.table
                else:
                    raise Exception(f"No queries found for report {reportQueryLinkIDs}")

        except Exception as e:
            self.LOG.error("get_report_query_link_variables: error={}".format(e))
            self.LOG.info("get_report_query_link_variables: END")
            return queries  # other error

        self.LOG.info("get_report_query_link_variables: entry={}".format(queries))
        self.LOG.info("get_report_query_link_variables: END")
        return queries  # no error

    # Creates a link between the list of queryVariables given and the reportQueryLinkID given
    # input: reportQueryLinkID, status, verification, var_list
    # output: ReportQueryLinkVariableIDs
    def create_report_query_link_variables(
        self, linkID: int, status: int, verification: Verification, var_list: list
    ) -> int:
        try:
            self.LOG.info(
                "create_report_query_link_variables: linkID={} status={} verification={} var_list={} ".format(
                    linkID, status, verification, len(var_list)
                )
            )
            report_query_link_variables = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    for variable in var_list:
                        # Set default_value to the given default value, if one isn't given then set it to an empty string
                        default_value = (
                            variable["DefaultValue"] if variable["DefaultValue"] else ""
                        )
                        # insert reportQueryLinkVariable
                        sql.execute(
                            self.insert_report_query_link_variable,
                            (
                                linkID,
                                status,
                                verification.get_verification(),
                                default_value,
                                variable["QueryRow"],
                                variable["QueryColumn"],
                                variable["Variable"],
                            ),
                        )

                        # Appends dict containing the Variable name and created link ID if success
                        if len(sql.table) != 0:
                            report_query_link_variables.append(
                                {
                                    "Variable": variable["Variable"],
                                    "VariableLinkID": str(sql.table[0]["ID"]),
                                }
                            )

                        # Appends dict containing the Variable name and empty link ID if fail
                        else:
                            report_query_link_variables.append(
                                {"Variable": variable["Variable"], "VariableLinkID": ""}
                            )

                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_report_query_link_variables: error={}".format(e))
            self.LOG.info("create_report_query_link_variables: END")
            return []  # other error

        self.LOG.info(
            "create_report_query_link_variables: entry={}".format(
                report_query_link_variables
            )
        )
        self.LOG.info("create_report_query_link_variables: END")
        return report_query_link_variables  # no error

    # Delete ReportQueryLinkVariable
    # input: reportQueryLinkVariableID
    # output: 0 on success, -1 on fail
    def delete_report_query_link_variable(self, reportQueryLinkVariableID: int) -> list:
        try:
            self.LOG.info(
                f"delete_report_query_link_variable: reportQueryLinkVariableID= {reportQueryLinkVariableID}"
            )
            success = -1

            with SQL_Pull()(self.sql_config)() as sql:
                # delete report
                sql.execute(
                    self.delete_report_query_link_variable_by_ID,
                    (reportQueryLinkVariableID),
                )

                if len(sql.table) != 0:
                    success = 0
                else:
                    raise Exception(
                        f"delete_report_query_link_variable: Delete ReportQueryLinkVariable Failed for {reportQueryLinkVariableID}"
                    )

        except Exception as e:
            self.LOG.error("delete_report_query_link_variable: error={}".format(e))
            self.LOG.info("delete_report_query_link_variable: END")
            return success  # other error

        self.LOG.info("delete_report_query_link_variable: entry={}".format(success))
        self.LOG.info("delete_report_query_link_variable: END")
        return success  # no error

    # Changes the information for a given reportQueryLinkVariable
    # input: reportQueryLinkVariableID, queryRow, queryColumn, variable, defaultValue, verification
    # output: 0 on success, -1 on failure
    def update_report_query_link_variables(
        self,
        reportQueryLinkVariableID: int,
        linkID: int,
        queryRow: int,
        queryColumn: str,
        variable: str,
        defaultValue: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "update_report_query_link_variables: reportQueryLinkVariableID={} linkID={} queryColumn={} queryrow={} variable={} defaultValue={} verification:{}".format(
                    reportQueryLinkVariableID,
                    linkID,
                    queryColumn,
                    queryRow,
                    variable,
                    defaultValue,
                    verification,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # update reportQueryLinkVariable with given information
                    sql.execute(
                        self.update_info_of_report_query_link_variable,
                        (
                            linkID,
                            queryColumn,
                            queryRow,
                            variable,
                            defaultValue,
                            reportQueryLinkVariableID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("update_proceduer_query_link_variable: END")
                        return 0
                    else:
                        raise Exception("Unable to Update reportQueryLinkVariable!")
                else:
                    raise Exception("Invalid Verification")

        except Exception as e:
            self.LOG.error("reportQueryLinkVariable: error={}".format(e))
            self.LOG.info("reportQueryLinkVariable: END")
            return -1  # other error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
