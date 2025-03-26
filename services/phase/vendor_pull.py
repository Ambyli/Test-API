#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .shade_regex import gen_steps
from .vendor_config import VendorConfig
from .gauge_pull import Gauge
from .sql_pull import SQL_Pull


class Vendor(VendorConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        VendorConfig.__init__(self, sql_config)

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

    # gets all vendors
    # input: N/A
    # output: All vendors on success, [] on error
    def get_vendors(self) -> list:
        try:
            self.LOG.info("get_all_vendors: BEGIN")

            vendors = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_vendors)
                if len(sql.table) != 0:
                    vendors = sql.table
                else:
                    raise Exception("No results found with the get_all_vendors query!")

        except Exception as e:
            self.LOG.error("get_all_vendors: error={}".format(e))
            self.LOG.info("get_all_vendors: END")
            return []  # other error

        self.LOG.info("get_all_vendors: vendors={}".format(vendors))
        self.LOG.info("get_all_vendors: END")
        return vendors  # no error

    def create_vendor(self, vendorID: str, vendor: str, address: str) -> str:
        try:
            self.LOG.info(
                "create_vendor: vendorID={} vendor={}".format(vendorID, vendor)
            )
            info = ""

            with SQL_Pull()(self.sql_config)() as sql:
                # add vendor
                sql.execute(self.insert_vendor, (vendorID, vendor, address))

                if len(sql.table) != 0:
                    info = str(sql.table[0]["VendorID"])
                else:
                    raise Exception(
                        "Unable to create new vendor for vendor {}!".format(vendor)
                    )
        except Exception as e:
            self.LOG.error("create_vendor: error={}".format(e))
            self.LOG.info("create_vendor: END")
            return ""  # other error

        self.LOG.info("create_vendor: entry={}".format(vendor))
        self.LOG.info("create_vendor: END")
        return info  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
