#!/usr/bin/env python3.7
import time
import math

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .fixit_config import FixitConfig
from .gauge_pull import Gauge
from .location_pull import Location
from .verification_pull import Verification
from .case_pull import Case
from .record_pull import Record
from .threading_return import ThreadWithReturnValue
from .constants import Locations, LogTypes


class Fixit(FixitConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        FixitConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # initialize location object
        self.loc = Location()

        # get locations and status
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]
            result, _ = sql.execute(self.get_fixit_reasons)
            for res in result:
                self.reasons[res["ID"]] = res["ReasonType"]
            result, _ = sql.execute(self.get_log_types)
            for log_type in result:
                self.log_types[log_type["ID"]] = log_type["LogType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # logs an aligner change given a description, used in other functions if a
    # value of an aligner is updated or changed from its initial creation form
    # input: FixitID, Change, Description, Verification
    # output: 0 for success, -1 on error
    def log_fixit(
        self,
        fixitID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_fixit: fixitID={} change="{}" description="{}" verification={} logtype={}'.format(
                    fixitID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_fixit_log,
                        (
                            fixitID,
                            logtype,
                            fixitID,
                            change,
                            description,
                            verification.get_verification(),
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                            fixitID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_fixit: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_fixit_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_fixit: error={}".format(e))

        self.LOG.info("log_fixit: END")
        return -1

    # updates an fixit's status
    # input: Verification, AlignerID, FixitID, index of predefined statuses
    # output: 0 for success, -1 for error
    def update_status(
        self, verification: Verification, fixitID: int, status: int = 5
    ) -> int:
        try:
            self.LOG.info(
                "update_status: verification={} fixitID={} status={}".format(
                    verification, fixitID, status
                )
            )

            # get label of status id given
            label = self.statuses[status]
            if len(label) == 0:
                raise Exception(
                    "Unable to find a matching status with given status id {0}!".format(
                        status
                    )
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_fixit_status, (status, fixitID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status: END")
                        self.log_fixit(
                            fixitID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            11,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_aligner_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status: error={}".format(e))

        self.LOG.info("update_status: END")
        return -1

    # checks if a fixitID is complete or not
    # input: fixitID
    # output: 0 for success, -1 for error
    def fixit_check(self, fixitID: int) -> int:
        try:
            self.LOG.info("fixit_check: fixitID={}".format(fixitID))

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:
                fixits, _ = sql.execute(self.check_fixit, (fixitID))
                if len(fixits) > 0:
                    if fixits[0]["Checkout"] is not None:
                        self.LOG.info("fixit_check: 0")
                        return 0
                else:
                    raise Exception(
                        "No fixitID found for {0} could be found!".format(fixitID)
                    )

        except Exception as e:
            self.LOG.error("fixit_check: error={}".format(e))

        self.LOG.info("fixit_check: -1")
        return -1

    # checks if an alignerID's fixitID is complete or not
    # input: alignerID
    # output: 0 for success, -1 for error
    def aligner_check(self, alignerID: int) -> int:
        try:
            self.LOG.info("aligner_check: alignerID={}".format(alignerID))

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                aligners, _ = sql.execute(self.check_aligner, (alignerID))
                if len(aligners) > 0:
                    # the fixitID is the last column
                    fixitID = aligners[0]["FixitCID"]
                    if fixitID is not None:
                        # check if fixitID is complete
                        status = self.fixit_check(fixitID)
                        self.LOG.info("aligner_check: {0}".format(status))
                        return status
                    else:
                        self.LOG.info("aligner_check: 0")
                        return 0  # return success if no fixitID for aligner
                else:
                    raise Exception(
                        "No aligners could be found for alignerID {0}!".format(
                            alignerID
                        )
                    )

        except Exception as e:
            self.LOG.error("aligner_check: error={}".format(e))

        self.LOG.info("aligner_check: -1")
        return -1

    # creates a fixit with the given information
    # input: Verification, CaseNumber, Zone, Reason, Who, Notes
    # output: FixitID for success, "" for error
    def create_fixit(
        self,
        owner_verification: Verification,
        verification: Verification,
        caseNumber: str,
        zone: int,
        reason: int,
        who_verification: Verification,
        notes: str = "",
        alignerIDs: list = [],
        locationID: int = Locations.CAD_IMPORT.value,
        update_fixit: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                "create_fixit: owner_verification={} verification={} caseNumber={} zone={} reason={} who_verification={} notes={}".format(
                    owner_verification,
                    verification,
                    caseNumber,
                    zone,
                    reason,
                    who_verification,
                    notes,
                )
            )

            fixitID = -1

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
                and isinstance(who_verification, Verification)
                and who_verification.get_verification() != -1
            ):
                # get caseID from casenumber
                with Case() as cas:
                    result = cas.get_info_by_case(caseNumber)
                    if len(result) != 0:
                        caseID = result[0]["CaseID"]
                    else:
                        raise Exception("Invalid case number provided!")

                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_fixit,
                        (
                            caseID,
                            zone,
                            reason,
                            who_verification.get_verification(),
                            notes,
                            verification.get_verification(),
                            locationID,
                        ),
                    )
                    if len(sql.table) != 0:
                        # define fixit_info
                        fixit_info = sql.table[0]

                        # get fixitID
                        fixitID = fixit_info["FixitID"]

                        # Disable any records associated with the Case
                        with Record() as rec:
                            rec.delete_laser_records_by_caseNumber(
                                caseNumber, verification
                            )
                            rec.delete_shipping_records_by_caseNumber(
                                caseNumber, verification
                            )

                        # remake aligners that are given
                        with Aligner(self.sql_config) as alg:
                            # match logger
                            alg.LOG = self.LOG

                            # disable logging
                            # self.LOG.disabled = True

                            # create each aligner
                            threads = []
                            for alignerID in alignerIDs:
                                thread = ThreadWithReturnValue(
                                    target=Aligner.remake_aligner,
                                    args=(
                                        alg,
                                        alignerID,
                                        owner_verification,
                                        verification,
                                        fixitID,
                                        None,
                                        None,
                                        None,
                                        None,
                                        None,
                                        None,
                                        (
                                            update_fixit if len(threads) == 0 else False
                                        ),  # only update fixit once when threads is 0
                                        fixit_info,
                                        locationID,
                                    ),
                                )
                                thread.handled = False
                                thread.alignerID = alignerID
                                threads.append(thread)
                                thread.start()

                            # rejoin threads
                            timeout = time.time() + 200  # timeout after 200 seconds
                            while len(threads) > 0:
                                threads = [t for t in threads if t.handled is False]

                                # find a thread thats done
                                for thread in threads:
                                    if thread.done() is False:
                                        continue

                                    # default value
                                    aligner = {}

                                    # timeout checker
                                    if time.time() > timeout:
                                        raise Exception("Threading timeout reached!")

                                    aligner = thread.join()
                                    thread.handled = True
                                    if len(aligner) == 0:
                                        raise Exception(
                                            "Aligner remake failed for aligner {}!".format(
                                                thread.alignerID
                                            )
                                        )

                            # enable logging
                            # self.LOG.disabled = False

                    else:
                        raise Exception("No results found with the insert_fixit query!")

                    # log creation
                    self.log_fixit(
                        fixitID,
                        "NEW",
                        "Fixit Created",
                        verification,
                        LogTypes.FIXIT_CREATED.value,
                    )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_fixit: error={}".format(e))
            self.LOG.info("create_fixit: END")
            return -1  # other error

        self.LOG.info("create_fixit: fixitID={}".format(fixitID))
        self.LOG.info("create_fixit: END")
        return fixitID  # no error

    # removes a fixit with verification
    # input: Verification, FixitID
    # output: FixitID for success, "" for error
    def checkout_fixit(self, verification: Verification, fixitID: int) -> int:
        try:
            self.LOG.info(
                "checkout_fixit: verification={}, fixitID={}".format(
                    verification, fixitID
                )
            )

            # run employee checkd(verification)
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.remove_fixit, (verification.get_verification(), fixitID)
                    )
                    if len(sql.table) != 0:
                        # log checkout
                        self.log_fixit(
                            fixitID,
                            "CHECKOUT",
                            "Fixit Marked Off",
                            verification,
                            13,
                        )

                        self.LOG.info("checkout_fixit: END")
                        return 0
                    else:
                        raise Exception("No results found with the remove_fixit query!")
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("checkout_fixit: error={}".format(e))

        self.LOG.info("checkout_fixit: END")
        return -1  # other error

    # removes a fixit with verification
    # input: Verification, FixitID
    # output: FixitID for success, "" for error
    def cancel_fixit(self, verification: Verification, fixitID: int) -> str:
        try:
            self.LOG.info(
                "cancel_fixit: verification={}, fixitID={}".format(
                    verification, fixitID
                )
            )

            # run employee checkd(verification)
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.deactivate_fixit.format(
                            verification.get_verification(), fixitID
                        )
                    )
                    if len(sql.table) != 0:
                        # confirm fixitID
                        fixitID = sql.table[0]["FixitID"]

                        #  undo aligners with this fixitID
                        with Aligner() as alg:
                            # cancel created ones
                            created = alg.get_aligners_by_fixitCID(fixitID)
                            for aligner in created:
                                alignerID = aligner["AlignerID"]
                                alg.update_status(verification, alignerID, 3)
                            # enable existing ones
                            original = alg.get_aligners_by_fixitID(fixitID, [3])
                            for aligner in original:
                                alignerID = aligner["AlignerID"]
                                alg.update_status(verification, alignerID, 0)
                    else:
                        raise Exception(
                            "No results found with the deactivate_fixit query!"
                        )

                    # log cancel
                    self.log_fixit(
                        fixitID, "CANCEL", "Fixit Canceled", verification, 14
                    )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("cancel_fixit: error={}".format(e))
            self.LOG.info("cancel_fixit: END")
            return -1  # other error

        self.LOG.info("cancel_fixit: fixitID={}".format(fixitID))
        self.LOG.info("cancel_fixit: END")
        return 0  # no error

    # retrieves a case by fixitID
    # input: FixitID
    # output: CaseNumber, CaseID for success, "" for error
    def get_case_by_fixitid(self, fixitID: int) -> list:
        try:
            self.LOG.info("get_case_by_fixitid: fixitID={}".format(fixitID))

            case = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above
                sql.execute(self.get_case_by_FixitID, (fixitID))
                if len(sql.table) != 0:
                    case = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_by_FixitID query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_by_fixitid: error={}".format(e))
            self.LOG.info("get_case_by_fixitid: END")
            return []  # other error

        self.LOG.info("get_case_by_fixitid: fixits={}".format(str(case)))
        self.LOG.info("get_case_by_fixitid: END")
        return case  # no error

    # retrieves an fixitID by fixitID
    # input: CaseID
    # output: FixitID for success, "" for error
    def get_fixits_by_ids(self, fixitIDs: list) -> list:
        try:
            self.LOG.info("get_fixits_by_ids: fixitIDs={}".format(fixitIDs))

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above
                sql.execute(self.get_fixit_by_IDs, (",".join(map(str, fixitIDs))))
                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception("No results found with the get_fixit_by_ID query!")

        except Exception as e:
            self.LOG.error("get_fixits_by_ids: error={}".format(e))
            self.LOG.info("get_fixits_by_ids: END")
            return []  # other error

        self.LOG.info("get_fixits_by_ids: fixits={}".format(fixits))
        self.LOG.info("get_fixits_by_ids: END")
        return fixits  # no error

    # retrieves an fixitID by fixitID
    # input: CaseID
    # output: FixitID for success, "" for error
    def get_fixit_by_id(self, fixitID: int) -> list:
        try:
            self.LOG.info("get_fixit_by_id: fixitID={}".format(fixitID))

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above
                sql.execute(self.get_fixit_by_ID, (fixitID))
                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception("No results found with the get_fixit_by_ID query!")

        except Exception as e:
            self.LOG.error("get_fixits_by_id: error={}".format(e))
            self.LOG.info("get_fixits_by_id: END")
            return []  # other error

        self.LOG.info("get_fixits_by_id: fixits={}".format(fixits))
        self.LOG.info("get_fixits_by_id: END")
        return fixits  # no error

    # retrieves a list of fixits
    # input: N/A
    # output: Fixit list for success, [] for error
    def get_active_fixits(self) -> list:
        try:
            self.LOG.info("get_active_fixits: N/A")

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above
                sql.execute(self.get_fixits_active)
                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_active query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_fixits: error={}".format(e))
            self.LOG.info("get_active_fixits: END")
            return []  # other error

        self.LOG.info("get_active_fixits: fixits={}".format(str(fixits)))
        self.LOG.info("get_active_fixits: END")
        return fixits  # no error

    # retrieves a list of fixits within a date range
    # input: startdate, enddate
    # output: Fixit list for success, [] for error
    def get_fixits_by_dates(
        self,
        startdate: str,
        enddate: str,
        rows: int,
        offset: int,
        statuses: list = [2, 4],
    ):
        try:
            self.LOG.info(
                "get_fixits_by_dates: startdate={} enddate={} rows={} offset={} statuses={}".format(
                    startdate, enddate, rows, offset, statuses
                )
            )

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_fixits_by_Dates,
                    (",".join(map(str, statuses)), startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_by_Dates query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixits_by_dates: error={}".format(e))
            self.LOG.info("get_fixits_by_dates: END")
            return []  # other error

        self.LOG.info("get_fixits_by_dates: fixits={}".format(str(fixits)))
        self.LOG.info("get_fixits_by_dates: END")
        return fixits  # no error

    # retrieves a list of fixits by case
    # input: CaseNumber
    # output: FixitID for success, "" for error
    def get_fixits_by_case(self, caseNumber: str, statuses: list = [2, 4]) -> list:
        try:
            self.LOG.info(
                "get_fixits_by_case: caseNumber={} statuses={}".format(
                    caseNumber, statuses
                )
            )

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_fixits_by_Case, (",".join(map(str, statuses)), caseNumber)
                )
                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_by_Case query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixits_by_case: error={}".format(e))
            self.LOG.info("get_fixits_by_case: END")
            return []  # other error

        self.LOG.info("get_fixits_by_case: fixits={}".format(str(fixits)))
        self.LOG.info("get_fixits_by_case: END")
        return fixits  # no error

    # retrieves an fixitID by reason type
    # input: Error
    # output: FixitID for success, "" for error
    def get_fixits_by_reason(
        self, reason: int, startdate: str, enddate: str, statuses: list = [2, 4]
    ) -> list:
        try:
            self.LOG.info(
                "get_fixits_by_reason: reason={} startdate={} enddate={} statuses={}".format(
                    reason, startdate, enddate, statuses
                )
            )

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_fixits_by_Reason,
                    (",".join(map(str, statuses)), reason, startdate, enddate),
                )

                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_by_Reason query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixits_by_reason: error={}".format(e))
            self.LOG.info("get_fixits_by_reason: END")
            return []  # other error

        self.LOG.info("get_fixits_by_reason: fixits={}".format(str(fixits)))
        self.LOG.info("get_fixits_by_reason: END")
        return fixits  # no error

    # retrieves an fixit by location
    # input: Error, startdate, enddate
    # output: FixitID for success, "" for error
    def get_fixits_by_location(
        self, location: int, startdate: str, enddate: str, statuses: list = [2, 4]
    ) -> list:
        try:
            self.LOG.info(
                "get_fixits_by_location: location={} startdate={} enddate={} statuses={}".format(
                    location, startdate, enddate, statuses
                )
            )

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_fixits_by_Location,
                    (",".join(map(str, statuses)), location, startdate, enddate),
                )

                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_by_Location query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixits_by_location: error={}".format(e))
            self.LOG.info("get_fixits_by_location: END")
            return []  # other error

        self.LOG.info("get_fixits_by_location: fixits={}".format(str(fixits)))
        self.LOG.info("get_fixits_by_location: END")
        return fixits  # no error

    # retrieves an fixitID by who
    # input: Error, startdate, enddate
    # output: FixitID for success, "" for error
    def get_fixits_by_who(
        self, verificaitonID: int, startdate: str, enddate: str, statuses: list = [2, 4]
    ) -> list:
        try:
            self.LOG.info(
                "get_fixits_by_who: who={} startdate={} enddate={} statuses={}".format(
                    verificaitonID, startdate, enddate, statuses
                )
            )

            fixits = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_fixits_by_Who,
                    (",".join(map(str, statuses)), verificaitonID, startdate, enddate),
                )
                if len(sql.table) != 0:
                    fixits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixits_by_Who query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixits_by_who: error={}".format(e))
            self.LOG.info("get_fixits_by_who: END")
            return []  # other error

        self.LOG.info("get_fixits_by_who: fixits={}".format(str(fixits)))
        self.LOG.info("get_fixits_by_who: END")
        return fixits  # no error

    # given a string reason, gets its matching id if found
    def get_id_from_reason(self, reason: str) -> int:
        try:
            self.LOG.info("get_id_from_reason: reason={0}".format(reason))

            Id = -1

            for key, value in self.reasons.items():
                if reason == value:
                    Id = key
                    break

        except Exception as e:
            self.LOG.error("get_id_from_reason: error={}".format(e))
            self.LOG.info("get_id_from_reason: END")
            return -1  # other error

        self.LOG.info("get_id_from_reason: Id={}".format(Id))
        self.LOG.info("get_id_from_reason: END")
        return Id  # no error

    # gets case employee links
    # input: N/A
    # output: CaseEmployeeLinks on success, [] on error
    def get_fixit_employee_links(self, statuses: list = [11, 12]) -> list:
        try:
            self.LOG.info(f"get_fixit_employee_links: statuses={statuses}")

            fixit_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:

                sql.execute(
                    self.get_fixit_employee_links_by_status,
                    (",".join(map(str, statuses))),
                )
                if len(sql.table) != 0:
                    fixit_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixit_employee_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixit_employee_links: error={}".format(e))
            self.LOG.info("get_fixit_employee_links: END")
            return []  # other error

        self.LOG.info(
            "get_fixit_employee_links: fixit_employee_links={}".format(
                fixit_employee_links
            )
        )
        self.LOG.info("get_fixit_employee_links: END")
        return fixit_employee_links  # no error

    # gets case employee link logs by case Number
    # input: caseNumber
    # output: CaseEmployeeLinkLogs on success, [] on error
    def get_fixit_employee_links_logs_by_fixit(self, caseNumber: int) -> list:
        try:
            self.LOG.info(
                f"get_fixit_employee_links_logs_by_fixit: caseNumber={caseNumber}"
            )

            fixit_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_fixit_employee_link_logs_by_fixit, (caseNumber))
                if len(sql.table) != 0:
                    fixit_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixit_employee_link_logs_by_fixit query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixit_employee_links_logs_by_fixit: error={}".format(e))
            self.LOG.info("get_fixit_employee_links_logs_by_fixit: END")
            return []  # other error

        self.LOG.info(
            "get_fixit_employee_links_logs_by_fixit: fixit_employee_links={}".format(
                fixit_employee_links
            )
        )
        self.LOG.info("get_fixit_employee_links_logs_by_fixit: END")
        return fixit_employee_links  # no error

    # gets last 48 hours of fixit employee link logs by EmployeeID
    # input: employeeID
    # output: FixitEmployeeLinkLogs on success, [] on error
    def get_fixit_employee_links_logs_by_employee(self, employeeID: int) -> list:
        try:
            self.LOG.info(
                f"get_fixit_employee_links_logs_by_employee: employeeID={employeeID}"
            )

            fixit_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_fixit_employee_link_logs_by_employeeID, (employeeID)
                )
                if len(sql.table) != 0:
                    fixit_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixit_employee_link_logs_by_employeeID query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_fixit_employee_links_logs_by_employee: error={}".format(e)
            )
            self.LOG.info("get_fixit_employee_links_logs_by_employee: END")
            return []  # other error

        self.LOG.info(
            "get_fixit_employee_links_logs_by_employee: fixit_employee_links={}".format(
                fixit_employee_links
            )
        )
        self.LOG.info("get_fixit_employee_links_logs_by_employee: END")
        return fixit_employee_links  # no error

    # Creates a link between the given fixitID and employeeID if no active link already exists
    # input: employeeID, fixitID
    # output: CaseEmployeeLinkID on success, -1 on error
    def create_fixit_employee_link(
        self, verification: Verification, fixitID: int
    ) -> int:
        try:
            self.LOG.info(
                f"create_fixit_employee_link: verification={verification} fixitID={fixitID}"
            )

            employee_link_ID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # If an active case employee link already exists, raise exception
                    previous_cases = self.get_fixit_employee_links_by_fixit(
                        fixitID, [11]
                    )
                    if len(previous_cases) != 0:
                        raise Exception(
                            f"An Employee is already linked to case {fixitID}!"
                        )

                    sql.execute(
                        self.insert_fixit_employee_link,
                        (fixitID, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        employee_link_ID = int(sql.table[0]["ID"])
                        # Generate employee case link log using caseEmployeeLinkID created
                        self.log_fixit_employee_link(employee_link_ID, verification, 50)

                    else:
                        raise Exception(
                            "No results found with the create_case_employee_links query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("create_fixit_employee_link: error={}".format(e))
            self.LOG.info("create_fixit_employee_link: END")
            return -1  # other error

        self.LOG.info(
            "create_fixit_employee_link: employee_link_ID={}".format(employee_link_ID)
        )
        self.LOG.info("create_fixit_employee_link: END")
        return employee_link_ID  # no error

    # Gets case employee links associated with the case given
    # Input: Case
    # Output: CaseEmployeeLinks
    def get_fixit_employee_links_by_fixit(
        self, fixitID: int, statuses: list = [11, 12]
    ) -> list:
        try:
            self.LOG.info(
                f"get_fixit_employee_links_by_fixit: fixitID={fixitID} statuses={statuses}"
            )

            fixit_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:

                sql.execute(
                    self.get_fixit_employee_links_by_fixit_and_status,
                    (",".join(map(str, statuses)), fixitID),
                )
                if len(sql.table) != 0:
                    fixit_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_fixit_employee_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixit_employee_links_by_fixit: error={}".format(e))
            self.LOG.info("get_fixit_employee_links_by_fixit: END")
            return []  # other error

        self.LOG.info(
            "get_fixit_employee_links_by_fixit: fixit_employee_links={}".format(
                fixit_employee_links
            )
        )
        self.LOG.info("get_fixit_employee_links_by_fixit: END")
        return fixit_employee_links  # no error

    # Gets fixit employee links associated with the fixits given
    # Input: fixits
    # Output: CaseEmployeeLinks
    def get_fixit_employee_links_by_fixits(
        self, fixits: list, statuses: list = [11]
    ) -> list:
        try:
            self.LOG.info(
                f"get_fixit_employee_links_by_fixits: fixits={fixits} statuses={statuses}"
            )

            fixit_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:

                # Generate the number of sql executions to run. When list is larger than 300 sql will send back an error
                num_sql_executions = math.ceil(len(fixits) / 300)

                for x in range(num_sql_executions):
                    # Execute sql with map converting fixits[0:299] to a str, remove those fixits from the initial list
                    sql.execute(
                        self.get_fixit_employee_links_by_fixits_and_status,
                        (
                            ",".join(map(str, statuses)),
                            ",".join(map(str, fixits[0:299])),
                        ),
                    )
                    del fixits[0:299]

                    if len(sql.table) != 0:
                        fixit_employee_links = [*fixit_employee_links, *sql.table]

                if len(fixit_employee_links) == 0:
                    raise Exception(
                        "No results found with the get_fixit_employee_links_by_fixitss_and_status query!"
                    )

        except Exception as e:
            self.LOG.error("get_fixit_employee_links_by_fixits: error={}".format(e))
            self.LOG.info("get_fixit_employee_links_by_fixits: END")
            return []  # other error

        self.LOG.info(
            "get_fixit_employee_links_by_fixits: fixit_employee_links={}".format(
                fixit_employee_links
            )
        )
        self.LOG.info("get_fixit_employee_links_by_fixits: END")
        return fixit_employee_links  # no error

    # change status of fixit_employee_link
    # input: verification, fixitemployeelinkID, status
    # output: fixit_employee_link
    def update_fixit_employee_link(
        self, verification: Verification, linkID: int
    ) -> int:
        try:
            self.LOG.info(
                f"update_fixit_employee_link: verification={verification} linkID={linkID}"
            )

            fixit_employee_link = -1
            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # Update fixit_employee_link
                with SQL_Pull()(self.sql_config)() as sql:
                    result, _ = sql.execute(self.change_fixit_employee_link, (linkID))
                    # Log the change to the fixit_employee_link
                    if len(result) != 0:
                        fixit_employee_link = result[0]["ID"]
                        self.log_fixit_employee_link(
                            fixit_employee_link,
                            verification,
                            52,
                        )
                    else:
                        raise Exception(
                            "No results found with the update_fixit_employee_link query"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_fixit_employee_link: error={}".format(e))
            self.LOG.info("update_fixit_employee_link: END")
            return -1  # other error

        self.LOG.info("update_fixit_employee_link: case_flag_link={}".format(result))
        self.LOG.info("update_fixit_employee_link: END")
        return fixit_employee_link

    # logs a change to a fixit_employee_link
    def log_fixit_employee_link(
        self,
        fixit_employee_link_ID: int,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                "log_fixit_employee_link: fixit_employee_link_ID={} verification={} logtype={}".format(
                    fixit_employee_link_ID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 50:
                        change = "Checked In"
                        description = "Fixit Link Checked In"
                    if logtype == 52:
                        change = "Unassigned"
                        description = "Fixit Link Unassigned"

                    # Execute sql query with above variables
                    sql.execute(
                        self.insert_fixit_employee_link_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            fixit_employee_link_ID,
                            fixit_employee_link_ID,
                            fixit_employee_link_ID,
                            fixit_employee_link_ID,
                            fixit_employee_link_ID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_fixit_employee_link: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_fixit_employee_link_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_fixit_employee_link: error={}".format(e))

        self.LOG.info("log_fixit_employee_link: END")
        return -1

    # updates the location assigned to a given case
    # input: Verification, CaseID, Location
    # output: Location on success, -1 on error
    def update_location(
        self, verification: Verification, fixitID: int, location: int
    ) -> int:
        try:
            self.LOG.info(
                "update_location: verification={} fixitID={} location={}".format(
                    verification, fixitID, location
                )
            )

            # update location
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_fixit_location, (location, fixitID))

                    if len(sql.table) != 0:  # didn't receive a response
                        self.LOG.info("update_location: END")
                        self.log_fixit(
                            fixitID,
                            "Location Updated!",
                            "Location Updated to '{}'".format(location),
                            verification,
                            LogTypes.FIXIT_LOCATION_UPDATED.value,
                        )
                        return location
                    else:
                        raise Exception(
                            "No results found with the update_case_location query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_location: error={}".format(e))

        self.LOG.info("update_location: END")
        return -1


# import on the bottom for circular import
from .aligner_pull import Aligner


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
