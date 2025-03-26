#!/usr/bin/env python3.7

from os import link

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .employee_pull import Employee
from .gauge_config import GaugeConfig
from .lock_pull import Lock
from .verification_pull import Verification


class Gauge(GaugeConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        GaugeConfig.__init__(self, sql_config)

        # Create an employee object
        self.emp = Employee()

        # initialize lock
        self.lock = Lock()

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def get_gauge(self, gaugeID: int) -> list:
        try:
            self.LOG.info("get_gauge: gaugeID={}".format(gaugeID))

            gauge = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_gauge_by_ID, (gaugeID,))
                if len(sql.table) != 0:
                    gauge = sql.table
                else:
                    raise Exception("No results found with the get_gauge_by_ID query!")

        except Exception as e:
            self.LOG.error("get_gauge: error={}".format(e))
            self.LOG.info("get_gauge: END")
            return []  # other error

        self.LOG.info("get_gauge: gauge={}".format(gauge))
        self.LOG.info("get_gauge: END")
        return gauge  # no error

    def create_gauge(
        self,
        verification: Verification,
        title: str,
        label: str,
        limit: int = 0,
        index: int = 0,
        length: int = 1,
        constant: int = 0,
        status: int = 11,
        lockID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "create_gauge: verification={} title={} label={} limit={} index={} length={} constant={}".format(
                    verification, title, label, limit, index, length, constant
                )
            )
            # check for division of 0
            if length == 0:
                raise ZeroDivisionError(
                    "Length cannot be 0, this will cause a division of 0 error!"
                )

            # update percent
            percent = int(limit * index / length) + constant

            # define gauge ID
            gaugeID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    if lockID is not None:
                        sql.execute(
                            self.insert_gauge_with_lock,
                            (
                                title,
                                label,
                                limit,
                                index,
                                length,
                                constant,
                                percent,
                                status,
                                verification.get_verification(),
                                lockID,
                            ),
                        )
                    else:
                        sql.execute(
                            self.insert_gauge,
                            (
                                title,
                                label,
                                limit,
                                index,
                                length,
                                constant,
                                percent,
                                status,
                                verification.get_verification(),
                            ),
                        )
                    if len(sql.table) > 0:
                        gaugeID = int(sql.table[0]["ID"])

                        # log gauge
                        self.log_gauge(
                            gaugeID,
                            "Created",
                            "Gauge Created",
                            verification,
                            41,
                        )
                    else:
                        raise Exception("No results found with the insert_gauge query!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_gauge: error={}".format(e))
            return -1

        self.LOG.info("create_gauge: gaugeID={0}".format(gaugeID))
        self.LOG.info("create_gauge: END")
        return gaugeID

    # updates a gauge object and/or outputs text to a log
    # input: Text, Index, Length, Limit, Constant
    # output: 0 on success, -1 on failure
    def update_gauge(
        self,
        gaugeID: int,
        logger: object,
        title: str | None = None,
        index: int | None = None,
        length: int | None = None,
        limit: int | None = None,
        constant: int | None = None,
        label: str | None = None,
        status: int | None = None,
        verification: Verification = None,
    ) -> int:
        """
        Updates a gaugeID object and/or outputs title to a log
        Args:
            title: Output title on update of gaugeID
            index: The ith item of the length
            length: The length of items to the update the gaugeID in
            constant: A constant to be applied if one wants to have a specific range
            limit: The max range the gaugeID will go to
            label: The label that indicates current task being run
        Returns:
            int
        """
        try:
            # check if we have a logger, if not then use constant pre-made
            if logger is None:
                logger = self.LOG

            # check for division of 0
            if length == 0:
                raise ZeroDivisionError(
                    "Length cannot be 0, this will cause a division of 0 error!"
                )

            logger.info(
                "update_gauge: gaugeID={} title={} index={} length={} limit={} constant={} label={} verification={} ".format(
                    gaugeID, title, index, length, limit, constant, label, verification
                )
            )

            # define percent
            percent = 0

            # define lockID
            lockID = None

            # only update gauge if gaugeID is not None and employee_check passes
            if gaugeID is not None:
                # get self
                result = self.get_gauge(gaugeID)
                if len(result) < 1:
                    raise Exception(
                        "No gauge was found with given gaugeID {}!".format(gaugeID)
                    )
                gauge = result[0]

                # update terms if needed
                if index is None:
                    index = gauge["Index"]
                    # force a None to be set to a valid value
                    if index is None:
                        index = 0
                if length is None:
                    length = gauge["Length"]
                    # force a None to be set to a valid value
                    if length is None:
                        length = 1
                if limit is None:
                    limit = gauge["Limit"]
                    # force a None to be set to a valid value
                    if limit is None:
                        limit = 0
                if constant is None:
                    constant = gauge["Constant"]
                    # force a None to be set to a valid value
                    if constant is None:
                        constant = 0
                if title is None:
                    title = gauge["Title"]
                if label is None:
                    label = gauge["Label"]
                if status is None:
                    status = gauge["Status"]
                if gauge["LockID"] is not None:
                    lockID = gauge["LockID"]

                # get verificationID
                if verification is None and gauge["VerificationID"] is not None:
                    verification = Verification()
                    verification.set_verification(gauge["VerificationID"])

                # update percent
                percent = (limit * index / length) + constant

                # update each given item that isnt None
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    with SQL_Pull()(self.sql_config)() as sql:
                        result, _ = sql.execute(
                            self.update_gauge_values,
                            (
                                title,
                                label,
                                limit,
                                index,
                                length,
                                constant,
                                percent,
                                status,
                                gaugeID,
                            ),
                        )
                        if len(result) == 0:
                            raise Exception(
                                "No results found with the update_gauge_values query!"
                            )

                    # update gauge and lock if there is a lock
                    if percent >= 100:
                        # log gauge
                        self.log_gauge(
                            gaugeID, "Completed", "Gauge Complete", verification, 40
                        )

                        # disable lock if we have a lock
                        if lockID is not None:
                            self.lock.disable_lock(verification, lockID)
                    else:
                        # log gauge
                        self.log_gauge(
                            gaugeID, "Updated", "Gauge Changed", verification, 39
                        )
                else:
                    raise Exception(
                        "Invalid verification provided on update_gauge call!"
                    )

            # no gauge provided
            else:
                # update terms to default values if needed
                if limit is None:
                    limit = 0
                if index is None:
                    index = 0
                if length is None:
                    length = 1
                if constant is None:
                    constant = 0

            # update percent
            percent = int(limit * index / length) + constant

            # log percentage
            logger.info("{0} - {1}: {2}%".format(title, label, percent))

        except Exception as e:
            logger.info("update_gauge: {}".format(e))
            return -1

        logger.info("update_gauge: END")
        return 0

    def log_gauge(
        self,
        gaugeID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_gauge: gaugeID={} change="{}" description="{}" verification={} logtype={}'.format(
                    gaugeID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_gauge_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                            gaugeID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_gauge: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_gauge_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_gauge: error={}".format(e))

        self.LOG.info("log_gauge: END")
        return -1


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
