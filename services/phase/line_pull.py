#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .verification_pull import Verification
from .line_config import LineConfig


class Line(LineConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        LineConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # gets all lines
    # input: N/A
    # output: All lines on success, [] on error
    def get_lines(self) -> list:
        try:
            self.LOG.info("get_all_lines: BEGIN")

            lines = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_lines)
                if len(sql.table) != 0:
                    lines = sql.table
                else:
                    raise Exception("No results found with the get_all_lines query!")

        except Exception as e:
            self.LOG.error("get_all_lines: error={}".format(e))
            self.LOG.info("get_all_lines: END")
            return []  # other error

        self.LOG.info("get_all_lines: lines={}".format(lines))
        self.LOG.info("get_all_lines: END")
        return lines  # no error

    # gets line by lineID
    # input: lineID
    # output: line on success, {} on error
    def get_line_by_ID(self, lineID: int) -> dict:
        try:
            self.LOG.info("get_line_by_ID: BEGIN")

            line = None
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_line_by_line_id, (lineID,))
                if len(sql.table) != 0:
                    line = sql.table[0]
                else:
                    raise Exception("No results found with the get_line_by_ID query!")

        except Exception as e:
            self.LOG.error("get_line_by_ID: error={}".format(e))
            self.LOG.info("get_line_by_ID: END")
            return {}  # other error

        self.LOG.info("get_line_by_ID: lines={}".format(line))
        self.LOG.info("get_line_by_ID: END")
        return line  # no error

    # gets lines by ownerID
    # input: ownerID
    # output: lines on success, {} on error
    def get_line_by_owner(self, ownerID: int) -> list:
        try:
            self.LOG.info("get_line_by_owner: BEGIN")

            line = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lines_by_owner_id, (ownerID,))
                if len(sql.table) != 0:
                    line = sql.table
                else:
                    raise Exception(
                        "No results found with the get_line_by_owner query!"
                    )

        except Exception as e:
            self.LOG.error("get_line_by_owner: error={}".format(e))
            self.LOG.info("get_line_by_owner: END")
            return []  # other error

        self.LOG.info("get_line_by_owner: lines={}".format(line))
        self.LOG.info("get_line_by_owner: END")
        return line  # no error

    def create_line(
        self, name: str, description: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "create_line: name={} description={}".format(name, description)
            )
            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add line
                    sql.execute(self.insert_line, (name, description))

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to create new line for line!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("create_line: error={}".format(e))
            self.LOG.info("create_line: END")
            return -1  # other error

        self.LOG.info("create_line: entry={}".format(info))
        self.LOG.info("create_line: END")
        return info  # no error

    def update_line_info(
        self,
        name: str,
        description: str,
        lineID: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "update_line_info: name={} description={} lineID={}".format(
                    name, description, lineID
                )
            )
            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add line
                    sql.execute(self.update_line, (name, description, lineID))

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to update line for line!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("update_line_info: error={}".format(e))
            self.LOG.info("update_line_info: END")
            return -1  # other error

        self.LOG.info("update_line_info: entry={}".format(info))
        self.LOG.info("update_line_info: END")
        return info  # no error

    def update_line_status_info(
        self, status: int, lineID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "update_line_status: status={} lineID={}".format(lineID, lineID)
            )
            info = -1
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add line
                    sql.execute(self.update_line_status, (status, lineID))

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to update line for line!")
            else:
                raise Exception("Invalid employee ID!")
        except Exception as e:
            self.LOG.error("update_line_status: error={}".format(e))
            self.LOG.info("update_line_status: END")
            return -1  # other error

        self.LOG.info("update_line_status: entry={}".format(info))
        self.LOG.info("update_line_status: END")
        return info  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
