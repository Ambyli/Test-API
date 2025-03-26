#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .shade_regex import gen_steps
from .sql_pull import SQL_Pull
from .customer_config import CustomerConfig
from .gauge_pull import Gauge
from .verification_pull import Verification
import json
import requests
import os


class Customer(CustomerConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        CustomerConfig.__init__(self, sql_config)

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

    # gets all basic case info associated with a given case
    # input: N/A
    # output: Customers on success, [] on error
    def get_active_customers(self) -> list:
        try:
            self.LOG.info("get_active_customers: BEGIN")

            customers = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_customers)
                if len(sql.table) != 0:
                    customers = sql.table
                else:
                    raise Exception("No results found with the get_customers query!")

        except Exception as e:
            self.LOG.error("get_active_customers: error={}".format(e))
            self.LOG.info("get_active_customers: END")
            return []  # other error

        self.LOG.info("get_active_customers: customers={}".format(len(customers)))
        self.LOG.info("get_active_customers: END")
        return customers  # no error

    def get_customer_by_id(self, customerID: str) -> list:
        try:
            self.LOG.info("get_customer_by_id: customerID={}".format(customerID))

            customers = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_customer_by_ID, (customerID))
                if len(sql.table) != 0:
                    customers = sql.table
                else:
                    raise Exception(
                        "No results found with the get_customer_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_customer_by_id: error={}".format(e))
            self.LOG.info("get_customer_by_id: END")
            return []  # other error

        self.LOG.info("get_customer_by_id: customers={}".format(customers))
        self.LOG.info("get_customer_by_id: END")
        return customers  # no error

    def get_customer_account(self, customerID: str) -> list:
        try:
            self.LOG.info("get_customer_account: customerID={}".format(customerID))

            customers = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_customer_account_by_ID, (customerID))
                if len(sql.table) != 0:
                    customers = sql.table
                else:
                    raise Exception(
                        "No results found with the get_customer_account_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_customer_account: error={}".format(e))
            self.LOG.info("get_customer_account: END")
            return []  # other error

        self.LOG.info("get_customer_account: customers={}".format(customers))
        self.LOG.info("get_customer_account: END")
        return customers  # no error

    def create_customer_account(self, customerID: str, accountID: str) -> list:
        try:
            customeraccount = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.insert_customeraccount, (customerID, accountID))
                if len(sql.table) != 0:
                    customeraccount = sql.table
                else:
                    raise Exception(
                        "No results found with the create_customer_account query!"
                    )

        except Exception as e:
            self.LOG.error("create_customer_account: error={}".format(e))
            self.LOG.info("create_customer_account: END")
            return []

        self.LOG.info("create_customer_account: customer={}".format(customeraccount))
        self.LOG.info("create_customer_account: END")
        return customeraccount

    def get_customer_catalog(self, customerID: str) -> list:
        try:
            self.LOG.info("get_customer_catalog: customerID={}".format(customerID))

            customers = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_customer_catalog_by_ID, (customerID))
                if len(sql.table) != 0:
                    customers = sql.table
                else:
                    raise Exception(
                        "No results found with the get_customer_catalog_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_customer_catalog: error={}".format(e))
            self.LOG.info("get_customer_catalog: END")
            return []  # other error

        self.LOG.info("get_customer_catalog: customers={}".format(customers))
        self.LOG.info("get_customer_catalog: END")
        return customers  # no error

    def create_customer(
        self,
        verification: Verification,
        customerID: str,
        firstName: str,
        lastName: str,
        prefix: str,
        dear: str,
        practiceName: str,
        address1: str,
        address2: str,
        city: str,
        state: str,
        zipCode: str,
        county: str,
        country: str,
        officePhone: str,
        email: str,
        createdBy: str,
    ) -> dict:
        try:

            self.LOG.info(
                f"create_customer: customerID={customerID} firstName={firstName} lastName={lastName} prefix={prefix}"
            )
            # Default info returned
            info = {
                "message": "Customer Failed to be added",
                "status": 500,
            }

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                values = {
                    "labID": "Phase",
                    "customerID": customerID,
                    "firstName": firstName,
                    "lastName": lastName,
                    "prefix": prefix,
                    "dear": dear,
                    "practiceName": practiceName,
                    "address1": address1,
                    "address2": address2,
                    "city": city,
                    "state": state,
                    "zipCode": zipCode,
                    "county": county,
                    "country": country,
                    "officePhone": officePhone,
                    "email": email,
                    "createdBy": createdBy,
                }
                headers = {
                    "Content-type": "application/json",
                    "Accept": "application/json",
                }

                session = requests.Session()

                response = session.post(
                    os.getenv("MAGIC_TOUCH_URL")
                    + "/LabCustomer/AddCustomer/token={}".format(
                        os.getenv("MAGIC_TOUCH_TOKEN")
                    ),
                    data=json.dumps(values),
                    headers=headers,
                )
                if response.status_code != 200:
                    raise Exception("Failure to enter customer info into {database}!")

                info = response.json()

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_customer: error={}".format(e))
            self.LOG.info("create_customer: END")
            return info

        self.LOG.info("create_customer: customer={}".format(info))
        self.LOG.info("create_customer: END")
        return info


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
