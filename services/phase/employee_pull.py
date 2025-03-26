#!/usr/bin/env python3.7

import random
from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .shade_regex import gen_steps
from .verification_pull import Verification
from .employee_config import EmployeeConfig


class Employee(EmployeeConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        EmployeeConfig.__init__(self, sql_config)

        # initialize sql
        # self.sql = SQL_Pull(self.sql_config)()

        # Current working values
        # result = []
        # with SQL_Pull()(self.sql_config)() as sql:
        #     result, _ = sql.execute(self.get_status)
        #     for stat in result:
        #         self.statuses[stat["ID"]] = stat["StatusType"]
        #     result, _ = sql.execute(self.get_roles)
        #     for rol in result:
        #         self.roles[rol["ID"]] = rol["Title"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # checks if an employee is real, converts employeeID to number version
    # input: employeeID
    # output: employeeID on success, "" on error
    def employee_check(self, employeeID: str, restrict=False) -> str:
        try:
            self.LOG.info(
                "employee_check: employeeID={}".format(str(employeeID).lower())
            )

            conversion = ""

            # convert to employeeID
            result = self.get_employee(employeeID)
            if len(result) > 0:
                conversion = result[0]["EmployeeID"]

                # return fail if restrict is true and employeeID == conversion
                if restrict is True and str(employeeID) == str(conversion):
                    raise Exception("Invalid employee {}!".format(employeeID))
            else:
                raise Exception("Invalid employee {}!".format(employeeID))

        except Exception as e:
            self.LOG.error("employee_check: error={}".format(e))
            self.LOG.info("employee_check: END")
            return ""

        self.LOG.info("employee_check: employeeID={}".format(str(conversion)))
        self.LOG.info("employee_check: END")
        return conversion

    # gets employee info
    # input: employeeID
    # output: employee info on success, [] on error
    def get_employee(self, employeeID: str, supervisor=False) -> list:
        try:
            self.LOG.info("get_employee: employeeID={}".format(employeeID))

            # define employee info
            employee_info = []

            with SQL_Pull()(self.sql_config)() as sql:
                if supervisor:
                    sql.execute(
                        self.get_Employee_Manager,
                        (
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                        ),
                    )
                else:
                    sql.execute(
                        self.get_Employee,
                        (
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                            str(employeeID).lower(),
                        ),
                    )
                if len(sql.table) != 0:
                    for employee in sql.table:
                        employee["EmployeeID"] = str(employee["EmployeeID"])
                    employee_info = sql.table
                else:
                    raise Exception("No results found with the get_Employee query!")

        except Exception as e:
            self.LOG.error("get_employee: error={}".format(e))
            self.LOG.info("get_employee: END")
            return []

        self.LOG.info("get_employee: employee_info={}".format(str(employee_info)))
        self.LOG.info("get_employee: END")
        return employee_info  # no error

    # gets a list of all employees and their info
    # input: N/A
    # output: employees on success, [] on error
    def get_employees(self) -> list:
        try:
            self.LOG.info("get_employees: BEGIN")

            # define employee info
            employees = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Employees)
                if len(sql.table) != 0:
                    employees = sql.table
                else:
                    raise Exception("No results found with the get_Employees query!")

        except Exception as e:
            self.LOG.error("get_employees: error={}".format(e))
            self.LOG.info("get_employees: END")
            return []

        self.LOG.info("get_employees: employee_info={}".format(len(employees)))
        self.LOG.info("get_employees: END")
        return employees  # no error

    # gets a list of all employees and their info
    # input: N/A
    # output: employees on success, [] on error
    def get_employees_by_token(self, tokenID: int) -> list:
        try:
            self.LOG.info("get_employees_by_token: tokenID={}".format(tokenID))

            # define employee info
            employees = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_employees_by_token_id, (tokenID,))
                if len(sql.table) != 0:
                    employees = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employees_by_token_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_employees_by_token: error={}".format(e))
            self.LOG.info("get_employees_by_token: END")
            return []

        self.LOG.info("get_employees_by_token: employee_info={}".format(len(employees)))
        self.LOG.info("get_employees_by_token: END")
        return employees  # no error

    # gets all employee stats for a given location
    # input: StartDate, EndDate, Location
    # output: Stats on success, [] on error
    def get_employee_stats_by_location(
        self, startdate: str, enddate: str, location: int
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_stats_by_location: startdate={} enddate={} location={}".format(
                    startdate, enddate, location
                )
            )

            stats = []

            # Get employee stats for location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_location_stats_for_all_employees,
                    (location, startdate, enddate),
                )

                if len(sql.table) > 0:
                    stats = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_stats_for_all_employees query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_stats_by_location: error={}".format(e))
            return []

        self.LOG.info("get_employee_stats_by_location: stats={0}".format(len(stats)))
        self.LOG.info("get_employee_stats_by_location: END")
        return stats

    # gets employee stats by a given location and given employee ID
    # input: StartDate, EndDate, EmployeeID, Location
    # output: Stats on success, [] on error
    def get_employee_stats_by_location_and_employee(
        self, startdate: str, enddate: str, employeeID: str, location: int
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_stats_by_location_and_employee: startdate={} enddate={} employeeID={} location={}".format(
                    startdate, enddate, employeeID, location
                )
            )

            stats = []

            # get aligners from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_location_stats_by_employee,
                    (location, employeeID, startdate, enddate),
                )

                if len(sql.table) > 0:
                    stats = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_status_by_employee query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_employee_stats_by_location_and_employee: error={}".format(e)
            )
            return []

        self.LOG.info(
            "get_employee_stats_by_location_and_employee: stats={0}".format(len(stats))
        )
        self.LOG.info("get_employee_stats_by_location_and_employee: END")
        return stats

    # gets employee stats by a given location
    # input: StartDate, EndDate, EmployeeID
    # output: Stats on success, [] on error
    def get_employee_stats_per_location(
        self, startdate: str, enddate: str, employeeID: str
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_stats_per_location: startdate={} enddate={} employeeID={}".format(
                    startdate, enddate, employeeID
                )
            )

            stats = []

            # get aligners from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_location_stats_by_employee_per_location,
                    (employeeID, startdate, enddate),
                )

                if len(sql.table) > 0:
                    stats = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_status_by_employee query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_stats_per_location: error={}".format(e))
            return []

        self.LOG.info("get_employee_stats_per_location: stats={0}".format(len(stats)))
        self.LOG.info("get_employee_stats_per_location: END")
        return stats

    # gets employee teams
    # input: N/A
    # output: Teams on success, [] on error
    def get_employee_teams(self) -> list:
        try:
            self.LOG.info("get_employee_teams: BEGIN")

            teams = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_team_info)
                if len(sql.table) != 0:
                    teams = sql.table
                else:
                    raise Exception("No results found with the get_team_info query!")

        except Exception as e:
            self.LOG.error("get_employee_teams: error={}".format(e))
            return []

        self.LOG.info("get_employee_teams: teams={0}".format(len(teams)))
        self.LOG.info("get_employee_teams: END")
        return teams

    # gets a list of employees by a team ID
    # input: TeamID
    # output: Employees on success, [] on error
    def get_employees_by_team(self, teamID: int) -> list:
        try:
            self.LOG.info("get_employees_by_team: team={}".format(teamID))

            employees = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_teams_employees_by_team, (teamID))
                if len(sql.table) != 0:
                    employees = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employee_by_team query!"
                    )

        except Exception as e:
            self.LOG.error("get_employees_by_team: error={}".format(e))
            return []

        self.LOG.info("get_employees_by_team: employees={0}".format(len(employees)))
        self.LOG.info("get_employees_by_team: END")
        return employees

    # links a particular location and date range to a given employee
    # input: EmployeeID, AssigneeID, Location, StartDate, EndDate
    # output: LinkID on success, -1 on error
    def link_employee_to_location(
        self,
        verification: Verification,
        employeeID: str,
        location: int,
        startdate: str,
        enddate: str,
        status: int = 11,
    ) -> int:
        try:
            self.LOG.info(
                "link_employee_to_location: verification={} employeeID={} location={} startdate={} enddate={}".format(
                    verification, employeeID, location, startdate, enddate
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                employeeID = self.employee_check(str(employeeID).lower())
                if (
                    len(employeeID) != 0
                    and isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_employee_location_link,
                        (
                            location,
                            employeeID,
                            startdate,
                            enddate,
                            verification.get_verification(),
                            status,
                        ),
                    )

                    if len(sql.table) > 0:
                        linkID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the insert_employee_location_link query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("link_employee_to_location: error={}".format(e))
            return -1

        self.LOG.info("link_employee_to_location: linkID={0}".format(linkID))
        self.LOG.info("link_employee_to_location: END")
        return linkID

    # updates a link's status
    # input: EmployeeID, LinkID, Status
    # output: LinkID on success, -1 on error
    def update_employee_location_link(
        self, verification: Verification, linkID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_employee_location_link: verification={} linkID={} status={}".format(
                    verification, linkID, status
                )
            )

            result = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_employee_location_link_status, (status, linkID)
                    )

                    if len(sql.table) > 0:
                        result = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the update_employee_location_link_status query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_employee_location_link: error={}".format(e))
            return []

        self.LOG.info("update_employee_location_link: result={0}".format(result))
        self.LOG.info("update_employee_location_link: END")
        return result

    # gets all employee location links
    # input: StartDate, EndDate
    # output: Links on success, [] on error
    def get_employee_location_links(self, startdate: str, enddate: str) -> list:
        try:
            self.LOG.info(
                "get_employee_location_links: startdate={} enddate={}".format(
                    startdate, enddate
                )
            )

            links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_active_links_for_employee_location,
                    (startdate, enddate, startdate, enddate),
                )

                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_links_for_employee_locations query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_location_links: error={}".format(e))
            return []

        self.LOG.info("get_employee_location_links: links={0}".format(len(links)))
        self.LOG.info("get_employee_location_links: END")
        return links

    # gets all links by a given employee
    # input: EmployeeID, StartDate, EndDate
    # output: Links on success, [] on error
    def get_employee_location_links_by_employee(
        self, employeeID: str, startdate: str, enddate: str
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_location_links_by_employee: employeeID={} startdate={} enddate={}".format(
                    employeeID, startdate, enddate
                )
            )

            links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_active_links_for_employee_location_by_employee,
                    (startdate, enddate, startdate, enddate, employeeID),
                )

                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_links_for_employee_locations_by_employee query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_employee_location_links_by_employee: error={}".format(e)
            )
            return []

        self.LOG.info(
            "get_employee_location_links_by_employee: links={0}".format(len(links))
        )
        self.LOG.info("get_employee_location_links_by_employee: END")
        return links

    # gets all links by a given location
    # input: Location, StartDate, EndDate
    # output: Links on success, [] on error
    def get_employee_location_links_by_location(
        self, location: str, startdate: str, enddate: str
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_location_links_by_location: location={} startdate={} enddate={}".format(
                    location, startdate, enddate
                )
            )

            links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_active_links_for_employee_location_by_location,
                    (startdate, enddate, startdate, enddate, location),
                )

                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_links_for_employee_location_by_location query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_employee_location_links_by_location: error={}".format(e)
            )
            return []

        self.LOG.info(
            "get_employee_location_links_by_location: links={0}".format(len(links))
        )
        self.LOG.info("get_employee_location_links_by_location: END")
        return links

    # links an asset path to a given employeeID, similar to aligner file linking
    # input: AssigneeID, FileID, Path, EmployeeID, Status
    # output: LinkID on success, -1 on error
    def link_asset_to_employee(
        self, employeeID: str, fileID: int, verification: Verification, status: int = 11
    ) -> int:
        try:
            self.LOG.info(
                "link_asset_to_employee: employeeID={} fileID={} verification={} status={}".format(
                    employeeID, fileID, verification, status
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                employeeID = self.employee_check(str(employeeID).lower())
                if (
                    len(employeeID) != 0
                    and isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_employee_asset_link,
                        (employeeID, fileID, verification.get_verification(), status),
                    )

                    if len(sql.table) > 0:
                        linkID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the insert_employee_asset_link query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("link_asset_to_employee: error={}".format(e))
            return -1

        self.LOG.info("link_asset_to_employee: linkID={0}".format(linkID))
        self.LOG.info("link_asset_to_employee: END")
        return linkID

    # gets all active employee assets under a given fileID only
    # input: FileID
    # output: Links on success, [] on error
    def get_employee_asset_links(self, fileID: int) -> list:
        try:
            self.LOG.info("get_employee_asset_links: fileID={}".format(fileID))

            links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_links_for_employee_assets, (fileID))
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_links_for_employee_assets query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_asset_links: error={}".format(e))
            return []

        self.LOG.info("get_employee_asset_links: links={0}".format(len(links)))
        self.LOG.info("get_employee_asset_links: END")
        return links

    # gets all active employee asset links by a given employee
    # input: EmployeeID, FileID
    # output: Links on success, [] on error
    def get_employee_asset_links_by_employee(
        self, employeeID: str, fileID: int
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_asset_links_by_employee: employeeID={} fileID={}".format(
                    employeeID, fileID
                )
            )

            links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_active_links_for_employee_assets_by_employee,
                    (employeeID, fileID),
                )

                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_links_for_employee_assets_by_employee query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_asset_links_by_employee: error={}".format(e))
            return []

        self.LOG.info(
            "get_employee_asset_links_by_employee: links={0}".format(len(links))
        )
        self.LOG.info("get_employee_asset_links_by_employee: END")
        return links

    # updates an asset link's status
    # input: EmployeeID, LinkID, Status
    # output: LinkID on success, -1 on error
    def update_employee_asset_link(
        self, verification: Verification, linkID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_employee_asset_link: verification={} linkID={} status={}".format(
                    verification, linkID, status
                )
            )

            result = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_employee_asset_link_status, (status, linkID)
                    )

                    if len(sql.table) > 0:
                        result = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the update_employee_asset_link_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_employee_asset_link: error={}".format(e))
            return -1

        self.LOG.info("update_employee_asset_link: linkID={0}".format(result))
        self.LOG.info("update_employee_asset_link: END")
        return result

    # punches out a given assigned employee if an existing punch exists
    # input: EmployeeID, AssigneeID
    # output: LinkID on success, -1 on error
    def punch_employee_out(self, verification: Verification, assigneeID: str) -> int:
        try:
            self.LOG.info(
                "punch_employee_out: verification={} assigneeID={}".format(
                    verification, assigneeID
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # check employee punches if they have one
                    punches = self.get_active_employee_punches(assigneeID)

                    # checkout employee
                    if len(punches) > 0:
                        punch = punches[0]["ID"]
                        sql.execute(
                            self.checkout_employee_punch_link,
                            (verification.get_verification(), punch),
                        )

                        if len(sql.table) > 0:
                            linkID = int(sql.table[0]["ID"])
                        else:
                            raise Exception(
                                "No results found with the checkout_employee_punch_link query!"
                            )
                    else:
                        raise Exception(
                            "No punches were found to checkout employee {}, please try again later!".format(
                                assigneeID
                            )
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("punch_employee_out: error={}".format(e))
            self.LOG.info("punch_employee_out: END")
            return -1

        self.LOG.info("punch_employee_out: linkID={0}".format(linkID))
        self.LOG.info("punch_employee_out: END")
        return linkID

    # punches an employee in generating a linkID
    # input: EmployeeID, AssigneeID, Location
    # output: LinkID on success, -1 on error
    def punch_employee_in(
        self, verification: Verification, assigneeID: str, location: int
    ) -> int:
        try:
            self.LOG.info(
                "punch_employee_in: verification={} assigneeID={} location={}".format(
                    verification, assigneeID, location
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # check employee punches if they have one
                    punches = self.get_active_employee_punches(assigneeID)
                    # we have punches that need to be punched out
                    if len(punches) > 0:
                        raise Exception(
                            "Unable to punch in employee, an existing punch already exists!"
                        )

                    # checkin employee
                    else:
                        sql.execute(
                            self.insert_employee_punch_link,
                            (location, assigneeID, verification.get_verification()),
                        )

                        if len(sql.table) != 0:
                            linkID = int(sql.table[0]["ID"])
                        else:
                            raise Exception(
                                "No results found with the insert_employee_punch_link query!"
                            )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("punch_employee_in: error={}".format(e))
            self.LOG.info("punch_employee_in: END")
            return -1

        self.LOG.info("punch_employee_in: linkID={0}".format(linkID))
        self.LOG.info("punch_employee_in: END")
        return linkID

    # gets a list of active punches given an employeeID
    # input: EmployeeID
    # output: Punches on success, [] on error
    def get_active_employee_punches(self, employeeID: str) -> list:
        try:
            self.LOG.info(
                "get_active_employee_punches: employeeID={}".format(employeeID)
            )

            punches = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_employee_punch_links, (employeeID))
                if len(sql.table) != 0:
                    punches = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_employee_punch_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_employee_punches: error={}".format(e))
            self.LOG.info("get_active_employee_punches: END")
            return []

        self.LOG.info("get_active_employee_punches: punches={0}".format(punches))
        self.LOG.info("get_active_employee_punches: END")
        return punches

    # given a date range, gets an employees punches in total
    # input: EmployeeID, StartDate, EndDate
    # output: Punches on success, [] on error
    def get_employee_punches_by_date(
        self, employeeID: str, startdate: str, enddate: str
    ) -> list:
        try:
            self.LOG.info(
                "get_employee_punches: employeeID={} startdate={} enddate={}".format(
                    employeeID, startdate, enddate
                )
            )

            punches = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_employee_punch_links_by_date,
                    (employeeID, startdate, enddate, startdate, enddate),
                )

                if len(sql.table) != 0:
                    punches = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employee_punch_links_by_date query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_punches: error={}".format(e))
            self.LOG.info("get_employee_punches: END")
            return []

        self.LOG.info("get_employee_punches: punches={0}".format(punches))
        self.LOG.info("get_employee_punches: END")
        return punches

    # Create an employee submission
    # input: verification, employeeID, firstname, technician, department, lastname, labName, BadgeID, HEXBadgeID, PIN
    # output: Employee, [] on error
    def create_employee(
        self,
        verification: Verification,
        technician: bool,
        department: str,
        labName: str,
        manager: bool,
        firstname: str,
        lastname: str,
        HEXBadgeID: str,
    ) -> list:
        try:
            self.LOG.info(
                "create_employee: technician={} department={} labName={} manager={} firstname={} lastname={} HEXBadgeID={} ".format(
                    technician,
                    department,
                    labName,
                    manager,
                    firstname,
                    lastname,
                    HEXBadgeID,
                )
            )

            employee = []

            # Remove any ":" separators from hexbadge entered
            hexbadge = HEXBadgeID.replace(":", "")
            # convert hexbadge into badge
            if len(hexbadge) % 2 != 0:
                raise Exception("Hexbadge must have a length divisible by 2!")

            badge = ""
            for i in range(0, len(hexbadge), 2):
                j = i + 2
                badge += str(int(hexbadge[i:j], 16))

            # get pin
            pin = random.randint(1000, 9999)

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_employee,
                        (
                            firstname.capitalize(),
                            lastname.capitalize(),
                            technician,
                            department,
                            labName.capitalize(),
                            manager,
                            verification.get_verification(),
                            badge,
                            hexbadge,
                            pin,
                        ),
                    )

                    if len(sql.table) != 0:
                        employee = sql.table
                    else:
                        raise Exception(
                            "No results found with the insert_employee query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_employee: error={}".format(e))
            self.LOG.info("create_employee: END")
            return []

        self.LOG.info("create_employee: employee={0}".format(employee))
        self.LOG.info("create_employee: END")
        return employee

    # Updates Employee with the information passed
    # output: Employee on success, {} on error
    def update_employee(
        self,
        verification: Verification,
        technician: bool,
        department: str,
        labName: str,
        manager: bool,
        firstname: str,
        lastname: str,
        HEXBadgeID: str,
        employeeID: int,
        status: int,
    ) -> dict:
        try:
            self.LOG.info(
                "update_employee: employeeID={} firstname={} lastname={} hexbadge={} manager={} labName={} department={} technician={} status={}".format(
                    employeeID,
                    firstname,
                    lastname,
                    HEXBadgeID,
                    manager,
                    labName,
                    department,
                    technician,
                    status,
                )
            )

            employee = {}

            # Remove any ":" separators from hexbadge entered
            hexbadge = HEXBadgeID.replace(":", "")
            # convert hexbadge into badge
            if len(hexbadge) % 2 != 0:
                raise Exception("Hexbadge must have a length divisible by 2!")

            badge = ""

            for i in range(0, len(hexbadge), 2):
                j = i + 2
                badge += str(int(hexbadge[i:j], 16))

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_selected_employee,
                        (
                            firstname.capitalize(),
                            lastname.capitalize(),
                            technician,
                            department,
                            labName.capitalize(),
                            manager,
                            badge,
                            hexbadge,
                            status,
                            employeeID,
                        ),
                    )

                    if len(sql.table) != 0:
                        employee = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the update_selected_employee query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_employee: error={}".format(e))
            self.LOG.info("update_employee: END")
            return {}

        self.LOG.info("update_employee: employee={0}".format(employee))
        self.LOG.info("update_employee: END")
        return employee

    # get employee tokens
    def get_employee_tokens(self, employeeID: str) -> list:
        try:
            self.LOG.info("get_employee_tokens: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_employee_tokens_by_employee, (employeeID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employee_tokens query!"
                    )
        except Exception as e:
            self.LOG.error("get_employee_tokens: error={}".format(e))
            self.LOG.info("get_employee_tokens: END")
            return []  # other error

        self.LOG.info("get_employee_tokens: vendors={}".format(info))
        self.LOG.info("get_employee_tokens: END")
        return info  # no error

    # create employee token link
    def create_employee_token_link(
        self, employeeID: str, tokenID: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info("create_employee_token_link: BEGIN")

            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_employee_token_link,
                        (employeeID, tokenID, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the create_employee_token_link query!"
                        )

            else:
                self.LOG.info(
                    "create_employee_endpoint_links: Error: Invalid Verification"
                )
                return -1
        except Exception as e:
            self.LOG.error("create_employee_token_link: error={}".format(e))
            self.LOG.info("create_employee_token_link: END")
            return -1  # other error

        self.LOG.info("create_employee_token_link: vendors={}".format(info))
        self.LOG.info("create_employee_token_link: END")
        return info  # no error

    # get employee endpoint links
    # input: endpoint id
    # output: links on success, [] on error
    def get_employee_endpoint_link(self, employeeID: int) -> list:
        try:
            self.LOG.info("get_employee_endpoint_link: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_employee_endpoint_links, (employeeID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employee_endpoint_link query!"
                    )

        except Exception as e:
            self.LOG.error("get_employee_endpoint_link: error={}".format(e))
            self.LOG.info("get_employee_endpoint_link: END")
            return []  # other error

        self.LOG.info("get_employee_endpoint_link: vendors={}".format(info))
        self.LOG.info("get_employee_endpoint_link: END")
        return info  # no error

    # create employee endpoint links
    # input:  employeeID, endpointIDs, verification
    # output: [[ID]] on success
    def create_employee_endpoint_links(
        self, employeeID: str, endpointIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_employee_endpoint_links: employeeID={} endpointIDs={} verification={}".format(
                    employeeID, endpointIDs, verification
                )
            )
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    employeeID = self.employee_check(str(employeeID).lower())
                    if len(employeeID) == 0:
                        raise Exception("Invalid employeeID!")

                    endpointIDs_string = ",".join(map(str, endpointIDs))
                    self.LOG.info(
                        "create_employee_endpoint_links: employeeID={} endpointIDs={} verification={}".format(
                            employeeID, endpointIDs_string, verification
                        )
                    )
                    sql.execute(
                        self.insert_employee_endpoint_links,
                        (
                            employeeID,
                            verification.get_verification(),
                            endpointIDs_string,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to create_employee_endpoint_links {}!".format(info)
                        )
            else:
                self.LOG.info(
                    "create_employee_endpoint_links: Error: Invalid Verification"
                )
                return []
        except Exception as e:
            self.LOG.error("create_employee_endpoint_links: error={}".format(e))
            self.LOG.info("create_employee_endpoint_links: END")
            return []  # other error

        self.LOG.info("create_employee_endpoint_links: entry={}".format(info))
        self.LOG.info("create_employee_endpoint_links: END")
        return info  # no error

    # update employee endpoint links status
    # input:  status, linkIDs, verification
    # output: [[ID]] on success
    def update_employee_endpoint_links_status(
        self, status: int, linkIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_employee_endpoint_links_status: status={} linkIDs={} verification={}".format(
                    status, linkIDs, verification
                )
            )
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    linkIDs_string = ",".join(map(str, linkIDs))
                    sql.execute(
                        self.update_employee_endpoint_link_status,
                        (status, linkIDs_string),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_employee_endpoint_links_status {}!".format(
                                info
                            )
                        )
            else:
                self.LOG.info(
                    "update_employee_endpoint_links_status: Error: Invalid Verification"
                )
                return []
        except Exception as e:
            self.LOG.error("update_employee_endpoint_links_status: error={}".format(e))
            self.LOG.info("update_employee_endpoint_links_status: END")
            return []  # other error

        self.LOG.info("update_employee_endpoint_links_status: entry={}".format(info))
        self.LOG.info("update_employee_endpoint_links_status: END")
        return info  # no error

    # get employee endpoint params
    # input: parent id
    # output: links on success, [] on error
    def get_employee_endpoint_params(self, employeeID: str, endpointID: int) -> list:
        try:
            self.LOG.info("get_employees_endpoint_params: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_employee_endpoint_params_by_employee_endpoint,
                    (employeeID, endpointID),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employees_endpoint_params query!"
                    )

        except Exception as e:
            self.LOG.error("get_employees_endpoint_params: error={}".format(e))
            self.LOG.info("get_employees_endpoint_params: END")
            return []  # other error

        self.LOG.info("get_employees_endpoint_params: vendors={}".format(info))
        self.LOG.info("get_employees_endpoint_params: END")
        return info  # no error

    def create_employee_endpoint_links(
        self, employeeID: int, endpointIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_employee_endpoint_links: employeeID={} endpointIDs={}".format(
                    employeeID, endpointIDs
                )
            )
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    endpointIDs_string = ",".join(map(str, endpointIDs))
                    # add link
                    sql.execute(
                        self.insert_employee_endpoint_links,
                        (
                            employeeID,
                            endpointIDs_string,
                            verification.get_verification(),
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception("Unable to create_employee_endpoint_links!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("create_employee_endpoint_links: error={}".format(e))
            self.LOG.info("create_employee_endpoint_links: END")
            return []  # other error

        self.LOG.info("create_employee_endpoint_links: entry={}".format(info))
        self.LOG.info("create_employee_endpoint_links: END")
        return info

    def update_employee_endpoint_link_statuses(
        self, status: int, linkIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_employee_endpoint_link_statuses: status={} linkIDs={}".format(
                    status, linkIDs
                )
            )
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    linkIDs_string = ",".join(linkIDs)
                    # update status
                    sql.execute(
                        self.update_employee_endpoint_link_status_by_link_id,
                        (status, linkIDs_string),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_employee_endpoint_link_statuses!"
                        )
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("update_employee_endpoint_link_statuses: error={}".format(e))
            self.LOG.info("update_employee_endpoint_link_statuses: END")
            return []  # other error

        self.LOG.info("update_employee_endpoint_link_statuses: entry={}".format(info))
        self.LOG.info("update_employee_endpoint_link_statuses: END")
        return info  # no error

    # gets a list of all departments
    # input: N/A
    # output: departments on success, [] on error
    def get_departments(self) -> list:
        try:
            self.LOG.info("get_departments: BEGIN")

            # define employee info
            departments = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Departments)
                if len(sql.table) != 0:
                    departments = sql.table
                else:
                    raise Exception("No results found with the get_Departments query!")

        except Exception as e:
            self.LOG.error("get_departments: error={}".format(e))
            self.LOG.info("get_departments: END")
            return []

        self.LOG.info("get_departments: departments={}".format(len(departments)))
        self.LOG.info("get_departments: END")
        return departments  # no error


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
