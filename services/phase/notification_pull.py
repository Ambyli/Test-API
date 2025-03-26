#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .shade_regex import gen_steps
from .sql_pull import SQL_Pull
from .notifications_config import NotificationsConfig
from .gauge_pull import Gauge
from .verification_pull import Verification
import json
import requests
import os


class Notifications(NotificationsConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        NotificationsConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

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

    # Select Notification Automations
    def get_notification_automations(
        self, name: str, offset: int, rows: int, statusIDs: str, roleIDs: str
    ) -> list:
        try:
            self.LOG.info("get_notification_automations: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if offset is not None and rows is not None:
                    sql.execute(
                        self.select_notification_automations_pagination,
                        (name, offset, rows, statusIDs, roleIDs),
                    )
                else:
                    sql.execute(self.select_notification_automations, (name,))

                if len(sql.table) > 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_notification_automations query!"
                    )
        except Exception as e:
            self.LOG.error("get_notification_automations: error={}".format(e))
            self.LOG.info("get_notification_automations: END")
            return []
        self.LOG.info("get_notification_automations: automations={}".format(info))
        self.LOG.info("get_notification_automations: END")
        return info

    # Select Notification Automation by ID
    def get_notification_automation_by_id(self, id: str) -> dict:
        try:
            self.LOG.info("get_notification_automations: BEGIN")
            info = {}
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.select_notification_automation_by_id,
                    (id,),
                )

                if len(sql.table) > 0:
                    info = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_notification_automations query!"
                    )
        except Exception as e:
            self.LOG.error("get_notification_automations: error={}".format(e))
            self.LOG.info("get_notification_automations: END")
            return {}
        self.LOG.info("get_notification_automations: automations={}".format(info))
        self.LOG.info("get_notification_automations: END")
        return info

    # Select Notification Automation by employeeID
    def select_notification_automation_by_employeeID(self, employeeID: int) -> list:
        try:
            self.LOG.info("select_notification_automation_by_employeeID: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.select_notification_automation_by_employee_id,
                    (employeeID),
                )

                if len(sql.table) > 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the select_notification_automation_by_employeeID query!"
                    )
        except Exception as e:
            self.LOG.error(
                "select_notification_automation_by_employeeID: error={}".format(e)
            )
            self.LOG.info("select_notification_automation_by_employeeID: END")
            return []
        self.LOG.info(
            "select_notification_automation_by_employeeID: automations={}".format(info)
        )
        self.LOG.info("select_notification_automation_by_employeeID: END")
        return info

    # Insert Notification Automations
    # status guide: active(11), off(5), delete(12)
    def create_notification_automation(
        self,
        name: str,
        description: str,
        func: str,
        interval: int,
        roleIDs: list,
        linkEmployeeIDs: list,
        status: int,
        verification: Verification,
    ) -> str:
        try:
            self.LOG.info("insert_notification_automation: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    roleIDs_string = (
                        None if len(roleIDs) == 0 else ",".join(map(str, roleIDs))
                    )
                    linkEmployeeIDs_string = (
                        None
                        if len(linkEmployeeIDs) == 0
                        else ",".join(map(str, linkEmployeeIDs))
                    )
                    sql.execute(
                        self.insert_notification_automation,
                        (
                            name,
                            description,
                            func,
                            interval,
                            verification.get_verification(),
                            roleIDs_string,
                            linkEmployeeIDs_string,
                            status,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to create new Notification Automations {}!".format(
                                info
                            )
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("insert_notification_automation: error={}".format(e))
            return None

        self.LOG.info("insert_notification_automation: entry={}".format(info))
        self.LOG.info("insert_notification_automation: END")
        return info  # no error

    # Update Notification Automation
    def update_notification_automation(
        self,
        id: str,
        name: str,
        description: str,
        func: str,
        interval: int,
        verification: Verification,
    ) -> str:
        try:
            self.LOG.info("update_notification_automation: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_notification_automation_by_id,
                        (name, description, func, interval, id),
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update Notification Automations {}!".format(info)
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_notification_automation: error={}".format(e))
            return None
        self.LOG.info("update_notification_automation: entry={}".format(info))
        self.LOG.info("update_notification_automation: END")
        return info  # no error

    # Update Notification Automation Status
    def update_notification_automation_status(
        self, id: str, status: int, verification: Verification
    ) -> str:
        try:
            self.LOG.info("update_notification_automation_status: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_notification_automation_status_by_id, (status, id)
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update Notification Automations Status {}!".format(
                                info
                            )
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_notification_automation_status: error={}".format(e))
            return None
        self.LOG.info("update_notification_automation_status: entry={}".format(info))
        self.LOG.info("update_notification_automation_status: END")
        return info  # no error

    # Select Role Notification Automation Links
    def get_role_notification_automation_links(self) -> list:
        try:
            self.LOG.info("get_role_notification_automation_links: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_role_notification_automation_links)
                if len(sql.table) > 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_role_notification_automation_links query!"
                    )
        except Exception as e:
            self.LOG.error("get_role_notification_automation_links: error={}".format(e))
            self.LOG.info("get_role_notification_automation_links: END")
            return []
        self.LOG.info("get_role_notification_automation_links: links={}".format(info))
        self.LOG.info("get_role_notification_automation_links: END")
        return info

    # Insert Role Notification Automation Links
    def create_role_notification_automation_links(
        self, roleIDs: list, notificationAutomationID: str, verification: Verification
    ) -> list:
        try:
            self.LOG.info("insert_role_notification_automation_link: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    roleIDs_string = ",".join(map(str, roleIDs))
                    sql.execute(
                        self.insert_role_notification_automation_links,
                        (
                            roleIDs_string,
                            notificationAutomationID,
                            verification.get_verification(),
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to insert_role_notification_automation_link {}!".format(
                                info
                            )
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error(
                "insert_role_notification_automation_link: error={}".format(e)
            )
            return []
        self.LOG.info("insert_role_notification_automation_link: entry={}".format(info))
        self.LOG.info("insert_role_notification_automation_link: END")
        return info  # no error

    # Update Role Notification Automation Status
    def update_status_role_notification_automation_links(
        self,
        status: int,
        roleIDs: list,
        notificationAutomationID: str,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_role_notification_automation_status: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    ids_string = ",".join(map(str, roleIDs))
                    sql.execute(
                        self.update_role_notification_automation_link_statuses,
                        (status, notificationAutomationID, ids_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_role_notification_automation_status {}!".format(
                                info
                            )
                        )
        except Exception as e:
            self.LOG.error(
                "update_role_notification_automation_status: error={}".format(e)
            )
            return []
        self.LOG.info(
            "update_role_notification_automation_status: entry={}".format(info)
        )
        self.LOG.info("update_role_notification_automation_status: END")
        return info  # no error

    # Select Employee Notification Links
    def get_employee_notification_links(self) -> list:
        try:
            self.LOG.info("get_employee_notification_links: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_employee_notification_links)
                if len(sql.table) > 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_employee_notification_links query!"
                    )
        except Exception as e:
            self.LOG.error("get_employee_notification_links: error={}".format(e))
            self.LOG.info("get_employee_notification_links: END")
            return []
        self.LOG.info("get_employee_notification_links: links={}".format(info))
        self.LOG.info("get_employee_notification_links: END")
        return info

    # Insert Employee Notification Links
    def create_employee_notification_link(
        self,
        notificationAutomationID: str,
        linkEmployeeIDs: list,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("insert_employee_notification_link: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    linkEmployeeIDs_string = ",".join(map(str, linkEmployeeIDs))

                    sql.execute(
                        self.insert_employee_notification_links,
                        (
                            str(linkEmployeeIDs_string),
                            notificationAutomationID,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to insert_employee_notification_links {}!".format(
                                info
                            )
                        )
        except Exception as e:
            self.LOG.error("insert_employee_notification_link: error={}".format(e))
            return []
        self.LOG.info("insert_employee_notification_links: entry={}".format(info))
        self.LOG.info("insert_employee_notification_links: END")
        return info  # no error

    # Update Employee Notification Links
    def update_status_employee_notification_links(
        self,
        linkedEmployeeIDs: list,
        id: str,
        status: int,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_employee_notification_link: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    linkedEmployeeIDs_string = ",".join(map(str, linkedEmployeeIDs))
                    sql.execute(
                        self.update_employee_notification_link_statuses,
                        (status, id, linkedEmployeeIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_employee_notification_links {}!".format(
                                info
                            )
                        )
        except Exception as e:
            self.LOG.error("update_employee_notification_link: error={}".format(e))
            return []
        self.LOG.info("update_employee_notification_link: entry={}".format(info))
        self.LOG.info("update_employee_notification_link: END")
        return info  # no error

    # Select Notification Automation Logs
    def get_notification_automation_logs(self) -> list:
        try:
            self.LOG.info("get_notification_automation_logs: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_notification_automation_logs)
                if len(sql.table) > 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_notification_automation_logs query!"
                    )
        except Exception as e:
            self.LOG.error("get_notification_automation_logs: error={}".format(e))
            self.LOG.info("get_notification_automation_logs: END")
            return []
        self.LOG.info("get_notification_automation_logs: logs={}".format(info))
        self.LOG.info("get_notification_automation_logs: END")
        return info

    # Insert Notification Automation Logs
    def create_notification_automation_log(
        self,
        logTypeID: int,
        change: str,
        logNote: str,
        loggedVerification: Verification,
        notificationAutomationID: int,
        name: str,
        description: str,
        func: str,
        interval: int,
    ) -> str:
        try:
            self.LOG.info("insert_notification_automation_log: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(loggedVerification, Verification)
                    and loggedVerification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_notification_automation_log,
                        (
                            logTypeID,
                            change,
                            logNote,
                            loggedVerification,
                            notificationAutomationID,
                            name,
                            description,
                            func,
                            interval,
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to insert_notification_automation_logs!"
                        )
        except Exception as e:
            self.LOG.error("insert_notification_automation_log: error={}".format(e))
            return None
        self.LOG.info("insert_notification_automation_log: entry={}".format(info))
        self.LOG.info("insert_notification_automation_log: END")
        return info  # no error

    # Select Notification Automation Query Links
    def get_notification_automation_query_links(self) -> list:
        try:
            self.LOG.info("get_notification_automation_query_links: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                info = sql.execute(self.select_notification_automation_query_links)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_notification_automation_query_links query!"
                    )
        except Exception as e:
            self.LOG.error(
                "get_notification_automation_query_links: error={}".format(e)
            )
            self.LOG.info("get_notification_automation_query_links: END")
            return []
        self.LOG.info("get_notification_automation_query_links: links={}".format(info))
        self.LOG.info("get_notification_automation_query_links: END")
        return info

    # Insert Notification Automation Query Link
    def create_notification_automation_query_link(
        self,
        queryID: int,
        variableName: str,
        verification: Verification,
        notificationAutomationId: str,
    ) -> str:
        try:
            self.LOG.info("insert_notification_automation_query_links: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_notification_automation_query_link,
                        (
                            queryID,
                            variableName,
                            verification.get_verification(),
                            notificationAutomationId,
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update_notification_automation_logs!"
                        )
        except Exception as e:
            self.LOG.error(
                "insert_notification_automation_query_link: error={}".format(e)
            )
            return None

        self.LOG.info(
            "insert_notification_automation_query_link: entry={}".format(info)
        )
        self.LOG.info("insert_notification_automation_query_link: END")
        return info  # no error

    # Update Notification Automation Query Link
    def update_notification_automation_query_link(
        self,
        id: str,
        variableName: str,
        verification: Verification,
    ) -> str:
        try:
            self.LOG.info("update_notification_automation_query_link: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_notification_automation_query_link_by_id,
                        (variableName, id),
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update_notification_automation_logs!"
                        )
        except Exception as e:
            self.LOG.error(
                "update_notification_automation_query_link: error={}".format(e)
            )
            self.LOG.info("update_notification_automation_query_link: END")
            return None
        self.LOG.info("update_notification_automation_query_link: info={}".format(info))
        self.LOG.info("update_notification_automation_query_link: END")
        return info

    # Update Notification Automation Query Link Status
    def update_notification_automation_query_link_statuses(
        self,
        ids: list,
        status: int,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_notification_automation_query_link_status: BEGIN")
            info = None
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    ids_string = ",".join(map(str, ids))
                    sql.execute(
                        self.update_notification_automation_query_link_status_by_ids,
                        (status, ids_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_notification_automation_logs!"
                        )
        except Exception as e:
            self.LOG.error(
                "update_notification_automation_query_link_status: error={}".format(e)
            )
            self.LOG.info("update_notification_automation_query_link_status: END")
            return None
        self.LOG.info(
            "update_notification_automation_query_link_status: info={}".format(info)
        )
        self.LOG.info("update_notification_automation_query_link_status: END")
        return info

    # Select Notification Automation Message Links
    def get_notification_automation_message_links(self) -> list:
        try:
            self.LOG.info("get_notification_automation_message_links: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_notification_automation_message_links)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No data found with the get_notification_automation_message_links query!"
                    )
        except Exception as e:
            self.LOG.error(
                "get_notification_automation_message_links: error={}".format(e)
            )
            self.LOG.info("get_notification_automation_message_links: END")
            return []
        self.LOG.info("get_notification_automation_message_links: info={}".format(info))
        self.LOG.info("get_notification_automation_message_links: END")
        return info

    # Insert Notification Automation Message Link
    def create_notification_automation_message_link(
        self,
        notificationAutomationId: int,
        notificationMessageId: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info("insert_notification_automation_message_link: BEGIN")
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_notification_automation_message_link,
                        (notificationAutomationId, notificationMessageId, verification),
                    )
                    if len(sql.table) != 0:
                        info = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No data found with the insert_notification_automation_message_link query!"
                        )
        except Exception as e:
            self.LOG.error(
                "insert_notification_automation_message_link: error={}".format(e)
            )
            self.LOG.info("insert_notification_automation_message_link: END")
            return -1
        self.LOG.info(
            "insert_notification_automation_message_link: info={}".format(info)
        )
        self.LOG.info("insert_notification_automation_message_link: END")
        return info

    # Update Notification Automation Message Link
    def update_notification_automation_message_link(
        self,
        id: int,
        notificationAutomationId: int,
        notificationMessageId: int,
        status: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info("update_notification_automation_message_link: BEGIN")
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_notification_automation_message_link_by_id,
                        (notificationAutomationId, notificationMessageId, status, id),
                    )
                    if len(sql.table) != 0:
                        info = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No data found with the update_notification_automation_message_link query!"
                        )
        except Exception as e:
            self.LOG.error(
                "update_notification_automation_message_link: error={}".format(e)
            )
            self.LOG.info("update_notification_automation_message_link: END")
            return -1
        self.LOG.info(
            "update_notification_automation_message_link: info={}".format(info)
        )
        self.LOG.info("update_notification_automation_message_link: END")
        return []

    # Select Notification Messages
    def get_notification_messages(self):
        try:
            self.LOG.info("get_notification_messages: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_notification_messages)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No data found with the get_notification_messages query!"
                    )
        except Exception as e:
            self.LOG.error("get_notification_messages: error={}".format(e))
            self.LOG.info("get_notification_messages: END")
            return []
        self.LOG.info("get_notification_messages: info={}".format(info))
        self.LOG.info("get_notification_messages: END")
        return info

    # Insert Notification Message
    def create_notification_message(
        self, message: str, notificationAutomationID: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info("insert_notification_message: BEGIN")

            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # create notification message
                    sql.execute(
                        self.insert_notification_message,
                        (
                            message,
                            verification.get_verification(),
                        ),
                    )
                    # if success
                    if len(sql.table) != 0:
                        # extract message id
                        info = sql.table[0]["ID"]

                        # create notification automation message link
                        sql.execute(
                            self.insert_notification_automation_message_link,
                            (
                                notificationAutomationID,
                                info,
                                verification.get_verification(),
                            ),
                        )
                        if len(sql.table) == 0:
                            raise Exception(
                                "Fail to create notification automation message link!"
                            )

                        # create notifications
                        # get all employee associate to the notification automation
                        employeeIDs = self.get_employeeIDs_by_automation_id(
                            notificationAutomationID
                        )
                        # if there is employee associate with the notification automation
                        if len(employeeIDs) > 0:
                            # create notifications for all associating employees
                            self.create_notifications(info, employeeIDs, verification)
                    else:
                        raise Exception(
                            "No data found with the insert_notification_message query!"
                        )
        except Exception as e:
            self.LOG.error("insert_notification_message: error={}".format(e))
            self.LOG.info("insert_notification_message: END")
            return -1
        self.LOG.info("insert_notification_message: info={}".format(info))
        self.LOG.info("insert_notification_message: END")
        return info

    # Update Notification Message
    def update_notification_message_status(
        self, ids: list, status: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info("update_notification_message: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    ids_string = ",".join(ids)
                    sql.execute(
                        self.update_notification_message_status_by_ids,
                        (status, ids_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No data found with the update_notification_message query!"
                        )
        except Exception as e:
            self.LOG.error("update_notification_message: error={}".format(e))
            self.LOG.info("update_notification_message: END")
            return []
        self.LOG.info("update_notification_message: info={}".format(info))
        self.LOG.info("update_notification_message: END")
        return info

    # Select Notifications
    def get_notifications(self):
        try:
            self.LOG.info("get_notifications: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.select_notifications)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No data found with the get_notifications query!")
        except Exception as e:
            self.LOG.error("get_notifications: error={}".format(e))
            self.LOG.info("get_notifications: END")
            return []
        self.LOG.info("get_notifications: info={}".format(info))
        self.LOG.info("get_notifications: END")
        return []

    def create_notifications(
        self,
        messageID: str,
        employeeIDs: list,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info(
                "insert_notifications: BEGIN messageID {}, employeeIDs {} verification {}".format(
                    messageID, employeeIDs, verification
                )
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    if len(employeeIDs) > 0:
                        employeeIDs_string = ",".join(map(str, employeeIDs))
                        sql.execute(
                            self.insert_notifications,
                            (
                                employeeIDs_string,
                                messageID,
                                verification.get_verification(),
                            ),
                        )
                        if len(sql.table) != 0:
                            info = sql.table
                        else:
                            raise Exception(
                                "No data found with the insert_notifications query!"
                            )
                    else:
                        raise Exception(
                            "No employeeIDs provided with the insert_notifications query!"
                        )
        except Exception as e:
            self.LOG.error("insert_notifications: error={}".format(e))
            self.LOG.info("insert_notifications: END")
            return []
        self.LOG.info("insert_notifications: info={}".format(info))
        self.LOG.info("insert_notifications: END")
        return info

    def update_notification(
        self,
        id: int,
        messageId: int,
        status: int,
        viewed: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info("update_notification: BEGIN")
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_notification_by_id,
                        (messageId, status, viewed, id),
                    )
                    if len(sql.table) != 0:
                        info = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No data found with the update_notification query!"
                        )
        except Exception as e:
            self.LOG.error("update_notification: error={}".format(e))
            self.LOG.info("update_notification: END")
            return -1
        self.LOG.info("update_notification: info={}".format(info))
        self.LOG.info("update_notification: END")

        return info

    # update status of all notifications by selected IDs
    def update_notification_status_by_ids(
        self,
        status: int,
        ids: list,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_notification_status_by_ids: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    ids_string = ",".join(ids)

                    sql.execute(
                        self.update_notification_status_by_notifications,
                        (
                            status,
                            ids_string,
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No data found with the update_notification_status_by_ids query!"
                        )
        except Exception as e:
            self.LOG.error("update_notification_status_by_ids: error={}".format(e))
            self.LOG.info("update_notification_status_by_ids: END")
            return []
        self.LOG.info("update_notification_status_by_ids: info={}".format(info))
        self.LOG.info("update_notification_status_by_ids: END")
        return info

    # update viewed of all notifications of selected employeeID
    def update_notification_viewed_by_employee_id(
        self,
        employeeID: int,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_notification_viewed_by_employee_id: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_all_notification_viewed_by_employee,
                        (employeeID,),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No data found with the update_notification_viewed_by_employee_id query!"
                        )
        except Exception as e:
            self.LOG.error(
                "update_notification_viewed_by_employee_id: error={}".format(e)
            )
            self.LOG.info("update_notification_viewed_by_employee_id: END")
            return []
        self.LOG.info("update_notification_viewed_by_employee_id: info={}".format(info))
        self.LOG.info("update_notification_viewed_by_employee_id: END")
        return info

    # update viewed of all selected ids
    def update_notification_viewed_by_notification_ids(
        self,
        ids: list,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_notification_viewed_by_notification_ids: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    ids_string = ",".join(map(str, ids))
                    sql.execute(
                        self.update_notification_viewed_by_ids,
                        (ids_string,),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No data found with the update_notification_viewed_by_notification_ids query!"
                        )
        except Exception as e:
            self.LOG.error(
                "update_notification_viewed_by_notification_ids: error={}".format(e)
            )
            self.LOG.info("update_notification_viewed_by_notification_ids: END")
            return []
        self.LOG.info(
            "update_notification_viewed_by_notification_ids: info={}".format(info)
        )
        self.LOG.info("update_notification_viewed_by_notification_ids: END")
        return info

    # Select Queries by Automation ID
    def get_queries_by_automation_id(self, notificationAutomationId: int) -> list:
        try:
            self.LOG.info("get_queries_by_automation_id: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.select_queries_by_automation_id, (notificationAutomationId,)
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No data found with the get_queries_by_automation_id query!"
                    )
        except Exception as e:
            self.LOG.error("get_queries_by_automation_id: error={}".format(e))
            return []

        self.LOG.info("get_queries_by_automation_id: info={}".format(info))
        self.LOG.info("get_queries_by_automation_id: END")
        return info

    # Select Employee IDs by Automation ID
    def get_employeeIDs_by_automation_id(self, notificationAutomationId: int) -> list:
        try:
            self.LOG.info("get_employeeIDs_by_automation_id: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.select_employee_ids_by_automation_id,
                    (notificationAutomationId, notificationAutomationId),
                )
                if len(sql.table) != 0:
                    info = [item["EmployeeID"] for item in sql.table]
                else:
                    raise Exception(
                        "No data found with the get_employeeIDs_by_automation_id query!"
                    )
        except Exception as e:
            self.LOG.error("get_employeeIDs_by_automation_id: error={}".format(e))
            return []

        self.LOG.info("get_employeeIDs_by_automation_id: info={}".format(info))
        self.LOG.info("get_employeeIDs_by_automation_id: END")
        return info

    # Select Notifications by Employee ID
    def get_notifications_by_employeeID(
        self, employeeID: int, offset: int, rows: int, viewed, UUIDs
    ) -> list:
        try:
            self.LOG.info("get_notifications_by_employeeID: BEGIN")
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                UUIDs_string = None if UUIDs is None else ",".join(map(str, UUIDs))
                # if provide offset and rows
                # return data using offset and rows
                if offset is not None and rows is not None:
                    sql.execute(
                        self.select_notifications_by_employee_id_pagination,
                        (offset, rows, viewed, employeeID, UUIDs_string),
                    )
                # if do not provide offset or rows
                # return all
                else:
                    sql.execute(
                        self.select_notifications_by_employee_id,
                        (None, None, viewed, employeeID, UUIDs_string),
                    )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No data found with the select_notifications_by_employee_id query!"
                    )
        except Exception as e:
            self.LOG.error("get_notifications_by_employeeID: error={}".format(e))
            return []

        self.LOG.info("get_notifications_by_employeeID: info={}".format(info))
        self.LOG.info("get_notifications_by_employeeID: END")
        return info


if __name__ == "__main__":
    main()
