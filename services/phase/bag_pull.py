#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .verification_pull import Verification
from .bag_config import BagConfig
from .gauge_pull import Gauge
from .sql_pull import SQL_Pull


class Bag(BagConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        BagConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # With provided info, logs the linking of a BagUDID and a AlignerID.
    # input: BagUDID, AlignerID
    # output: LinkID on success, "" on error
    def insert_aligner_bag(
        self, bagUDID: str, alignerID: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "insert_aligner_bag: bagUDID={} alignerID={} verification={}".format(
                    bagUDID, alignerID, verification
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_Bag_Link,
                        (bagUDID, alignerID, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        linkID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the insert_Bag_Link query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_aligner_bag: error={}".format(e))
            self.LOG.info("insert_aligner_bag: END")
            return -1  # other error

        self.LOG.info("insert_aligner_bag: linkID={}".format(linkID))
        self.LOG.info("insert_aligner_bag: END")
        return linkID  # no error

    # With provided information, creates a bag entry.
    # input: PatientName, DoctorName, LegibleStep, Steps, GTIN, LotNumber, SerialNumber, Barcode, MDate, EDate, Verification
    # output: BagUDID on success, "" on error
    def insert_bag_udid(
        self,
        patientName: str,
        doctorName: str,
        legibleStep: str,
        steps: str,
        gtin: str,
        lotNumber: str,
        serialNumber: str,
        barcode: str,
        mDate: str,
        eDate: str,
        verification: Verification,
        machineID: int = -1,
        stationID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                'insert_bag_udid: patientName="{}" doctorName="{}" legibleStep="{}" steps={} gtin={} lotNumber={} serialNumber={} verification="{}" stationID={}'.format(
                    patientName,
                    doctorName,
                    legibleStep,
                    steps,
                    gtin,
                    lotNumber,
                    serialNumber,
                    verification,
                    stationID,
                )
            )

            bagUDID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_Bag_UDID,
                        (
                            patientName,
                            doctorName,
                            legibleStep,
                            steps,
                            gtin,
                            lotNumber,
                            serialNumber,
                            barcode,
                            mDate,
                            eDate,
                            verification.get_verification(),
                            machineID,
                            stationID,
                        ),
                    )
                    if len(sql.table) != 0:
                        bagUDID = int(sql.table[0]["BagUDID"])
                    else:
                        raise Exception(
                            "No results found with the insert_Bag_UDID query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_bag_udid: error={}".format(e))
            self.LOG.info("insert_bag_udid: END")
            return -1  # other error

        self.LOG.info("insert_bag_udid: bagUDID={}".format(bagUDID))
        self.LOG.info("insert_bag_udid: END")
        return bagUDID  # no error

    # gets a particular bag from its bagUDID
    # input: BagUDID
    # output: BagUDID on success, [] on error
    def get_bag_by_udid(self, bagUDID: int) -> list:
        try:
            self.LOG.info("get_bag_by_udid: bagUDID={}".format(bagUDID))

            bags = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Bag_by_UDID, (bagUDID))
                if len(sql.table) != 0:
                    bags = sql.table
                else:
                    raise Exception("No results found with the get_Bag_by_UDID query!")

        except Exception as e:
            self.LOG.error("get_bag_by_udid: error={}".format(e))
            self.LOG.info("get_bag_by_udid: END")
            return []  # other error

        self.LOG.info("get_bag_by_udid: bags={}".format(bags))
        self.LOG.info("get_bag_by_udid: END")
        return bags  # no error

    # pulls an aligner's data from a particular bag
    # input: LinkID
    # output: Bags on success, [] on error
    def get_bags_by_link(self, linkID: int) -> list:
        try:
            self.LOG.info("get_bag_by_link: linkID={}".format(linkID))

            bags = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Bags_by_Link, (linkID))
                if len(sql.table) != 0:
                    bags = sql.table
                else:
                    raise Exception("No results found with the get_Bags_by_Link query!")

        except Exception as e:
            self.LOG.error("get_bag_by_link: error={}".format(e))
            self.LOG.info("get_bag_by_link: END")
            return []  # other error

        self.LOG.info("get_bag_by_link: bags={}".format(bags))
        self.LOG.info("get_bag_by_link: END")
        return bags  # no error

    # pulls an aligner's data from a particular bag link
    # input: AlignerID
    # output: Links on success, [] on error
    def get_bag_links_by_aligner(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_bag_links_by_aligner: alignerID={}".format(alignerID))

            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_BagLinks_by_aligner, (alignerID))
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_BagLinks_by_aligner query!"
                    )

        except Exception as e:
            self.LOG.error("get_bag_links_by_aligner: error={}".format(e))
            self.LOG.info("get_bag_links_by_aligner: END")
            return []  # other error

        self.LOG.info("get_bag_links_by_aligner: links={}".format(links))
        self.LOG.info("get_bag_links_by_aligner: END")
        return links  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
