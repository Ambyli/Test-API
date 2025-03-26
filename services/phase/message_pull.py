#!/usr/bin/env python3.7
import logging
import os
import concurrent.futures
import requests
from os import link
from typing import Dict, List

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .verification_pull import Verification
from .message_config import MessageConfig


class Message(MessageConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        MessageConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Get case messages by case number
    def get_case_messages_by_case(self, case_number: str) -> list:
        try:
            self.LOG.info("get_case_messages_by_case_number: BEGIN")
            case_messages = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_case_messages_by_case_number, (str(case_number),))
                if len(sql.table) != 0:
                    case_messages = sql.table
                else:
                    raise Exception(f"No results found for case number {case_number}!")

        except Exception as e:
            self.LOG.error("get_case_messages_by_case_number: error={}".format(e))
            self.LOG.info("get_case_messages_by_case_number: END")
            return []  # other error

        self.LOG.info(
            "get_case_messages_by_case_number: case_messages={}".format(case_messages)
        )
        self.LOG.info("get_case_messages_by_case_number: END")
        return case_messages  # no error

    # Get case messages by case id
    def get_case_messages_by_caseID(self, case_id: str) -> list:
        try:
            self.LOG.info("get_case_messages_by_caseID: BEGIN")
            case_messages = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_case_messages_by_case_id, (str(case_id),))
                if len(sql.table) != 0:
                    case_messages = sql.table
                else:
                    raise Exception(f"No results found for case number {case_id}!")

        except Exception as e:
            self.LOG.error("get_case_messages_by_caseID: error={}".format(e))
            self.LOG.info("get_case_messages_by_caseID: END")
            return []  # other error

        self.LOG.info(
            "get_case_messages_by_caseID: case_messages={}".format(case_messages)
        )
        self.LOG.info("get_case_messages_by_caseID: END")
        return case_messages  # no error

    # Create case message
    def create_case_message(
        self, case_number: str, case_id: str, status: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_case_message: BEGIN case_number={}".format(case_number)
            )
            result = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # Add case message
                    sql.execute(
                        self.create_case_messages,
                        (case_number, case_id, status),
                    )
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            f"Failed to create case message for {case_number}!"
                        )
            else:
                raise Exception("Invalid verification ID!")

        except Exception as e:
            self.LOG.error("create_case_message: error={}".format(e))
            self.LOG.info("create_case_message: END")
            return []  # other error

        self.LOG.info("create_case_message: result={}".format(result))
        self.LOG.info("create_case_message: END")
        return result  # no error

    # Update case message status
    def update_case_message_status(
        self, status: int, case_message_id: str, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_case_message_status: status={} case_message_id={}".format(
                    status, case_message_id
                )
            )
            result = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_case_messages_status, (status, case_message_id)
                    )
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            f"Unable to update status for message ID {case_message_id}!"
                        )
            else:
                raise Exception("Invalid verification ID!")
        except Exception as e:
            self.LOG.error("update_case_message_status: error={}".format(e))
            self.LOG.info("update_case_message_status: END")
            return []  # other error

        self.LOG.info("update_case_message_status: result={}".format(result))
        self.LOG.info("update_case_message_status: END")
        return result  # no error

    # Get messages by case message ID
    def get_messages_by_case_message(self, case_message_id: str) -> list:
        try:
            self.LOG.info("get_messages_by_case_message_id: BEGIN")
            messages = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_messages_by_case_message_id, (case_message_id,))
                if len(sql.table) != 0:
                    messages = sql.table
                else:
                    raise Exception(
                        f"No messages found for case message ID {case_message_id}!"
                    )

        except Exception as e:
            self.LOG.error("get_messages_by_case_message_id: error={}".format(e))
            self.LOG.info("get_messages_by_case_message_id: END")
            return []  # other error

        self.LOG.info("get_messages_by_case_message_id: messages={}".format(messages))
        self.LOG.info("get_messages_by_case_message_id: END")
        return messages  # no error

    # Get messages filter
    def case_messages_filter(
        self,
        caseNumbers: list,
        statuses: list,
        isASC: bool,
        offset: int,
        rowPerPage: int,
        createdFrom: str,
        createdTo: str,
    ) -> list:
        try:
            self.LOG.info(
                "case_messages_filter: BEGIN caseNumbers={} statuses={}".format(
                    caseNumbers, statuses
                )
            )
            caseMessages = []
            with SQL_Pull()(self.sql_config)() as sql:
                caseNumbers_string = (
                    ",".join(map(str, caseNumbers)) if caseNumbers else None
                )
                statuses_string = ",".join(map(str, statuses)) if statuses else None
                isASC_value = 1 if isASC else 0
                sql.execute(
                    self.filter_messages,
                    (
                        caseNumbers_string,
                        statuses_string,
                        isASC_value,
                        offset,
                        rowPerPage,
                        createdFrom,
                        createdTo,
                    ),
                )
                if len(sql.table) != 0:
                    caseMessages = sql.table
                else:
                    raise Exception(f"No case messages found!")

        except Exception as e:
            self.LOG.error("case_messages_filter: error={}".format(e))
            self.LOG.info("case_messages_filter: END")
            return []  # other error

        self.LOG.info("case_messages_filter: messages={}".format(caseMessages))
        self.LOG.info("case_messages_filter: END")
        return caseMessages  # no error

    # Create message
    def create_message(
        self,
        message: str,
        case_message_id: str,
        verification: Verification,
    ) -> dict:
        try:
            self.LOG.info(
                "create_message: BEGIN message={} verification_id={} case_message_id={}".format(
                    message, verification.get_verification(), case_message_id
                )
            )
            result = []
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # Create message and link to case
                    sql.execute(
                        self.insert_message,
                        (message, verification.get_verification(), case_message_id),
                    )
                    if len(sql.table) != 0:
                        result = sql.table[0]
                    else:
                        raise Exception(
                            f"Failed to create message for case message ID {case_message_id}!"
                        )
            else:
                raise Exception("Invalid verification ID!")

        except Exception as e:
            self.LOG.error("create_message: error={}".format(e))
            self.LOG.info("create_message: END")
            return []  # other error

        self.LOG.info("create_message: result={}".format(result))
        self.LOG.info("create_message: END")
        return result  # no error

    # Update message status
    def update_message_status(
        self, status: int, message_id: str, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_message_status: status={} message_id={}".format(
                    status, message_id
                )
            )
            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_message_status, (status, message_id))
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            f"Unable to update status for message ID {message_id}!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_message_status: error={}".format(e))
            self.LOG.info("update_message_status: END")
            return []  # other error

        self.LOG.info("update_message_status: result={}".format(result))
        self.LOG.info("update_message_status: END")
        return result  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
