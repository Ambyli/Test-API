#!/usr/bin/env python3.7

from os import link
from typing import Dict, List

from .verification_pull import Verification
from .gauge_pull import Gauge
from .record_config import RecordConfig
from .shade_regex import gen_steps
from .sql_pull import SQL_Pull
from .sql_config import SQLConfig
from .constants import Locations, Statuses


class Record(RecordConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        RecordConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # get laser record logs by case
    # input: caseNumber
    # output: All records on success, [] on error
    def get_laser_record_logs_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_laser_record_logs_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_laser_record_logs_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_laser_record_logs_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_laser_record_logs_by_caseNumber: error={}".format(e))
            self.LOG.info("get_laser_record_logs_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_laser_record_logs_by_caseNumber: records={}".format(info))
        self.LOG.info("get_laser_record_logs_by_caseNumber: END")
        return info  # no error

    # get all laser records
    # input: N/A
    # output: All records on success, [] on error
    def get_laser_records(self) -> list:
        try:
            self.LOG.info("get_laser_records: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_laser_records)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_laser_records query!"
                    )

        except Exception as e:
            self.LOG.error("get_laser_records: error={}".format(e))
            self.LOG.info("get_laser_records: END")
            return []  # other error

        self.LOG.info("get_laser_records: records={}".format(info))
        self.LOG.info("get_laser_records: END")
        return info  # no error

    # get laser records by case
    # input: caseNumber
    # output: All records on success, [] on error
    def get_laser_records_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_laser_records_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_laser_records_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_laser_records_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_laser_records_by_caseNumber: error={}".format(e))
            self.LOG.info("get_laser_records_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_laser_records_by_caseNumber: records={}".format(info))
        self.LOG.info("get_laser_records_by_caseNumber: END")
        return info  # no error

    # get laser records by id
    # input: caseNumber
    # output: All records on success, [] on error
    def get_laser_records_by_id(self, id: int) -> list:
        try:
            self.LOG.info("get_laser_records_by_id: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_laser_records_by_laser, (id,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_laser_records_by_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_laser_records_by_id: error={}".format(e))
            self.LOG.info("get_laser_records_by_id: END")
            return []  # other error

        self.LOG.info("get_laser_records_by_id: records={}".format(info))
        self.LOG.info("get_laser_records_by_id: END")
        return info  # no error

    # create laser record
    # input: LaserMark, Aligner, CaseNumber, Correct, CreatedBy
    # output: ID, -1 on error
    def create_new_laser_record(
        self,
        laserMark: str,
        aligner: int,
        caseNumber: int,
        correct: int,
        verification: Verification,
        bagUDID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_laser_record: laserMark={} aligner={} bagUDID={} caseNumber={} correct={} verification={}".format(
                    laserMark, aligner, bagUDID, caseNumber, correct, verification
                )
            )

            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add laser record
                    sql.execute(
                        self.create_laser_record,
                        (
                            laserMark,
                            aligner,
                            caseNumber,
                            correct,
                            verification.get_verification(),
                            bagUDID,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to create new laser record {}!".format(info)
                        )
            else:
                self.LOG.info("create_new_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("create_new_laser_record: error={}".format(e))
            self.LOG.info("create_new_laser_record: END")
            return -1  # other error

        self.LOG.info("create_new_laser_record: entry={}".format(info))
        self.LOG.info("create_new_laser_record: END")
        return info  # no error

    # update laser record
    # input: LaserMark1, LaserMark2, aligner, ID, EmployeeID
    # output: ID, -1 on error
    def edit_laser_record(
        self,
        laserMark: str,
        aligner: int,
        bagUDID: int,
        correct: int,
        id: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "edit_laser_record: laserMark={} aligner={} bagUDID={} correct={} id={} verification={}".format(
                    laserMark, aligner, bagUDID, correct, id, verification
                )
            )
            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # get old data
                    sql.execute(self.get_laser_records_by_laser, (id,))
                    laser_data = sql.table[0]
                    # compare to new data to create change value
                    change = []
                    if laser_data["LaserMark"] != laserMark:
                        change.append("LaserMark")
                    if laser_data["Aligner"] != aligner:
                        change.append("Aligner")
                    if laser_data["BagUDID"] != bagUDID:
                        change.append("BagUDID")
                    if laser_data["Correct"] != correct:
                        change.append("Correct")

                    # update laser record
                    sql.execute(
                        self.update_laser_record,
                        (
                            laserMark,
                            aligner,
                            bagUDID,
                            correct,
                            "Update " + ", ".join(change),
                            verification.get_verification(),
                            id,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update laser record {}!".format(info)
                        )
            else:
                self.LOG.info("edit_laser_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("edit_laser_record: error={}".format(e))
            self.LOG.info("edit_laser_record: END")
            return -1  # other error

        self.LOG.info("edit_laser_record: entry={}".format(info))
        self.LOG.info("edit_laser_record: END")
        return info  # no error

    # delete laser records by laserRecordID
    # input: laserRecordID, employeeID
    # output: deleted records on success, {} on error
    def delete_laser_record_by_laser_record_ID(
        self, laser_record_ID: int, verificaton: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_laser_records_by_laser_record: laser_record_ID={laser_record_ID} verificaton={verificaton}"
            )

            info = []
            # check employee ID
            if (
                isinstance(verificaton, Verification)
                and verificaton.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_laser_record_by_laser_record,
                        (verificaton.get_verification(), laser_record_ID),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_laser_record_by_laser_record query!"
                        )
            else:
                self.LOG.info(
                    "delete_laser_record_by_laser_record: Error: Invalid Verification!"
                )
                return []

        except Exception as e:
            self.LOG.error("delete_laser_records_by_laser_record: error={}".format(e))
            self.LOG.info("delete_laser_records_by_laser_record: END")
            return []  # other error

        self.LOG.info("delete_laser_records_by_laser_record: records={}".format(info))
        self.LOG.info("delete_laser_records_by_laser_record: END")
        return info  # no error

    # delete laser records by caseNumber
    # input: caseNumber, employeeID
    # output: deleted records on success, [] on error
    def delete_laser_records_by_caseNumber(
        self, caseNumber: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_laser_records_by_caseNumber: caseNumber={caseNumber} verification={verification}"
            )

            info = []
            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_laser_record_by_laser_case,
                        (verification.get_verification(), caseNumber),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_laser_record_by_case query!"
                        )
            else:
                self.LOG.info("delete_laser_record: Error: Invalid Verification")
                return []

        except Exception as e:
            self.LOG.error("delete_laser_records_by_caseNumber: error={}".format(e))
            self.LOG.info("delete_laser_records_by_caseNumber: END")
            return []  # other error

        self.LOG.info("delete_laser_records_by_caseNumber: records={}".format(info))
        self.LOG.info("delete_laser_records_by_caseNumber: END")
        return info  # no error

    # delete shipping records by caseNumber
    # input: caseNumber, employeeID
    # output: deleted records on success, [] on error
    def delete_shipping_records_by_caseNumber(
        self, caseNumber: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_shipping_records_by_caseNumber: caseNumber={caseNumber} verification={verification}"
            )

            info = {}
            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_shipping_record_by_case,
                        (verification.get_verification(), caseNumber),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_shipping_record_by_case query!"
                        )
            else:
                self.LOG.info(
                    "delete_shipping_records_by_caseNumber: Error: Invalid Employee"
                )
                return {}

        except Exception as e:
            self.LOG.error("delete_shipping_records_by_caseNumber: error={}".format(e))
            self.LOG.info("delete_shipping_records_by_caseNumber: END")
            return {}  # other error

        self.LOG.info("delete_shipping_records_by_caseNumber: records={}".format(info))
        self.LOG.info("delete_shipping_records_by_caseNumber: END")
        return info  # no error

    # delete shipping records by shipping
    # input: caseNumber, employeeID
    # output: deleted records on success, [] on error
    def delete_shipping_records_by_shipping_ID(
        self, recordID: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_shipping_records_by_shipping_ID: recordID={recordID} verification={verification}"
            )

            info = {}
            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_shipping_record_by_shipping,
                        (verification.get_verification(), recordID),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_shipping_records_by_shipping_ID query!"
                        )
            else:
                self.LOG.info(
                    "delete_shipping_records_by_shipping_ID: Error: Invalid Employee"
                )
                return {}

        except Exception as e:
            self.LOG.error("delete_shipping_records_by_shipping_ID: error={}".format(e))
            self.LOG.info("delete_shipping_records_by_shipping_ID: END")
            return {}  # other error

        self.LOG.info("delete_shipping_records_by_shipping_ID: records={}".format(info))
        self.LOG.info("delete_shipping_records_by_shipping_ID: END")
        return info  # no error

    # get shipping record logs by case
    # input: caseNumber
    # output: All records on success, [] on error
    def get_shipping_record_logs_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_shipping_record_logs_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_shipping_record_logs_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_shipping_record_logs_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_shipping_record_logs_by_caseNumber: error={}".format(e))
            self.LOG.info("get_shipping_record_logs_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_shipping_record_logs_by_caseNumber: records={}".format(info))
        self.LOG.info("get_shipping_record_logs_by_caseNumber: END")
        return info  # no error

    # get all shipping records
    # input: N/A
    # output: All records on success, [] on error
    def get_shipping_records(self) -> list:
        try:
            self.LOG.info("get_shipping_records: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_shipping_records)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_shipping_records query!"
                    )

        except Exception as e:
            self.LOG.error("get_shipping_records: error={}".format(e))
            self.LOG.info("get_shipping_records: END")
            return []  # other error

        self.LOG.info("get_shipping_records: records={}".format(info))
        self.LOG.info("get_shipping_records: END")
        return info  # no error

    # get shipping records by case
    # input: caseNumber
    # output: All records on success, [] on error
    def get_shipping_records_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_shipping_records_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_shipping_records_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_shipping_records_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_shipping_records_by_caseNumber: error={}".format(e))
            self.LOG.info("get_shipping_records_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_shipping_records_by_caseNumber: records={}".format(info))
        self.LOG.info("get_shipping_records_by_caseNumber: END")
        return info  # no error

    # get shipping records by id
    # input: caseNumber
    # output: All records on success, [] on error
    def get_shipping_records_by_id(self, id: int) -> list:
        try:
            self.LOG.info("get_shipping_records_by_id: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_shipping_records_by_shipping, (id,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_shipping_records_by_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_shipping_records_by_id: error={}".format(e))
            self.LOG.info("get_shipping_records_by_id: END")
            return []  # other error

        self.LOG.info("get_shipping_records_by_id: records={}".format(info))
        self.LOG.info("get_shipping_records_by_id: END")
        return info  # no error

    # get shipping records by tracking
    # input: tracking number
    # output: All records on success, [] on error
    def get_shipping_records_by_tracking(self, tracking: str) -> list:
        try:
            self.LOG.info("get_shipping_records_by_tracking: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_shipping_records_by_tracking_number, (tracking,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_shipping_records_by_tracking query!"
                    )

        except Exception as e:
            self.LOG.error("get_shipping_records_by_tracking: error={}".format(e))
            self.LOG.info("get_shipping_records_by_tracking: END")
            return []  # other error

        self.LOG.info("get_shipping_records_by_tracking: records={}".format(info))
        self.LOG.info("get_shipping_records_by_tracking: END")
        return info  # no error

    # create shipping record
    # input: Country, Tracking, CaseNumber, verification
    # output: ID, -1 on error
    def create_new_shipping_record(
        self,
        country: str,
        tracking: str,
        caseNumber: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_shipping_record: country={} tracking={} caseNumber={} verification={}".format(
                    country, tracking, caseNumber, verification
                )
            )
            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add shipping record
                    sql.execute(
                        self.create_shipping_record,
                        (
                            country,
                            tracking,
                            caseNumber,
                            verification.get_verification(),
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to create new shipping record {}!".format(info)
                        )
            else:
                self.LOG.info("create_new_shipping_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("create_new_shipping_record: error={}".format(e))
            self.LOG.info("create_new_shipping_record: END")
            return -1  # other error

        self.LOG.info("create_new_shipping_record: entry={}".format(info))
        self.LOG.info("create_new_shipping_record: END")
        return info  # no error

    # update shipping record
    # input: Country, Tracking, ID, EmployeeID
    # output: ID, -1 on error
    def edit_shipping_record(
        self,
        country: str,
        tracking: str,
        id: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "edit_shipping_record: country={} tracking={} id={} verification={}".format(
                    country, tracking, id, verification
                )
            )
            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # get old data
                    sql.execute(self.get_shipping_records_by_shipping, (id,))
                    if len(sql.table) == 0:
                        raise Exception(
                            "No results found with the get_shipping_records_by_shipping query!"
                        )
                    shipping_data = sql.table[0]
                    # compare to new data to create change value
                    change = []
                    if shipping_data["Country"] != country:
                        change.append("Country")
                    if shipping_data["Tracking"] != tracking:
                        change.append("Tracking")

                    # update shipping record
                    sql.execute(
                        self.update_shipping_record,
                        (
                            country,
                            tracking,
                            "Update " + ", ".join(change),
                            verification.get_verification(),
                            id,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update shipping record {}!".format(info)
                        )
            else:
                self.LOG.info("edit_shipping_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("edit_shipping_record: error={}".format(e))
            self.LOG.info("edit_shipping_record: END")
            return -1  # other error

        self.LOG.info("edit_shipping_record: entry={}".format(info))
        self.LOG.info("edit_shipping_record: END")
        return info  # no error

        # get bag record logs by case

    # input: caseNumber
    # output: All records on success, [] on error
    def get_bag_record_logs_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_bag_record_logs_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bag_record_logs_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_bag_record_logs_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_bag_record_logs_by_caseNumber: error={}".format(e))
            self.LOG.info("get_bag_record_logs_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_bag_record_logs_by_caseNumber: records={}".format(info))
        self.LOG.info("get_bag_record_logs_by_caseNumber: END")
        return info  # no error

    # get all bag records
    # input: N/A
    # output: All records on success, [] on error
    def get_bag_records(self) -> list:
        try:
            self.LOG.info("get_bag_records: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_bag_records)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No results found with the get_bag_records query!")

        except Exception as e:
            self.LOG.error("get_bag_records: error={}".format(e))
            self.LOG.info("get_bag_records: END")
            return []  # other error

        self.LOG.info("get_bag_records: records={}".format(info))
        self.LOG.info("get_bag_records: END")
        return info  # no error

    # get bag records by case
    # input: caseNumber
    # output: All records on success, [] on error
    def get_bag_records_by_caseNumber(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_bag_records_by_caseNumber: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bag_records_by_case, (caseNumber,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_bag_records_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_bag_records_by_caseNumber: error={}".format(e))
            self.LOG.info("get_bag_records_by_caseNumber: END")
            return []  # other error

        self.LOG.info("get_bag_records_by_caseNumber: records={}".format(info))
        self.LOG.info("get_bag_records_by_caseNumber: END")
        return info  # no error

    # get bag records by id
    # input: caseNumber
    # output: All records on success, [] on error
    def get_bag_records_by_id(self, id: int) -> list:
        try:
            self.LOG.info("get_bag_records_by_id: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bag_records_by_bag, (id,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_bag_records_by_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_bag_records_by_id: error={}".format(e))
            self.LOG.info("get_bag_records_by_id: END")
            return []  # other error

        self.LOG.info("get_bag_records_by_id: records={}".format(info))
        self.LOG.info("get_bag_records_by_id: END")
        return info  # no error

    # create bag record
    # input: BagUDID, Barcode, CaseID, CreatedBy
    # output: ID, -1 on error
    def create_new_bag_record(
        self,
        bagUDID: int,
        barcode: str,
        caseID: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "create_new_bag_record: bagUDID={} barcode={} caseID={} verification={}".format(
                    bagUDID, barcode, caseID, verification
                )
            )
            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add bag record
                    sql.execute(
                        self.create_bag_record,
                        (
                            bagUDID,
                            barcode,
                            verification.get_verification(),
                            caseID,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to create new bag record {}!".format(info)
                        )
            else:
                self.LOG.info("create_new_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("create_new_bag_record: error={}".format(e))
            self.LOG.info("create_new_bag_record: END")
            return -1  # other error

        self.LOG.info("create_new_bag_record: entry={}".format(info))
        self.LOG.info("create_new_bag_record: END")
        return info  # no error

    # update bag record
    # input: BagUDID1, BagUDID2, aligner, ID, EmployeeID
    # output: ID, -1 on error
    def edit_bag_record(
        self,
        bagUDID: int,
        barcode: str,
        caseID: str,
        id: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "edit_bag_record: bagUDID={} barcode={} caseID={} id={} verification={}".format(
                    bagUDID, barcode, caseID, id, verification
                )
            )
            info = -1

            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # get old data
                    sql.execute(self.get_bag_records_by_bag, (id,))
                    bag_data = sql.table[0]
                    # compare to new data to create change value
                    change = []
                    if bag_data["BagUDID"] != bagUDID:
                        change.append("BagUDID")
                    if bag_data["Barcode"] != barcode:
                        change.append("Barcode")
                    if bag_data["CaseID"] != caseID:
                        change.append("CaseID")

                    # update bag record
                    sql.execute(
                        self.update_bag_record,
                        (
                            bagUDID,
                            barcode,
                            caseID,
                            "Update " + ", ".join(change),
                            verification.get_verification(),
                            id,
                        ),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to update bag record {}!".format(info))
            else:
                self.LOG.info("edit_bag_record: Error: Invalid Employee")
                return -1
        except Exception as e:
            self.LOG.error("edit_bag_record: error={}".format(e))
            self.LOG.info("edit_bag_record: END")
            return -1  # other error

        self.LOG.info("edit_bag_record: entry={}".format(info))
        self.LOG.info("edit_bag_record: END")
        return info  # no error

    # delete bag records by bagRecordID
    # input: bagRecordID, employeeID
    # output: deleted records on success, {} on error
    def delete_bag_record_by_bag_record_ID(
        self, bag_record_ID: int, verificaton: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_bag_records_by_bag_record: bag_record_ID={bag_record_ID} verificaton={verificaton}"
            )

            info = []
            # check employee ID
            if (
                isinstance(verificaton, Verification)
                and verificaton.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_bag_record_by_bag_record,
                        (verificaton.get_verification(), bag_record_ID),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_bag_record_by_bag_record query!"
                        )
            else:
                self.LOG.info(
                    "delete_bag_record_by_bag_record: Error: Invalid Verification!"
                )
                return []

        except Exception as e:
            self.LOG.error("delete_bag_records_by_bag_record: error={}".format(e))
            self.LOG.info("delete_bag_records_by_bag_record: END")
            return []  # other error

        self.LOG.info("delete_bag_records_by_bag_record: records={}".format(info))
        self.LOG.info("delete_bag_records_by_bag_record: END")
        return info  # no error

    # delete bag records by caseNumber
    # input: caseNumber, employeeID
    # output: deleted records on success, [] on error
    def delete_bag_records_by_caseNumber(
        self, caseNumber: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"delete_bag_records_by_caseNumber: caseNumber={caseNumber} verification={verification}"
            )

            info = []
            # check employee ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_bag_record_by_case,
                        (verification.get_verification(), caseNumber),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "No results found with the delete_bag_record_by_case query!"
                        )
            else:
                self.LOG.info("delete_bag_record: Error: Invalid Verification")
                return []

        except Exception as e:
            self.LOG.error("delete_bag_records_by_caseNumber: error={}".format(e))
            self.LOG.info("delete_bag_records_by_caseNumber: END")
            return []  # other error

        self.LOG.info("delete_bag_records_by_caseNumber: records={}".format(info))
        self.LOG.info("delete_bag_records_by_caseNumber: END")
        return info  # no error

    # gets all waste records
    # input: N/A
    # output: All waste records on success, [] on error
    def get_waste_types(self) -> list:
        try:
            self.LOG.info("get_waste_types: BEGIN")

            wastes = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_waste_types)
                if len(sql.table) != 0:
                    wastes = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_waste_types query!"
                    )

        except Exception as e:
            self.LOG.error("get_waste_types: error={}".format(e))
            self.LOG.info("get_waste_types: END")
            return []  # other error

        self.LOG.info("get_waste_types: wastes={}".format(len(wastes)))
        self.LOG.info("get_waste_types: END")
        return wastes  # no error

    def create_waste_type(
        self,
        verification: Verification,
        name: str,
        unit_of_measurement: str,
    ) -> int:
        try:
            self.LOG.info(
                "create_waste_type: name={} unit_of_measurement={} verification={}".format(
                    name, unit_of_measurement, verification
                )
            )

            wasteTypeID = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.insert_waste_type,
                        (name, unit_of_measurement, verification.get_verification()),
                    )

                    if len(sql.table) != 0:
                        wasteTypeID = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "An error occurred with the insert_waste_record query!"
                        )
            else:
                self.LOG.info("create_waste_type: Error: Invalid Verification")
                return -1

        except Exception as e:
            self.LOG.error("create_waste_type: error={}".format(e))
            self.LOG.info("create_waste_type: END")
            return -1  # other error

        self.LOG.info("create_waste_type: typeID={}".format(wasteTypeID))
        self.LOG.info("create_waste_type: END")
        return wasteTypeID  # no error

    def update_waste_type(
        self,
        verification: Verification,
        wasteTypeID: int,
        name: str,
        unit_of_measurement: str,
    ) -> int:
        try:
            self.LOG.info(
                "update_waste_type: verification={} wasteTypeID={} name={} unit_of_measurement={}".format(
                    verification, wasteTypeID, name, unit_of_measurement
                )
            )

            result = []

            # update aligners status
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_waste_type_by_waste_type,
                        (
                            name,
                            unit_of_measurement,
                            wasteTypeID,
                        ),
                    )
                    if len(sql.table) != 0:
                        result = int(sql.table[0]["ID"])
                    else:
                        raise Exception("Unable to update waste type!")
            else:
                self.LOG.info("update_waste_type: Error: Invalid Verification")
                return -1

        except Exception as e:
            self.LOG.error("update_waste_type: error={}".format(e))
            return -1

        self.LOG.info("update_waste_type: END")
        return result

    # gets all waste records
    # input: N/A
    # output: All waste records on success, [] on error
    def get_waste_records(self, offset: int = 0, rows: int = 1000) -> list:
        try:
            self.LOG.info("get_waste_records: BEGIN")

            wastes = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_waste_records, (offset, rows))
                if len(sql.table) != 0:
                    wastes = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_waste_records query!"
                    )

        except Exception as e:
            self.LOG.error("get_waste_records: error={}".format(e))
            self.LOG.info("get_waste_records: END")
            return []  # other error

        self.LOG.info("get_waste_records: wastes={}".format(len(wastes)))
        self.LOG.info("get_waste_records: END")
        return wastes  # no error

    # get bag records by id
    # input: caseNumber
    # output: All records on success, [] on error
    def get_waste_record_by_id(self, wasteID: int) -> list:
        try:
            self.LOG.info("get_waste_record_by_id: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_waste_record_by_waste, (wasteID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_waste_record_by_waste query!"
                    )

        except Exception as e:
            self.LOG.error("get_waste_record_by_id: error={}".format(e))
            self.LOG.info("get_waste_record_by_id: END")
            return []  # other error

        self.LOG.info("get_waste_record_by_id: records={}".format(info))
        self.LOG.info("get_waste_record_by_id: END")
        return info  # no error

    def create_waste_record(
        self,
        verification: Verification,
        value: str,
        wasteTypeID: int,
        locationID: int = Locations.PRODUCTION.value,
    ) -> int:
        try:
            self.LOG.info(
                "create_waste_record: value={} wasteTypeID={} verification={} locationID={}".format(
                    value, wasteTypeID, verification, locationID
                )
            )

            wasteID = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # add vendor
                    sql.execute(
                        self.insert_waste_record,
                        (
                            value,
                            wasteTypeID,
                            verification.get_verification(),
                            locationID,
                        ),
                    )

                    if len(sql.table) != 0:
                        wasteID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "An error occurred with the insert_waste_record query!"
                        )
            else:
                self.LOG.info("create_waste_record: Error: Invalid Verification")
                return -1

        except Exception as e:
            self.LOG.error("create_waste_record: error={}".format(e))
            self.LOG.info("create_waste_record: END")
            return -1  # other error

        self.LOG.info("create_waste_record: record={}".format(wasteID))
        self.LOG.info("create_waste_record: END")
        return wasteID  # no error

    def update_waste_record(
        self,
        verification: Verification,
        wasteID: int,
        value: str,
        wasteTypeID: int,
        locationID: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_waste_record: verification={} wasteID={} value={} wasteTypeID={} locationID={}".format(
                    verification, wasteID, value, wasteTypeID, locationID
                )
            )

            result = []

            # update aligners status
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # get old data
                    sql.execute(self.get_waste_record_by_waste, (wasteID,))
                    waste_data = sql.table[0]
                    # compare to new data to create change value
                    change = []
                    if waste_data["Value"] != value:
                        change.append("Value")
                    if waste_data["WasteTypeID"] != wasteTypeID:
                        change.append("WasteTypeID")
                    if waste_data["LocationID"] != locationID:
                        change.append("LocationID")

                    sql.execute(
                        self.update_waste_record_by_waste_record,
                        (
                            value,
                            wasteTypeID,
                            locationID,
                            "Update " + ", ".join(change),
                            verification.get_verification(),
                            wasteID,
                        ),
                    )
                    if len(sql.table) != 0:
                        result = int(sql.table[0]["ID"])
                    else:
                        raise Exception("Unable to update waste record!")
            else:
                self.LOG.info("update_waste_record: Error: Invalid Verification")
                return -1

        except Exception as e:
            self.LOG.error("update_waste_record: error={}".format(e))
            return -1

        self.LOG.info("update_waste_record: END")
        return result

    # delete waste records by wasteID
    # input: wasteID, employeeID
    # output: deleted records on success, {} on error
    def delete_waste_record(self, wasteID: int, verificaton: Verification) -> int:
        try:
            self.LOG.info(
                f"delete_waste_record: wasteID={wasteID} verificaton={verificaton}"
            )

            info = -1

            # check employee ID
            if (
                isinstance(verificaton, Verification)
                and verificaton.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.delete_waste_record_by_waste_record,
                        (verificaton.get_verification(), wasteID),
                    )
                    if len(sql.table) != 0:
                        info = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the delete_waste_record query!"
                        )
            else:
                self.LOG.info("delete_waste_record: Error: Invalid Verification!")
                return -1

        except Exception as e:
            self.LOG.error("delete_waste_record: error={}".format(e))
            self.LOG.info("delete_waste_record: END")
            return -1  # other error

        self.LOG.info("delete_waste_record: records={}".format(info))
        self.LOG.info("delete_waste_record: END")
        return info  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
