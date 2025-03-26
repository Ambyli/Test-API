#!/usr/bin/env python3.7
import logging
import os
import concurrent.futures
import requests
from os import link
from typing import Dict, List

from .dashboard_config import DashboardConfig
from .verification_pull import Verification
from .gauge_pull import Gauge
from .shade_regex import gen_steps
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .file_pull import File


class Dashboard(DashboardConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        DashboardConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # Create a file object
        self.file = File()

        # Current working values
        result = []
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

    # gets all chart types
    # input: N/A
    # output: All chart types on success, [] on error
    def get_all_chart_types(self) -> list:
        try:
            self.LOG.info("get_all_chart_types: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_chart_types)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_chart_types query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_chart_types: error={}".format(e))
            self.LOG.info("get_all_chart_types: END")
            return []  # other error

        self.LOG.info("get_all_chart_types: vendors={}".format(len(info)))
        self.LOG.info("get_all_chart_types: END")
        return info  # no error

    # gets all dashboards
    # input: N/A
    # output: All chart on success, [] on error
    def get_all_dashboards(
        self, searchName: str, offset: int, rows: int, statuses: list
    ) -> list:
        try:
            self.LOG.info("get_all_dashboards: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(
                    self.get_dashboards, (status_string, searchName, offset, rows)
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_dashboards query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_dashboards: error={}".format(e))
            self.LOG.info("get_all_dashboards: END")
            return []  # other error

        self.LOG.info("get_all_dashboards: vendors={}".format(len(info)))
        self.LOG.info("get_all_dashboards: END")
        return info  # no error

    # get dashboard by id
    # input: dashboard id
    # output: All chart on success, [] on error
    def get_dashboard_by_id(self, dashboardID: int, statuses: list) -> object:
        try:
            self.LOG.info("get_dashboard_by_id: BEGIN")

            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(
                    self.get_dashboard_by_dashboard_id, (status_string, dashboardID)
                )
                if len(sql.table) != 0:
                    info = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_dashboard_by_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_dashboard_by_id: error={}".format(e))
            self.LOG.info("get_dashboard_by_id: END")
            return -1  # other error

        self.LOG.info("get_dashboard_by_id: vendors={}".format(len(info)))
        self.LOG.info("get_dashboard_by_id: END")
        return info  # no error

    # get dashboard by chart id
    # input: chart id
    # output: All dashboard on success, [] on error
    def get_dashboard_by_chart(self, chartID: int) -> list:
        try:
            self.LOG.info("get_dashboard_by_chart: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_dashboards_by_chart_id, (chartID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_dashboard_by_chart query!"
                    )

        except Exception as e:
            self.LOG.error("get_dashboard_by_chart: error={}".format(e))
            self.LOG.info("get_dashboard_by_chart: END")
            return []  # other error

        self.LOG.info("get_dashboard_by_chart: vendors={}".format(len(info)))
        self.LOG.info("get_dashboard_by_chart: END")
        return info  # no error

    # gets all dashboards by verification
    # input: verification
    # output: All chart on success, [] on error
    def get_dashboard_by_employee(self, employeeID: str, statuses: list) -> list:
        try:
            self.LOG.info("get_dashboard_by_employee: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(
                    self.get_dashboards_employee_id, (status_string, employeeID)
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_dashboard_by_employee query!"
                    )

        except Exception as e:
            self.LOG.error("get_dashboard_by_employee: error={}".format(e))
            self.LOG.info("get_dashboard_by_employee: END")
            return []  # other error

        self.LOG.info("get_dashboard_by_employee: vendors={}".format(len(info)))
        self.LOG.info("get_dashboard_by_employee: END")
        return info  # no error

    # create new dashboard
    # input:  name, description, creator, link
    # output: ID on success
    def create_new_dashboard(
        self,
        name: str,
        description: str,
        verification: Verification,
        data: str,
        refreshRate: int,
        visibility: int,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_dashboard: name={} description={} verification={} refreshRate={} visibility={}".format(
                    name, description, verification, refreshRate, visibility
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    # add vendor
                    sql.execute(
                        self.create_dashboard,
                        (
                            name,
                            description,
                            verification.get_verification(),
                            refreshRate,
                            visibility,
                            data,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Create Dashboard Log
                        self.log_dashboard_change(info, verification, 67)
                    else:
                        raise Exception(
                            "Unable to create new dashboard {}!".format(info)
                        )
            else:
                self.LOG.info("create_new_dashboard: Error: Invalid verification")
                return -1
        except Exception as e:
            self.LOG.error("create_new_dashboard: error={}".format(e))
            self.LOG.info("create_new_dashboard: END")
            return -1  # other error

        self.LOG.info("create_new_dashboard: entry={}".format(info))
        self.LOG.info("create_new_dashboard: END")
        return info  # no error

    # update dashboard
    # input: name, description
    # output: ID on success
    def update_dashboard_info(
        self,
        name: str,
        description: str,
        refreshRate: int,
        data: str,
        thumbnailLink: str,
        dashboardID: int,
        verification: Verification,
        visibility: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_dashboard_info: name={} description={} refreshRate={} thumbnailLink={} dashboardID={} verification={} visibility={}".format(
                    name,
                    description,
                    refreshRate,
                    thumbnailLink,
                    dashboardID,
                    verification,
                    visibility,
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.update_dashboard,
                        (
                            name,
                            description,
                            refreshRate,
                            data,
                            thumbnailLink,
                            visibility,
                            dashboardID,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Log dashboard update
                        self.log_dashboard_change(info, verification, 68)
                    else:
                        raise Exception("Unable to update dashboard {}!".format(info))
            else:
                self.LOG.info("update_dashboard_info: Error: Invalid verification")
                return -1
        except Exception as e:
            self.LOG.error("update_dashboard_info: error={}".format(e))
            self.LOG.info("update_dashboard_info: END")
            return -1

        self.LOG.info("update_dashboard_info: entry={}".format(info))
        self.LOG.info("update_dashboard_info: END")
        return info  # no error

    # update dashboard status
    # input: status, dashboardID
    # output: ID on success
    def update_dashboard_status(
        self, status: int, dashboardID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "update_dashboard_status: status={} dashboardID={} verification={}".format(
                    status, dashboardID, verification
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.update_dashboard_status_by_dashboard_id,
                        (status, dashboardID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Log Dashboard Update
                        self.log_dashboard_change(info, verification, 68)
                    else:
                        raise Exception(
                            "Unable to update dashboard status {}!".format(info)
                        )
            else:
                self.LOG.info("update_dashboard_status: Error: Invalid Verification")
                return -1

        except Exception as e:
            self.LOG.error("update_dashboard_status: error={}".format(e))
            self.LOG.info("update_dashboard_status: END")
            return -1

        self.LOG.info("update_dashboard_status: entry={}".format(info))
        self.LOG.info("update_dashboard_status: END")
        return info  # no error

    # gets all chart
    # input: N/A
    # output: All chart on success, [] on error
    def get_all_charts(
        self,
        searchName: str,
        chartTypeIDs: list,
        offset: int,
        rows: int,
        statuses: list,
    ) -> list:
        try:
            self.LOG.info("get_all_charts: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                chart_type_ids_string = ",".join(map(str, chartTypeIDs))
                sql.execute(
                    self.get_charts,
                    (
                        status_string,
                        searchName,
                        chart_type_ids_string,
                        chart_type_ids_string,
                        offset,
                        rows,
                    ),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No results found with the get_all_charts query!")

        except Exception as e:
            self.LOG.error("get_all_charts: error={}".format(e))
            self.LOG.info("get_all_charts: END")
            return []  # other error

        self.LOG.info("get_all_charts: vendors={}".format(len(info)))
        self.LOG.info("get_all_charts: END")
        return info  # no error

    # gets all chart by type id
    # input: type id
    # output: All chart on success, [] on error
    def get_all_charts_by_type_id(self, typeID: int, statuses: list) -> list:
        try:
            self.LOG.info("get_all_charts_by_type_id: BEGIN")

            info = []
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(self.get_charts_by_type, (status_string, typeID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_charts_by_type_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_charts_by_type_id: error={}".format(e))
            self.LOG.info("get_all_charts_by_type_id: END")
            return []  # other error

        self.LOG.info("get_all_charts_by_type_id: vendors={}".format(len(info)))
        self.LOG.info("get_all_charts_by_type_id: END")
        return info  # no error

    # gets all chart by creator id
    # input: creator id
    # output: All chart on success, [] on error
    def get_all_charts_by_creator_id(self, creatorID: str, statuses: list) -> list:
        try:
            self.LOG.info("get_all_charts_by_creator_id: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(self.get_charts_by_creator, (status_string, creatorID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_charts_by_creator_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_charts_by_creator_id: error={}".format(e))
            self.LOG.info("get_all_charts_by_creator_id: END")
            return []  # other error

        self.LOG.info("get_all_charts_by_creator_id: vendors={}".format(len(info)))
        self.LOG.info("get_all_charts_by_creator_id: END")
        return info  # no error

    # gets all chart by chart id
    # input: creator id
    # output: All chart on success, [] on error
    def get_chart_by_chart_id(self, chartID: int, statuses: list) -> list:
        try:
            self.LOG.info("get_chart_by_chart_id: BEGIN")
            self.LOG.info(f"get_chart_by_chart_id: {chartID} {statuses}")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(self.get_chart_by_chart, (status_string, chartID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_chart_by_chart_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_chart_by_chart_id: error={}".format(e))
            self.LOG.info("get_chart_by_chart_id: END")
            return []  # other error

        self.LOG.info("get_chart_by_chart_id: vendors={}".format(len(info)))
        self.LOG.info("get_chart_by_chart_id: END")
        return info  # no error

    # gets all charts by dashboard id
    # input: dashboard id
    # output: All chart on success, [] on error
    def get_charts_by_dashboard(self, dashboardID: int) -> list:
        try:
            self.LOG.info("get_charts_by_dashboard: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_charts_by_dashboard_id, (dashboardID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_charts_by_dashboard query!"
                    )

        except Exception as e:
            self.LOG.error("get_charts_by_dashboard: error={}".format(e))
            self.LOG.info("get_charts_by_dashboard: END")
            return []  # other error

        self.LOG.info("get_charts_by_dashboard: vendors={}".format(len(info)))
        self.LOG.info("get_charts_by_dashboard: END")
        return info  # no error

    # gets all charts by query id
    # input: query id
    # output: All chart on success, [] on error
    def get_charts_by_query(self, queryID: int) -> list:
        try:
            self.LOG.info("get_charts_by_query: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_chart_by_query_id, (queryID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_charts_by_query query!"
                    )

        except Exception as e:
            self.LOG.error("get_charts_by_query: error={}".format(e))
            self.LOG.info("get_charts_by_query: END")
            return []  # other error

        self.LOG.info("get_charts_by_query: vendors={}".format(len(info)))
        self.LOG.info("get_charts_by_query: END")
        return info  # no error

    # gets all charts by query id
    # input: query id
    # output: All chart on success, [] on error
    def get_charts_by_query(self, queryID: int) -> list:
        try:
            self.LOG.info("get_charts_by_query: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_chart_by_query_id, (queryID))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_charts_by_query query!"
                    )

        except Exception as e:
            self.LOG.error("get_charts_by_query: error={}".format(e))
            self.LOG.info("get_charts_by_query: END")
            return []  # other error

        self.LOG.info("get_charts_by_query: vendors={}".format(len(info)))
        self.LOG.info("get_charts_by_query: END")
        return info  # no error

    # create new chart
    # input: name, description, creator, typeID, link
    # output: ID on success
    def create_new_chart(
        self,
        name: str,
        description: str,
        verification: Verification,
        typeID: int,
        queryID: int,
        data: str,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_chart: name={} description={} verification={} typeID={} queryID={}".format(
                    name, description, verification, typeID, queryID
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.create_chart,
                        (
                            name,
                            description,
                            verification.get_verification(),
                            typeID,
                            queryID,
                            11,
                            data,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Create Chart Log
                        self.log_chart_change(info, verification, 65)
                    else:
                        raise Exception("Unable to create new chart {}!".format(info))
            else:
                self.LOG.info("create_new_chart: Error: Invalid verification")
                return -1
        except Exception as e:
            self.LOG.error("create_new_chart: error={}".format(e))
            self.LOG.info("create_new_chart: END")
            return -1  # other error

        self.LOG.info("create_new_chart: entry={}".format(info))
        self.LOG.info("create_new_chart: END")
        return info  # no error

    # update chart
    # input: name, description
    # output: ID on success
    def update_chart_info(
        self,
        name: str,
        description: str,
        queryID: int,
        chartID: int,
        data: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "update_chart_info: name={} description={} chartID={} verification={}".format(
                    name, description, chartID, verification
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.update_chart_by_chart_id,
                        (name, description, queryID, data, chartID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Create Chart Log
                        self.log_chart_change(info, verification, 66)
                    else:
                        raise Exception("Unable to update chart {}!".format(info))
            else:
                self.LOG.info("update_chart_info: Error: Invalid verification")
                return -1
        except Exception as e:
            self.LOG.error("update_chart_info: error={}".format(e))
            self.LOG.info("update_chart_info: END")
            return -1

        self.LOG.info("update_chart_info: entry={}".format(info))
        self.LOG.info("update_chart_info: END")
        return info  # no error

    # update chart status
    # input: name, description
    # output: ID on success
    def update_chart_status(
        self, status: int, chartIDs: list, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "update_chart_status: status={} chartIDs={} verification={}".format(
                    status, chartIDs, verification
                )
            )
            info = -1
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    chartIDs = ",".join(map(str, chartIDs))
                    # add vendor
                    sql.execute(
                        self.update_chart_status_by_chart_ids,
                        (
                            status,
                            chartIDs,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                        # Create Chart Log
                        self.log_chart_change(info, verification, 66)
                    else:
                        raise Exception("Unable to update chart {}!".format(info))
            else:
                self.LOG.info("update_chart_status: Error: Invalid verification")
                return -1
        except Exception as e:
            self.LOG.error("update_chart_status: error={}".format(e))
            self.LOG.info("update_chart_status: END")
            return -1  # other error

        self.LOG.info("update_chart_status: entry={}".format(info))
        self.LOG.info("update_chart_status: END")
        return info  # no error

    # gets all chart dashboard Link by dashboard id
    # input: dashboard id
    # output: All chart on success, [] on error
    def get_chart_dashboard_links_by_dashboard(
        self, dashboardID: int, statuses: list
    ) -> list:
        try:
            self.LOG.info("get_chart_dashboard_links_by_dashboard: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(
                    self.get_chart_dashboard_link_by_dashboard_id,
                    (dashboardID, status_string),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_chart_dashboard_links_by_dashboard query!"
                    )

        except Exception as e:
            self.LOG.error("get_chart_dashboard_links_by_dashboard: error={}".format(e))
            self.LOG.info("get_chart_dashboard_links_by_dashboard: END")
            return []  # other error

        self.LOG.info(
            "get_chart_dashboard_links_by_dashboard: vendors={}".format(len(info))
        )
        self.LOG.info("get_chart_dashboard_links_by_dashboard: END")
        return info  # no error

    # create new chart dashboard links
    # input: name, description, creator, typeID, link
    # output: ID on success
    def create_chart_dashboard_links(
        self, dashboardID: int, chartIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_chart_dashboard_links: dashboardID={} chartIDs={} verification={}".format(
                    dashboardID, chartIDs, verification
                )
            )
            info = []
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    chartIDs_string = ",".join([str(chartID) for chartID in chartIDs])
                    sql.execute(
                        self.create_chart_dashboard_link,
                        (dashboardID, verification.get_verification(), chartIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = [row["ID"] for row in sql.table]

                        for dashboard_link_ID in info:
                            self.log_chart_dashboard_link_change(
                                dashboard_link_ID, verification, 63
                            )
                    else:
                        raise Exception("Unable to create new chart {}!".format(info))
            else:
                self.LOG.info(
                    "create_chart_dashboard_links: Error: Invalid verification"
                )
                return []
        except Exception as e:
            self.LOG.error("create_chart_dashboard_links: error={}".format(e))
            self.LOG.info("create_chart_dashboard_links: END")
            return []  # other error

        self.LOG.info("create_chart_dashboard_links: entry={}".format(info))
        self.LOG.info("create_chart_dashboard_links: END")
        return info  # no error

    # update chart dashboard links status
    # input: name, description
    # output: ID on success
    def update_chart_dashboard_links_status(
        self, status: int, linkIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_chart_dashboard_links_status: status={} linkIDs={} verification={}".format(
                    status, linkIDs, verification
                )
            )
            info = []
            # check verification ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    linkIDs_string = ",".join([str(chartID) for chartID in linkIDs])
                    sql.execute(
                        self.Update_chart_dashboard_links_status_by_link_id,
                        (
                            status,
                            linkIDs_string,
                        ),
                    )
                    if len(sql.table) != 0:
                        info = [row["ID"] for row in sql.table]

                        for dashboard_link_ID in info:
                            self.log_chart_dashboard_link_change(
                                dashboard_link_ID, verification, 64
                            )
                    else:
                        raise Exception(
                            "Unable to update chart dashboard links status {}!".format(
                                info
                            )
                        )
            else:
                self.LOG.info(
                    "update_chart_dashboard_links_status: Error: Invalid verification"
                )
                return []
        except Exception as e:
            self.LOG.error("update_chart_dashboard_links_status: error={}".format(e))
            self.LOG.info("update_chart_dashboard_links_status: END")
            return []  # other error

        self.LOG.info("update_chart_dashboard_links_status: entry={}".format(info))
        self.LOG.info("update_chart_dashboard_links_status: END")
        return info  # no error

    # logs a change to chart_dashboard_links
    # input : chartDashboardLinkID, verification, logtype
    # output: int
    def log_chart_dashboard_link_change(
        self, chartDashboardLinkID: int, verification: Verification, logtype: int
    ) -> int:
        try:
            self.LOG.info(
                "log_chart_dashboard_link_change: queryID={} verification={} logtype={}".format(
                    chartDashboardLinkID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 63:
                        change = "Created"
                        description = "ChartDashboardLink Created"
                    if logtype == 64:
                        change = "Updated"
                        description = "ChartDashboardLink Updated"

                    # Create chart_dashboard_link_log
                    sql.execute(
                        self.insert_chart_dashboard_link_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            chartDashboardLinkID,
                            chartDashboardLinkID,
                            chartDashboardLinkID,
                            chartDashboardLinkID,
                            chartDashboardLinkID,
                            chartDashboardLinkID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_chart_dashboard_link_change: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the log_chart_dashboard_link_change query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_chart_dashboard_link_change: error={}".format(e))

        self.LOG.info("log_chart_dashboard_link_change: END")
        return -1

    # gets all queries
    # input: offset, row, Statuses
    # output: All chart on success, [] on error
    def get_all_queries(
        self, searchName: str, offset: int, rows: int, statuses: list
    ) -> list:
        try:
            self.LOG.info("get_all_queries: BEGIN")
            self.LOG.info(
                "get_all_queries: offset={} rows={} statuses={}".format(
                    offset, rows, statuses
                )
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                status_string = ",".join(map(str, statuses))
                sql.execute(self.get_queries, (status_string, searchName, offset, rows))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No results found with the get_all_queries query!")

        except Exception as e:
            self.LOG.error("get_all_queries: error={}".format(e))
            self.LOG.info("get_all_queries: END")
            return []  # other error

        self.LOG.info("get_all_queries: vendors={}".format(len(info)))
        self.LOG.info("get_all_queries: END")
        return info  # no error

    # gets all queries by ids
    # input: ids
    # output: All chart on success, [] on error
    def get_all_queries_by_ids(self, ids: list) -> list:
        try:
            self.LOG.info("get_all_queries_by_ids: BEGIN")
            self.LOG.info("get_all_queries_by_ids: ids={}".format(ids))
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                ids_string = ",".join(map(str, ids))
                sql.execute(self.get_queries_by_query_ids, (ids_string))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_queries_by_ids query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_queries_by_ids: error={}".format(e))
            self.LOG.info("get_all_queries_by_ids: END")
            return []  # other error

        self.LOG.info("get_all_queries_by_ids: vendors={}".format(len(info)))
        self.LOG.info("get_all_queries_by_ids: END")
        return info  # no error

    # create new query
    # input: name, description, creator, queryString,
    # output: ID on success
    def create_new_query(
        self,
        name: str,
        description: str,
        verification: Verification,
        queryString: str,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_query: name={} description={} verification={} queryString={}".format(
                    name, description, verification, queryString
                )
            )
            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.create_query,
                        (
                            queryString,
                            verification.get_verification(),
                            name,
                            description,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]

                        # Log Query Creation
                        self.log_query_change(info, verification, 61)

                    else:
                        raise Exception("Unable to create new chart {}!".format(info))
            else:
                self.LOG.info("create_new_query: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("create_new_query: error={}".format(e))
            self.LOG.info("create_new_query: END")
            return -1  # other error

        self.LOG.info("create_new_query: entry={}".format(info))
        self.LOG.info("create_new_query: END")
        return info  # no error

    # update query
    # input: name, description, employee, queryString,
    # output: ID on success
    def update_query(
        self,
        name: str,
        description: str,
        verification: Verification,
        queryString: str,
        queryID: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_query: name={} description={} verification={} queryString={} queryID={}".format(
                    name, description, verification, queryString, queryID
                )
            )
            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # Update Query
                    sql.execute(
                        self.update_query_by_query_id,
                        (name, description, queryString, queryID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]

                        # Log Query Edit
                        self.log_query_change(info, verification, 62)

                    else:
                        raise Exception("Unable to create new chart {}!".format(info))
            else:
                self.LOG.info("update_query: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("update_query: error={}".format(e))
            self.LOG.info("update_query: END")
            return -1  # other error

        self.LOG.info("update_query: entry={}".format(info))
        self.LOG.info("update_query: END")
        return info  # no error

    # update query
    # input: name, description, creator, queryString,
    # output: ID on success
    def update_query_status(
        self, verification: Verification, status: int, queryID: int
    ) -> int:
        try:
            self.LOG.info(
                "verification={} status={} queryID={}".format(
                    verification, status, queryID
                )
            )
            info = -1
            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.update_query_status_by_query_id,
                        (status, queryID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]

                        # Log Query Edit
                        self.log_query_change(info, verification, 62)

                    else:
                        raise Exception("Unable to create new chart {}!".format(info))
            else:
                self.LOG.info("update_query_status: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("update_query_status: error={}".format(e))
            self.LOG.info("update_query_status: END")
            return -1  # other error

        self.LOG.info("update_query_status: entry={}".format(info))
        self.LOG.info("update_query_status: END")
        return info  # no error

    # execute custom query
    # input: query
    # output: {data: [], headerOrder: []}
    def execute_custom_query(self, query: str) -> dict:
        try:
            self.LOG.info("execute_custom_query: query={} ".format(query))
            # Initialize the info dictionary
            info = {"data": None, "headerOrder": None, "types": None}
            with SQL_Pull()(self.sql_config)() as sql:
                sql.update_con_string(
                    None,
                    None,
                    os.getenv("SQL_USERNAME_READONLY"),
                    os.getenv("SQL_PASSWORD_READONLY"),
                    None,
                )
                sql.execute(query)
                # check if we got valid types
                if len(sql.types) == 0:
                    raise Exception(
                        "Unable to execute custom query or no results found: {}".format(
                            query
                        )
                    )
                # get result data
                if len(sql.table) != 0:
                    info["data"] = sql.table
                    # somehow the columns order of data here different from data sent to react,
                    # so headerOrder will be used to sort columns to match data return from database in react
                    info["headerOrder"] = list(info["data"][0].keys())
                    info["types"] = sql.types

        except Exception as e:
            self.LOG.error("execute_custom_query: error={}".format(e))
            self.LOG.error("execute_custom_query: END")
            return {}  # Indicate error condition

        self.LOG.info("execute_custom_query: END")
        return info  # Return results

    # logs a change to a queries
    # input : queryID, verification, logtype
    # output: int
    def log_query_change(
        self, queryID: int, verification: Verification, logtype: int
    ) -> int:
        try:
            self.LOG.info(
                "log_query_change: queryID={} verification={} logtype={}".format(
                    queryID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 61:
                        change = "Created"
                        description = "Query Created"
                    if logtype == 62:
                        change = "Updated"
                        description = "Query Updated"

                    # Create query_log
                    sql.execute(
                        self.insert_query_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            queryID,
                            queryID,
                            queryID,
                            queryID,
                            queryID,
                            queryID,
                            queryID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_query_change: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the log_query_change query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_query_change: error={}".format(e))

        self.LOG.info("log_query_change: END")
        return -1

    # logs a change to a chart
    # input : ChartID, verification, logtype
    # output: int
    def log_chart_change(
        self, chartID: int, verification: Verification, logtype: int
    ) -> int:
        try:
            self.LOG.info(
                "log_chart_change: chartID={} verification={} logtype={}".format(
                    chartID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 65:
                        change = "Created"
                        description = "Chart Created"
                    if logtype == 66:
                        change = "Updated"
                        description = "Chart Updated"

                    # Create query_log
                    sql.execute(
                        self.insert_chart_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                            chartID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_chart_change: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the log_chart_change query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_chart_change: error={}".format(e))

        self.LOG.info("log_chart_change: END")
        return -1

    # logs a change to a Dashboard
    # input : DashboardID, verification, logtype
    # output: int
    def log_dashboard_change(
        self, dashboardID: int, verification: Verification, logtype: int
    ) -> int:
        try:
            self.LOG.info(
                "log_dashboard_change: dashboardID={} verification={} logtype={}".format(
                    dashboardID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 67:
                        change = "Created"
                        description = "Dashboard Created"
                    if logtype == 68:
                        change = "Updated"
                        description = "Dashboard Updated"

                    # Create query_log
                    sql.execute(
                        self.insert_dashboard_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                            dashboardID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_dashboard_change: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the log_dashboard_change_query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_dashboard_change: error={}".format(e))

        self.LOG.info("log_dashboard_change: END")
        return -1


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
