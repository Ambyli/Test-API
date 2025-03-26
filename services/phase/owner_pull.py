#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .verification_pull import Verification
from .owners_config import OwnerConfig


class Owner(OwnerConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        OwnerConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # gets all owners
    # input: N/A
    # output: All owners on success, [] on error
    def get_owners(self) -> list:
        try:
            self.LOG.info("get_all_owners: BEGIN")

            owners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_owners)
                if len(sql.table) != 0:
                    owners = sql.table
                else:
                    raise Exception("No results found with the get_all_owners query!")

        except Exception as e:
            self.LOG.error("get_all_owners: error={}".format(e))
            self.LOG.info("get_all_owners: END")
            return []  # other error

        self.LOG.info("get_all_owners: owners={}".format(owners))
        self.LOG.info("get_all_owners: END")
        return owners  # no error

    def get_owner_employee_links_by_owner(self, ownerID: int) -> list:
        try:
            self.LOG.info(
                "get_owner_employee_links_by_owner: ownerID={} ".format(ownerID)
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_owner_employee_links_by_owner_id, (ownerID,))

                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("Unable to get_owner_employee_links_by_owner!")
        except Exception as e:
            self.LOG.error("get_owner_employee_links_by_owner: error={}".format(e))
            self.LOG.info("get_owner_employee_links_by_owner: END")
            return []  # other error

        self.LOG.info("get_owner_employee_links_by_owner: entry={}".format(info))
        self.LOG.info("get_owner_employee_links_by_owner: END")
        return info

    def update_owner_status(
        self, status: int, id: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info("update_owner_status: status={} id={}".format(status, id))
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # update status
                    sql.execute(
                        self.update_owner_status_by_id,
                        (status, id),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception("Unable to update_owner_status!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("update_owner_status: error={}".format(e))
            self.LOG.info("update_owner_status: END")
            return []  # other error

        self.LOG.info("update_owner_status: entry={}".format(info))
        self.LOG.info("update_owner_status: END")
        return info  # no error

    def create_owner_employee_links(
        self, ownerID: int, assigneeIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_owner_employee_links: ownerID={} assigneeIDs={}".format(
                    assigneeIDs, assigneeIDs
                )
            )
            info = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    employeeIDs_string = ",".join(map(str, employeeIDs))
                    # add link
                    sql.execute(
                        self.insert_owner_employee_links,
                        (ownerID, assigneeIDs_string),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception("Unable to create_owner_employee_links!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("create_owner_employee_links: error={}".format(e))
            self.LOG.info("create_owner_employee_links: END")
            return []  # other error

        self.LOG.info("create_owner_employee_links: entry={}".format(info))
        self.LOG.info("create_owner_employee_links: END")
        return info  # no error

    def update_owner_employee_link_statuses(
        self, status: int, linkIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_owner_employee_link_statuses: status={} linkIDs={}".format(
                    status, linkIDs
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
                        self.update_owner_employee_links_statuses,
                        (status, linkIDs_string),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update_owner_employee_link_statuses!"
                        )
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("update_owner_employee_link_statuses: error={}".format(e))
            self.LOG.info("update_owner_employee_link_statuses: END")
            return []  # other error

        self.LOG.info("update_owner_employee_link_statuses: entry={}".format(info))
        self.LOG.info("update_owner_employee_link_statuses: END")
        return info  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
