#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .verification_config import VerificationConfig


class Verification(VerificationConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        VerificationConfig.__init__(self, sql_config)

        # globals
        self._employees = {}
        self._verificationID = -1

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def add_employee(
        self,
        employeeID: str,
        restrict: bool = False,
        bypass_check: bool = False,
    ) -> bool:
        try:
            self.LOG.info(
                "add_employee: employeeID={} restrict={}".format(
                    str(employeeID).lower(), restrict
                )
            )

            result = False

            # check employee info
            # bypass check toggle
            if bypass_check is False:
                employeeID = self.emp.employee_check(str(employeeID).lower(), restrict)
            # Disabled while employeeIDs are returned as string
            # if isinstance(employeeID, int):
            if len(employeeID) > 0:
                # reset batchID as we are getting a new employee
                self._verificationID = -1

                # append employee's info to list
                self._employees[employeeID] = {
                    "restrict": restrict,
                }

                # result update
                result = True

        except Exception as e:
            self.LOG.error("add_employee: error={}".format(e))
            self.LOG.info("add_employee: END")
            return False

        self.LOG.info("add_employee: result={}".format(result))
        self.LOG.info("add_employee: END")
        return result

    def remove_employee(self, employeeID: str) -> bool:
        try:
            self.LOG.info("remove_employee: employeeID={}".format(employeeID))

            result = False

            if employeeID in self._employees.keys():
                # remove employee info
                del self._employees[employeeID]

                # reset batch
                self._verificationID = -1

                # update result
                result = True

        except Exception as e:
            self.LOG.error("remove_employee: error={}".format(e))
            self.LOG.info("remove_employee: END")
            return False

        self.LOG.info("remove_employee: result={}".format(result))
        self.LOG.info("remove_employee: END")
        return result

    def verify_employees(self) -> int:
        try:
            self.LOG.info("verify_employees: employeeIDs={}".format(self._employees))

            verificationID = -1

            # check if we have a verificationID without employees listed
            if self._verificationID != -1 and len(self._employees) == 0:
                self.import_verification_by_id(self._verificationID)

            # for each employee check if they are valid
            for employeeID in self._employees.keys():
                result = self.emp.employee_check(
                    employeeID,
                    self._employees[employeeID]["restrict"],
                )

                # if employee info is not valid anymore
                if len(result) == 0:
                    # remove employee
                    self.remove_employee(employeeID)

            # create new verification
            if len(self._employees) > 0:
                verificationID = self.create_verification()

        except Exception as e:
            self.LOG.error("verify_employees: error={}".format(e))
            self.LOG.info("verify_employees: END")
            return -1

        self.LOG.info("verify_employees: verificationID={}".format(verificationID))
        self.LOG.info("verify_employees: END")
        return verificationID

    # Creates a employee batch and links it to all employees in the provided list
    def create_verification(self) -> int:
        try:
            self.LOG.info("create_verification: employeeIDs={}".format(self._employees))

            verificationID = -1

            # check if we have a verificationID without employees listed
            if self._verificationID != -1 and len(self._employees) == 0:
                self.import_verification_by_id(self._verificationID)

            if len(self._employees) > 0:
                with SQL_Pull()(self.sql_config)() as sql:
                    # create verificationID
                    sql.execute(self.insert_verification_batch)
                    if len(sql.table) == 0:
                        raise Exception(
                            "No results found with the insert_verification_batch query!"
                        )

                    # set ID
                    verificationID = sql.table[0]["ID"]

                    # link employees in class with verificationID
                    for employeeID in self._employees.keys():
                        result = sql.execute(
                            self.link_employee_verification_batch,
                            (verificationID, employeeID),
                        )
                        if len(result) == 0:
                            raise Exception(
                                "No results found with the link_employee_verification_batch query!"
                            )

                    # set global verificationID
                    self._verificationID = verificationID
            else:
                raise Exception("Verification failed, invalid employee count!")

        except Exception as e:
            self.LOG.error("create_verification: error={}".format(e))
            self.LOG.info("create_verification: END")
            return -1

        self.LOG.info("create_verification: verificationID={}".format(verificationID))
        self.LOG.info("create_verification: END")
        return verificationID

    def get_verification_info(self) -> list:
        try:
            self.LOG.info(
                "get_verification_info: verificationID={}".format(self._verificationID)
            )

            result = []

            with SQL_Pull()(self.sql_config)() as sql:
                # create verificationID
                sql.execute(self.get_verification_batch_by_id, (self._verificationID))
                if len(sql.table) != 0:
                    result = sql.table
                else:
                    raise Exception(
                        "No results found with the insert_verification_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_verification_info: error={}".format(e))
            self.LOG.info("get_verification_info: END")
            return []

        self.LOG.info("get_verification_info: result={}".format(result))
        self.LOG.info("get_verification_info: END")
        return result

    def import_verification_by_id(self, verificationID, bypass_check=False) -> int:
        try:
            self.LOG.info(
                "import_verification_by_id: verificationID={}".format(verificationID)
            )

            result = -1

            # confirm verificationID is real
            verification_info = self.get_verification_info_by_id(verificationID)
            if len(verification_info) > 0:
                verification_links = []
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_employees_by_verification_id, (verificationID))
                    if len(sql.table) != 0:
                        verification_links = sql.table
                    else:
                        raise Exception(
                            "The given verificationID {} fails to have any valid employee links!".format(
                                verificationID
                            )
                        )

                    # add employees from verification links and then reverify them
                    for verification_link in verification_links:
                        self.add_employee(
                            verification_link["EmployeeID"], bypass_check=bypass_check
                        )

                    # set verificationID
                    self._verificationID = verificationID

                    # set return result as a success
                    result = 0

            else:
                raise Exception(
                    "The given verificationID {} is not a valid verification!".format(
                        verificationID
                    )
                )

        except Exception as e:
            self.LOG.error("import_verification_by_id: error={}".format(e))
            self.LOG.info("import_verification_by_id: END")
            return -1

        self.LOG.info("import_verification_by_id: result={}".format(result))
        self.LOG.info("import_verification_by_id: END")
        return result

    def get_verification_info_by_id(self, verificationID) -> list:
        try:
            self.LOG.info(
                "get_verification_info_by_id: verificationID={}".format(verificationID)
            )

            result = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get batch info from SQL
                sql.execute(self.get_verification_batch_by_id, (verificationID))
                if len(sql.table) != 0:
                    result = sql.table
                else:
                    raise Exception(
                        "No results found with the insert_verification_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_verification_info_by_id: error={}".format(e))
            self.LOG.info("get_verification_info_by_id: END")
            return []

        self.LOG.info("get_verification_info_by_id: result={}".format(result))
        self.LOG.info("get_verification_info_by_id: END")
        return result

    def get_employees(self) -> dict:
        try:
            self.LOG.info("get_employees: BEGIN")

            result = self._employees

        except Exception as e:
            self.LOG.error("get_employees: error={}".format(e))
            self.LOG.info("get_employees: END")
            return {}

        self.LOG.info("get_employees: result={}".format(result))
        self.LOG.info("get_employees: END")
        return result

    def get_verification(self) -> int:
        try:
            self.LOG.info("get_verification: BEGIN")

            result = self._verificationID

        except Exception as e:
            self.LOG.error("get_verification: error={}".format(e))
            self.LOG.info("get_verification: END")
            return -1

        self.LOG.info("get_verification: result={}".format(result))
        self.LOG.info("get_verification: END")
        return result

    def set_verification(self, verificationID: int) -> int:
        try:
            self.LOG.info("set_verification: verificationID={}".format(verificationID))

            self._verificationID = verificationID

        except Exception as e:
            self.LOG.error("set_verification: error={}".format(e))
            self.LOG.info("set_verification: END")
            return {}

        self.LOG.info("set_verification: result={}".format(verificationID))
        self.LOG.info("set_verification: END")
        return verificationID


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
